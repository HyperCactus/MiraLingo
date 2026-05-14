#!/usr/bin/env python3
"""
Evaluate precompiled bootstrapRS program with additional DeepInfra models.

Compares performance across:
  - deepseek-ai/DeepSeek-V4-Flash (existing baseline)
  - meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo
  - meta-llama/Llama-3.3-70B-Instruct-Turbo

Usage:
    python run_model_comparison.py
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "translator" / "src"))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

import dspy
from mirad_translator.translate import TranslatorModule

RESULTS_DIR = PROJECT_ROOT / "data" / "eval_results" / "optimizer_comparison"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

COMPILED_DIR = str(RESULTS_DIR / "compiled_bootstrap_fast_program")

# Models to evaluate
MODELS = [
    "deepseek-ai/DeepSeek-V4-Flash",
    "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    "meta-llama/Llama-3.3-70B-Instruct-Turbo",
]


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
    gold = _normalize(example.mirad_text)
    pred = _normalize(prediction.mirad_text)
    if gold == pred:
        return 1.0
    return 1.0 if _strip_punct(gold) == _strip_punct(pred) else 0.0


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_full_dataset():
    """Load all examples from the sentence pairs CSV."""
    import csv
    csv_path = PROJECT_ROOT / "data" / "phrases" / "english-mirad-sentence-pairs.csv"

    examples = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            en = row["english"].strip()
            mi = row["mirad"].strip()
            if en and mi:
                examples.append(
                    dspy.Example(
                        english_text=en,
                        mirad_text=mi,
                    ).with_inputs("english_text")
                )

    # Shuffle deterministically
    import random
    rng = random.Random(42)
    rng.shuffle(examples)
    return examples


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate_with_model(compiled_program, model_name, eval_examples):
    """Evaluate compiled program with a specific model."""
    print(f"\n{'=' * 70}")
    print(f"Evaluating with model: {model_name}")
    print(f"{'=' * 70}")

    # Configure LM
    api_key = os.environ.get("DEEPINFRA_API_KEY")
    api_base = os.environ.get("DEEPINFRA_BASE_URL", "https://api.deepinfra.com/v1/openai")

    lm = dspy.LM(
        model=f"openai/{model_name}",
        api_key=api_key,
        api_base=api_base,
        num_retries=5,
        cache=True,
    )
    dspy.settings.configure(lm=lm)

    # Evaluate
    eval_start = time.time()
    per_example = []
    for i, ex in enumerate(eval_examples):
        pred = compiled_program(english_text=ex.english_text)
        raw_mirad = pred.mirad_text
        gold = ex.mirad_text

        norm_score = normalized_match_en_to_mir(ex, pred)
        exact = 1.0 if _normalize(gold) == _normalize(raw_mirad) else 0.0

        per_example.append({
            "english_text": ex.english_text,
            "gold_mirad": gold,
            "predicted_mirad": raw_mirad,
            "normalized_match": norm_score,
            "exact_match": exact,
        })

        if (i + 1) % 10 == 0:
            print(f"  Progress: {i+1}/{len(eval_examples)} examples evaluated")

    eval_time = time.time() - eval_start
    print(f"  Completed in {eval_time:.1f}s ({eval_time/60:.1f} min)")

    return per_example, eval_time


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("MODEL COMPARISON: Precompiled BootstrapRS Program")
    print("=" * 70)

    # Load compiled program
    print(f"\n[LOAD] Loading compiled program from {COMPILED_DIR}/")
    try:
        compiled = dspy.load(COMPILED_DIR, allow_pickle=True)
        print("[LOAD] Successfully loaded compiled program")
    except Exception as e:
        print(f"[LOAD] Failed to load compiled program: {e}")
        return

    # Load evaluation dataset (same 30 examples used in original eval)
    all_examples = load_full_dataset()
    train_size = 50
    eval_size = 30
    eval_examples = all_examples[train_size:train_size + eval_size]

    print(f"\n[DATA] Using {len(eval_examples)} evaluation examples (indices {train_size}-{train_size + eval_size - 1})")

    # Evaluate with each model
    all_results = {}

    # Load existing DeepSeek-V4-Flash results if available
    baseline_path = RESULTS_DIR / "bootstrap_fast_results.json"
    if baseline_path.exists():
        print(f"\n[LOAD] Loading existing DeepSeek-V4-Flash results from {baseline_path}")
        with open(baseline_path) as f:
            baseline_data = json.load(f)
        baseline_examples = baseline_data["per_example"]
        baseline_eval_time = baseline_data.get("eval_time_s", 0)

        # Compute metrics
        norm_hits = sum(e["normalized_match"] for e in baseline_examples)
        exact_hits = sum(e["exact_match"] for e in baseline_examples)
        total = len(baseline_examples)
        norm_pct = norm_hits / total * 100
        exact_pct = exact_hits / total * 100

        all_results["deepseek-ai/DeepSeek-V4-Flash"] = {
            "per_example": baseline_examples,
            "eval_time_s": round(baseline_eval_time, 2),
            "normalized_score": norm_pct,
            "exact_score": exact_pct,
            "normalized_hits": int(norm_hits),
            "exact_hits": int(exact_hits),
            "total": total,
        }

        print(f"  Normalized match: {norm_pct:.1f}% ({int(norm_hits)}/{total})")
        print(f"  Exact match:     {exact_pct:.1f}% ({int(exact_hits)}/{total})")
        print(f"  Eval time:       {baseline_eval_time:.1f}s")

    for model_name in MODELS:
        # Skip DeepSeek-V4-Flash if we already loaded it
        if model_name == "deepseek-ai/DeepSeek-V4-Flash" and model_name in all_results:
            continue

        # Check if we already have results for this model
        model_results_path = RESULTS_DIR / f"model_comparison_{model_name.replace('/', '_')}.json"

        if model_results_path.exists():
            print(f"\n[SKIP] Loading cached results for {model_name} from {model_results_path}")
            with open(model_results_path) as f:
                cached_data = json.load(f)
            per_example = cached_data["per_example"]
            eval_time = cached_data["eval_time_s"]
        else:
            per_example, eval_time = evaluate_with_model(compiled, model_name, eval_examples)

            # Save per-model results for caching
            model_cache = {
                "model": model_name,
                "per_example": per_example,
                "eval_time_s": eval_time,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            with open(model_results_path, "w") as f:
                json.dump(model_cache, f, indent=2, ensure_ascii=False)
            print(f"[SAVE] Cached results to {model_results_path}")

        # Compute metrics
        norm_hits = sum(e["normalized_match"] for e in per_example)
        exact_hits = sum(e["exact_match"] for e in per_example)
        total = len(per_example)
        norm_pct = norm_hits / total * 100
        exact_pct = exact_hits / total * 100

        all_results[model_name] = {
            "per_example": per_example,
            "eval_time_s": round(eval_time, 2),
            "normalized_score": norm_pct,
            "exact_score": exact_pct,
            "normalized_hits": int(norm_hits),
            "exact_hits": int(exact_hits),
            "total": total,
        }

        print(f"\n  Results for {model_name}:")
        print(f"    Normalized match: {norm_pct:.1f}% ({int(norm_hits)}/{total})")
        print(f"    Exact match:     {exact_pct:.1f}% ({int(exact_hits)}/{total})")
        print(f"    Eval time:       {eval_time:.1f}s")

    # Save results
    output_path = RESULTS_DIR / "model_comparison_results.json"
    comparison_data = {
        "task": "Model comparison with precompiled BootstrapRS program",
        "compiled_program_dir": "compiled_bootstrap_fast_program/",
        "eval_size": eval_size,
        "train_size": train_size,
        "num_context_passages": 5,
        "use_postprocessor": True,
        "models": all_results,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    with open(output_path, "w") as f:
        json.dump(comparison_data, f, indent=2, ensure_ascii=False)
    print(f"\n[SAVE] Results saved to {output_path}")

    # Print comparison table
    print(f"\n{'=' * 70}")
    print("COMPARISON TABLE")
    print(f"{'=' * 70}")
    print(f"{'Model':<55} {'Norm%':>7} {'Ex%':>7} {'Hits':>5} {'Time(s)':>8}")
    print("-" * 70)

    for model_name in MODELS:
        result = all_results[model_name]
        name_short = model_name.split("/")[-1]
        print(f"  {name_short:<53} {result['normalized_score']:>6.1f}% {result['exact_score']:>6.1f}% {result['normalized_hits']:>5} {result['eval_time_s']:>8.1f}s")

    # Find best model
    best_model = max(all_results.keys(), key=lambda m: all_results[m]["normalized_score"])
    best_score = all_results[best_model]["normalized_score"]

    print(f"\nBest model: {best_model.split('/')[-1]} at {best_score:.1f}%")

    # Compare to baseline (DeepSeek-V4-Flash)
    baseline_model = "deepseek-ai/DeepSeek-V4-Flash"
    baseline_score = all_results[baseline_model]["normalized_score"]

    print(f"\nComparison to baseline ({baseline_model.split('/')[-1]}):")
    for model_name in MODELS:
        if model_name != baseline_model:
            delta = all_results[model_name]["normalized_score"] - baseline_score
            name_short = model_name.split("/")[-1]
            print(f"  {name_short}: {delta:+.1f}pp")

    return comparison_data


if __name__ == "__main__":
    import sys
    main()
