#!/usr/bin/env python3
"""
Evaluate the precompiled bootstrap_fast DSPy program with:
  - NVIDIA hosted model: bytedance/seed-oss-36b-instruct
  - 50 evaluation samples
  - Progress tracking with ETA

Compares against gold Mirad output.

Usage:
    python run_seed_oss_eval.py
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

PROJECT_ROOT = Path(__file__).resolve().parents[3]
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
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = re.sub(r"\s+", " ", text)
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
    total = len(eval_examples)

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

        # Progress tracking with ETA
        now = time.time()
        elapsed = now - eval_start
        avg_time = elapsed / (i + 1)
        remaining = avg_time * (total - (i + 1))
        eta_min = remaining / 60
        rate = hits_norm / (i + 1) * 100

        if (i + 1) % 10 == 0:
            print(f"  [{i+1}/{total}] {rate:.1f}% | ETA: {eta_min:.1f} min ({eta_min/60:.1f}h)")

    eval_time = time.time() - eval_start
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
    print("SEED OSS 36B EVAL: bytedance/seed-oss-36b-instruct")
    print("50-sample evaluation with precompiled bootstrap_fast program")
    print("=" * 70)

    # Load compiled program
    print(f"\n[LOAD] Loading compiled bootstrap_fast program from {COMPILED_DIR}/")
    compiled = dspy.load(COMPILED_DIR, allow_pickle=True)
    print("[LOAD] ✅ Successfully loaded compiled program")

    # Load dataset
    all_examples = load_full_dataset()
    eval_examples = all_examples[:50]

    print(f"\n[DATA] Eval: {len(eval_examples)} samples (indices 0-49)")

    # LM config for Seed-OSS
    lm_config = {
        "model": "bytedance/seed-oss-36b-instruct",
        "api_key_env": "NVIDIA_API_KEY",
        "api_base_env": "NVIDIA_BASE_URL",
        "default_api_base": "https://integrate.api.nvidia.com/v1",
    }

    # Run evaluation
    result = evaluate_compiled(
        compiled,
        lm_config,
        eval_examples,
        "Seed-OSS 36B",
    )

    # Save results
    cache_path = RESULTS_DIR / "seed_oss_eval_50s.json"
    with open(cache_path, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n[SAVE] Results saved → {cache_path.name}")

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"Model:       {lm_config['model']}")
    print(f"Samples:     {result['total']}")
    print(f"Normalized:  {result['normalized_score']:.1f}%")
    print(f"Exact:       {result['exact_score']:.1f}%")
    print(f"Eval time:   {result['eval_time_s']:.1f}s")
    print(f"{'=' * 60}")

    # Per-example breakdown
    print(f"\n{'=' * 60}")
    print(f"PER-EXAMPLE BREAKDOWN ({result['exact_hits']}/{result['total']} HIT)")
    print(f"{'=' * 60}")

    hits = [pe for pe in result["per_example"] if pe["normalized_match"] == 1.0]
    for i, pe in enumerate(hits, 1):
        print(f"\n[{i}/{result['total']}] ✓ '{pe['english_text'][:50]!r}'")
        print(f"    GOLD: {pe['gold_mirad']}")
        print(f"    PRED: {pe['predicted_mirad']}")

    return result


if __name__ == "__main__":
    main()