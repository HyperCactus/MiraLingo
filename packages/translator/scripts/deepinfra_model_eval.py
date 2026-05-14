#!/usr/bin/env python3
"""Parametric DeepInfra model eval: LabeledFewShot k=5 on English→Mirad.

Usage:
    python scripts/deepinfra_model_eval.py --model "deepseek-ai/DeepSeek-V4-Flash" [--output-suffix flash]

Runs the same LabeledFewShot k=5 pipeline for each model, saves per-example + summary JSON.
"""
import argparse
import json
import os
import sys
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "packages", "translator", "src"))

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

import dspy
from dspy import LabeledFewShot

from mirad_translator.evaluate import (
    load_evaluation_set,
    normalized_match_metric,
    exact_match_metric,
    _make_deepinfra_lm,
    _enrich_examples,
)
from mirad_translator.translate import TranslatorModule

NUM_FEWSHOT = 5
NUM_CONTEXT = 5
OUT_DIR = os.path.join(PROJECT_ROOT, "data", "eval_results")


def main():
    parser = argparse.ArgumentParser(description="DeepInfra model eval")
    parser.add_argument("--model", required=True, help="DeepInfra model identifier")
    parser.add_argument("--output-suffix", default=None, help="Output file suffix (defaults to sanitized model name)")
    parser.add_argument("--num-fewshot", type=int, default=NUM_FEWSHOT)
    parser.add_argument("--num-context", type=int, default=NUM_CONTEXT)
    args = parser.parse_args()

    model = args.model
    suffix = args.output_suffix or model.replace("/", "_").replace(".", "-").replace(" ", "_")
    num_fewshot = args.num_fewshot
    num_context = args.num_context

    os.makedirs(OUT_DIR, exist_ok=True)

    print(f"[{suffix}] Configuring LM: {model} on DeepInfra...")
    lm = _make_deepinfra_lm(model=model)
    dspy.settings.configure(lm=lm)

    # Load dataset
    all_examples = load_evaluation_set()
    fewshot_examples = all_examples[:num_fewshot]
    eval_examples = all_examples[num_fewshot:]
    print(f"[{suffix}] {num_fewshot} few-shot demos, {len(eval_examples)} eval examples, k={num_context}")

    # Enrich demos with RAG
    print(f"[{suffix}] Enriching demos with RAG context...")
    enriched_fewshot = _enrich_examples(
        fewshot_examples,
        db_path=None,
        num_context_passages=num_context,
    )

    # Build + compile module
    module = TranslatorModule(db_path=None, num_context_passages=num_context)
    print(f"[{suffix}] Compiling with LabeledFewShot...")
    compile_start = time.time()
    optimizer = LabeledFewShot(k=num_fewshot)
    compiled = optimizer.compile(student=module, trainset=enriched_fewshot)
    compile_time = time.time() - compile_start

    # Evaluate
    print(f"[{suffix}] Running evaluation...")
    eval_start = time.time()

    per_example = []
    for i, example in enumerate(eval_examples):
        start = time.time()
        try:
            prediction = compiled(example.english_text)
            elapsed = time.time() - start
        except Exception as e:
            elapsed = time.time() - start
            print(f"  [{i}] ERROR: {e}")
            per_example.append({
                "english_text": example.english_text,
                "gold_mirad": example.mirad_text,
                "predicted_mirad": f"ERROR: {e}",
                "normalized_match": 0.0,
                "exact_match": 0.0,
                "elapsed_s": round(elapsed, 2),
            })
            continue

        norm_s = normalized_match_metric(example, prediction)
        exact_s = exact_match_metric(example, prediction)
        per_example.append({
            "english_text": example.english_text,
            "gold_mirad": example.mirad_text,
            "predicted_mirad": prediction.mirad_text,
            "word_equivalents": prediction.word_equivalents if hasattr(prediction, "word_equivalents") else {},
            "context": prediction.context if hasattr(prediction, "context") else [],
            "normalized_match": norm_s,
            "exact_match": exact_s,
            "elapsed_s": round(elapsed, 2),
        })

        marker = "✓" if exact_s == 1.0 else "✗"
        print(f"  [{i}] ({elapsed:.1f}s) NORM={norm_s} EXACT={exact_s} {marker}  {example.english_text[:50]}")

    eval_time = time.time() - eval_start

    # Compute scores
    normalized_score = sum(e["normalized_match"] for e in per_example) / len(per_example) * 100
    exact_score = sum(e["exact_match"] for e in per_example) / len(per_example) * 100
    hits = sum(1 for e in per_example if e["exact_match"] == 1.0)
    avg_latency = sum(e["elapsed_s"] for e in per_example) / len(per_example)

    summary = {
        "method": "LabeledFewShot_k5",
        "lm_type": "deepinfra",
        "model": model,
        "num_fewshot": num_fewshot,
        "k_context_passages": num_context,
        "eval_set_size": len(eval_examples),
        "normalized_score": round(normalized_score, 1),
        "exact_score": round(exact_score, 1),
        "exact_hits": hits,
        "avg_latency_s": round(avg_latency, 1),
        "compile_time_s": round(compile_time, 2),
        "eval_time_s": round(eval_time, 2),
    }

    # Save
    results_path = os.path.join(OUT_DIR, f"model_{suffix}.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    per_example_path = os.path.join(OUT_DIR, f"model_{suffix}_per_example.json")
    with open(per_example_path, "w", encoding="utf-8") as f:
        json.dump(per_example, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*50}")
    print(f"  {model}")
    print(f"  Normalized: {normalized_score:.1f}%  |  Exact: {exact_score:.1f}%  |  Hits: {hits}/{len(eval_examples)}")
    print(f"  Avg latency: {avg_latency:.1f}s  |  Total: {eval_time:.1f}s")
    print(f"{'='*50}")
    print(f"Saved: {results_path}")


if __name__ == "__main__":
    main()