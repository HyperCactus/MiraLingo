#!/usr/bin/env python3
"""Run LabeledFewShot eval with DeepSeek-V4-Flash + MultiHop retrieval on DeepInfra, k=5.

Compares 2-hop retrieval against the k=5 single-hop baseline.
"""
import json
import os
import sys
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "packages", "translator", "src"))

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

import dspy
from dspy import LabeledFewShot, Evaluate

from mirad_translator.evaluate import (
    load_evaluation_set,
    normalized_match_metric,
    exact_match_metric,
    _make_deepinfra_lm,
    _enrich_examples,
    _format_word_equivalents,
    _format_context_passages,
)
from mirad_translator.translate import MultiHopTranslatorModule

MODEL = "deepseek-ai/DeepSeek-V4-Flash"
NUM_FEWSHOT = 5
NUM_CONTEXT = 5
NUM_HOPS = 2
OUT_DIR = os.path.join(PROJECT_ROOT, "data", "eval_results")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    print(f"Configuring LM: {MODEL} on DeepInfra...")
    lm = _make_deepinfra_lm(model=MODEL)
    dspy.settings.configure(lm=lm)

    # Load and split dataset
    all_examples = load_evaluation_set()
    fewshot_examples = all_examples[:NUM_FEWSHOT]
    eval_examples = all_examples[NUM_FEWSHOT:]
    print(f"[eval] {NUM_FEWSHOT} few-shot demos, {len(eval_examples)} eval examples, k={NUM_CONTEXT}, hops={NUM_HOPS}")

    # Enrich few-shot demos with pre-computed intermediates (including RAG context)
    # Note: demos still use single-hop since the LM signature input format is the same
    print("[eval] Enriching demos with RAG context...")
    enriched_fewshot = _enrich_examples(
        fewshot_examples,
        db_path=None,
        num_context_passages=NUM_CONTEXT,
    )

    for i, demo in enumerate(enriched_fewshot):
        we_count = len(demo.word_equivalents.split("\n")) if demo.word_equivalents else 0
        ctx_count = len(demo.context_passages.split("\n")) if demo.context_passages else 0
        print(f"  Demo {i}: EN={demo.english_text[:50]!r}... WE={we_count} items, CTX={ctx_count} lines")

    # Build multi-hop module
    module = MultiHopTranslatorModule(
        db_path=None,
        num_context_passages=NUM_CONTEXT,
        num_hops=NUM_HOPS,
    )

    # Compile with LabeledFewShot
    print("[eval] Compiling with LabeledFewShot...")
    compile_start = time.time()
    optimizer = LabeledFewShot(k=NUM_FEWSHOT)
    compiled = optimizer.compile(student=module, trainset=enriched_fewshot)
    compile_time = time.time() - compile_start
    print(f"[eval] Compile time: {compile_time:.1f}s")

    # Evaluate
    print(f"[eval] Running evaluation (each example uses {NUM_HOPS} retrieval hops + translation)...")
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

        print(f"  [{i}] ({elapsed:.1f}s) NORM={norm_s} EXACT={exact_s}")
        print(f"       GOLD: {example.mirad_text[:70]}")
        print(f"       PRED: {prediction.mirad_text[:70]}")

    eval_time = time.time() - eval_start

    # Compute scores
    normalized_score = sum(e["normalized_match"] for e in per_example) / len(per_example) * 100
    exact_score = sum(e["exact_match"] for e in per_example) / len(per_example) * 100

    summary = {
        "method": "MultiHop_LabeledFewShot",
        "lm_type": "deepinfra",
        "model": MODEL,
        "num_fewshot": NUM_FEWSHOT,
        "k_context_passages": NUM_CONTEXT,
        "num_hops": NUM_HOPS,
        "eval_set_size": len(eval_examples),
        "normalized_score": round(normalized_score, 1),
        "exact_score": round(exact_score, 1),
        "compile_time_s": round(compile_time, 2),
        "eval_time_s": round(eval_time, 2),
    }

    # Save results
    results_path = os.path.join(OUT_DIR, f"labeled_fewshot_k5_hops{NUM_HOPS}.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    per_example_path = os.path.join(OUT_DIR, f"labeled_fewshot_k5_hops{NUM_HOPS}_per_example.json")
    with open(per_example_path, "w", encoding="utf-8") as f:
        json.dump(per_example, f, indent=2, ensure_ascii=False)

    # Print report
    print(f"\n{'='*60}")
    print(f"MultiHop LabeledFewShot Results (k={NUM_CONTEXT}, {NUM_FEWSHOT} demos, {NUM_HOPS} hops)")
    print(f"{'='*60}")
    print(f"  Model:              {MODEL}")
    print(f"  Few-shot demos:     {NUM_FEWSHOT}")
    print(f"  RAG passages:       {NUM_CONTEXT}")
    print(f"  Retrieval hops:     {NUM_HOPS}")
    print(f"  Eval examples:      {len(eval_examples)}")
    print(f"  Normalized match:   {normalized_score:.1f}%")
    print(f"  Exact match:         {exact_score:.1f}%")
    print(f"  Compile time:        {compile_time:.1f}s")
    print(f"  Eval time:           {eval_time:.1f}s")
    print(f"{'='*60}")

    # Compare with k=5 single-hop baseline
    baseline_path = os.path.join(OUT_DIR, "labeled_fewshot_k5.json")
    if os.path.exists(baseline_path):
        baseline = json.load(open(baseline_path))
        print(f"\n  vs k=5 single-hop baseline (no multi-hop):")
        print(f"    Normalized: {baseline['normalized_score']:.1f}% → {normalized_score:.1f}%  ({'+' if normalized_score > baseline['normalized_score'] else ''}{normalized_score - baseline['normalized_score']:.1f}pp)")
        print(f"    Exact:       {baseline['exact_score']:.1f}% → {exact_score:.1f}%  ({'+' if exact_score > baseline['exact_score'] else ''}{exact_score - baseline['exact_score']:.1f}pp)")

    print(f"\nSaved: {results_path}")
    print(f"Saved: {per_example_path}")


if __name__ == "__main__":
    main()