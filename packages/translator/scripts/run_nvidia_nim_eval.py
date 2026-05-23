#!/usr/bin/env python3
"""
Evaluate the precompiled bootstrap_fast DSPy program with:
  - NVIDIA hosted model: nvidia_nim/minimaxai/minimax-m2.7
  - 50 evaluation samples (separate from first 50 training examples)
  - Post-processing enabled

Compares against:
  - DeepSeek-V4-Flash (existing baseline)
  - Meta-Llama-3.1-8B-Instruct-Turbo
  - Meta-Llama-3.3-70B-Instruct-Turbo

Usage:
    python run_nvidia_nim_eval.py
"""

import csv
import json
import os
import random
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]  # packages/translator/scripts/x.py → project root
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "translator" / "src"))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

import dspy

RESULTS_DIR = PROJECT_ROOT / "data" / "eval_results" / "optimizer_comparison"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

COMPILED_DIR = str(RESULTS_DIR / "compiled_bootstrap_fast_program")


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    return text


def _strip_punct(s: str) -> str:
    s = re.sub(r'[.,!?;:()"\'\[\]{}]', "", s)
    return re.sub(r"\s+", " ", s).strip()


def normalized_match_en_to_mir(example, prediction, trace=None) -> float:
    gold = _normalize(getattr(example, "mirad_text", ""))
    pred = _normalize(getattr(prediction, "mirad_text", ""))
    if gold == pred:
        return 1.0
    return 1.0 if _strip_punct(gold) == _strip_punct(pred) else 0.0


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_full_dataset(csv_path: str | None = None):
    """Load all examples from the sentence pairs CSV."""
    if csv_path is None:
        csv_path = str(PROJECT_ROOT / "data" / "phrases" / "english-mirad-sentence-pairs.csv")

    examples = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            en = row.get("English", row.get("english", "")).strip()
            mi = row.get("Mirad", row.get("mirad", "")).strip()
            if en and mi:
                examples.append(
                    dspy.Example(
                        english_text=en,
                        mirad_text=mi,
                    ).with_inputs("english_text")
                )

    rng = random.Random(42)
    rng.shuffle(examples)
    return examples


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate_compiled(compiled_program, lm_config, eval_examples, label):
    print(f"\n{'=' * 70}")
    print(f"Evaluating: {label}")
    print(f"Model:     {lm_config['model']}")
    print(f"{'=' * 70}")

    api_key = os.environ.get(lm_config["api_key_env"], "")
    api_base = os.environ.get(
        lm_config.get("api_base_env", ""),
        lm_config.get("default_api_base", "")
    )

    lm = dspy.LM(
        model=lm_config["model"],
        api_key=api_key,
        api_base=api_base,
        num_retries=5,
        cache=True,
    )
    dspy.settings.configure(lm=lm)

    eval_start = time.time()
    per_example = []
    hits_norm = 0
    hits_exact = 0

    for i, ex in enumerate(eval_examples):
        pred = compiled_program(english_text=ex.english_text)
        raw_mirad = pred.mirad_text
        gold = ex.mirad_text

        norm_score = normalized_match_en_to_mir(ex, pred)
        exact = 1.0 if _normalize(gold) == _normalize(raw_mirad) else 0.0

        hits_norm += norm_score
        hits_exact += exact

        per_example.append({
            "english_text": ex.english_text,
            "gold_mirad": gold,
            "predicted_mirad": raw_mirad,
            "normalized_match": norm_score,
            "exact_match": exact,
        })

        if (i + 1) % 10 == 0:
            elapsed = time.time() - eval_start
            rate = hits_norm / (i + 1) * 100
            print(f"  [{i+1}/{len(eval_examples)}] {elapsed:.1f}s elapsed, hit rate: {rate:.1f}%")

    eval_time = time.time() - eval_start
    total = len(eval_examples)
    norm_pct = hits_norm / total * 100
    exact_pct = hits_exact / total * 100

    print(f"\n  Results:")
    print(f"    Normalized match: {norm_pct:.1f}% ({int(hits_norm)}/{total})")
    print(f"    Exact match:       {exact_pct:.1f}% ({int(hits_exact)}/{total})")
    print(f"    Eval time:         {eval_time:.1f}s ({eval_time/60:.1f} min)")

    return {
        "model": lm_config["model"],
        "label": label,
        "per_example": per_example,
        "eval_time_s": round(eval_time, 2),
        "normalized_score": norm_pct,
        "exact_score": exact_pct,
        "normalized_hits": int(hits_norm),
        "exact_hits": int(hits_exact),
        "total": total,
    }


def main():
    print("=" * 70)
    print("NVIDIA NIM EVAL: nvidia_nim/minimaxai/minimax-m2.7")
    print("50-sample evaluation with precompiled bootstrap_fast program")
    print("=" * 70)

    # Load compiled program
    print(f"\n[LOAD] Loading compiled program from {COMPILED_DIR}/")
    compiled = dspy.load(COMPILED_DIR, allow_pickle=True)
    print("[LOAD] Successfully loaded compiled program")

    # Load dataset
    all_examples = load_full_dataset()
    train_size = 50
    eval_size = 50
    eval_examples = all_examples[train_size:train_size + eval_size]

    print(f"\n[DATA] Total examples: {len(all_examples)}")
    print(f"[DATA] Training: indices 0-{train_size-1} (excluded)")
    print(f"[DATA] Eval:     indices {train_size}-{train_size + eval_size - 1} ({eval_size} samples)")

    all_results = {}

    # LM configs
    lm_configs = {
        "nvidia_nim/minimaxai/minimax-m2.7": {
            "model": "nvidia_nim/minimaxai/minimax-m2.7",
            "api_key_env": "NVIDIA_API_KEY",
            "api_base_env": "NVIDIA_BASE_URL",
            "default_api_base": "https://integrate.api.nvidia.com/v1",
        },
        "deepseek-ai/DeepSeek-V4-Flash": {
            "model": "deepseek-ai/DeepSeek-V4-Flash",
            "api_key_env": "DEEPINFRA_API_KEY",
            "api_base_env": "DEEPINFRA_BASE_URL",
            "default_api_base": "https://api.deepinfra.com/v1/openai",
        },
        "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo": {
            "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            "api_key_env": "DEEPINFRA_API_KEY",
            "api_base_env": "DEEPINFRA_BASE_URL",
            "default_api_base": "https://api.deepinfra.com/v1/openai",
        },
        "meta-llama/Llama-3.3-70B-Instruct-Turbo": {
            "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
            "api_key_env": "DEEPINFRA_API_KEY",
            "api_base_env": "DEEPINFRA_BASE_URL",
            "default_api_base": "https://api.deepinfra.com/v1/openai",
        },
    }

    for model_name, lm_cfg in lm_configs.items():
        cache_path = RESULTS_DIR / f"50s_eval_{model_name.replace('/', '_')}.json"

        if cache_path.exists():
            print(f"\n[CACHE] Loading cached {model_name} from {cache_path.name}")
            with open(cache_path) as f:
                cached = json.load(f)
            all_results[model_name] = cached
            print(f"  normalized={cached['normalized_score']:.1f}% exact={cached['exact_score']:.1f}%")
        else:
            result = evaluate_compiled(
                compiled,
                lm_cfg,
                eval_examples,
                model_name,
            )
            all_results[model_name] = result
            with open(cache_path, "w") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"[CACHE] Saved to {cache_path.name}")

    # Save full comparison
    output_path = RESULTS_DIR / "nvidia_nim_eval_50s_comparison.json"
    comparison = {
        "task": "NVIDIA NIM evaluation with precompiled bootstrap_fast program",
        "compiled_program_dir": "compiled_bootstrap_fast_program/",
        "eval_size": eval_size,
        "train_size": train_size,
        "eval_index_range": f"{train_size}:{train_size + eval_size}",
        "num_context_passages": 5,
        "use_postprocessor": True,
        "models": all_results,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    with open(output_path, "w") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)
    print(f"\n[SAVE] Full comparison → {output_path}")

    # Comparison table
    print(f"\n{'=' * 75}")
    print("MODEL COMPARISON (50 eval samples, compiled bootstrap_fast program)")
    print(f"{'=' * 75}")
    print(f"{'Model':<55} {'Norm%':>7} {'Ex%':>7} {'Hits':>6} {'Time':>8}")
    print("-" * 75)

    sorted_models = sorted(all_results.items(), key=lambda x: -x[1]["normalized_score"])
    for model_name, result in sorted_models:
        name_short = model_name.split("/")[-1]
        marker = " ◄" if "nvidia" in model_name else ""
        print(
            f"  {name_short:<53} {result['normalized_score']:>6.1f}% "
            f"{result['exact_score']:>6.1f}% {result['normalized_hits']:>5}/50 "
            f"{result['eval_time_s']:>7.1f}s{marker}"
        )

    # Per-example breakdown for NVIDIA NIM
    nvidia_result = all_results.get("nvidia_nim/minimaxai/minimax-m2.7")
    if nvidia_result:
        print(f"\n{'=' * 75}")
        print("NVIDIA NIM: Per-example breakdown (50 samples)")
        print(f"{'=' * 75}")
        hits = [pe for pe in nvidia_result["per_example"] if pe["normalized_match"] >= 0.5]
        misses = [pe for pe in nvidia_result["per_example"] if pe["normalized_match"] < 0.5]

        print(f"\n  HIT ({len(hits)}):")
        for pe in hits:
            print(f"    ✓ {pe['english_text'][:55]!r}")
            print(f"      GOLD: {pe['gold_mirad']}")
            print(f"      PRED: {pe['predicted_mirad']}")

        print(f"\n  MISS ({len(misses)}):")
        for pe in misses:
            print(f"    ✗ {pe['english_text'][:55]!r}")
            print(f"      GOLD: {pe['gold_mirad']}")
            print(f"      PRED: {pe['predicted_mirad']}")

    return comparison


if __name__ == "__main__":
    main()