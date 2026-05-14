#!/usr/bin/env python3
"""Run LabeledFewShot eval with DeepSeek-V4-Flash + CritiqueAndFix on DeepInfra, k=5.

Compares critique-and-fix (max_retries=3) against the k=5 baseline.
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
from mirad_translator.translate import CritiqueAndFixModule

MODEL = "deepseek-ai/DeepSeek-V4-Flash"
NUM_FEWSHOT = 5
NUM_CONTEXT = 5
MAX_RETRIES = 3
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
    print(f"[eval] {NUM_FEWSHOT} few-shot demos, {len(eval_examples)} eval examples, k={NUM_CONTEXT}, max_retries={MAX_RETRIES}")

    # Enrich few-shot demos with pre-computed intermediates (including RAG context)
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

    # Build module with critique-and-fix
    module = CritiqueAndFixModule(
        db_path=None,
        num_context_passages=NUM_CONTEXT,
        max_retries=MAX_RETRIES,
    )

    # Compile with LabeledFewShot
    print("[eval] Compiling with LabeledFewShot...")
    compile_start = time.time()
    optimizer = LabeledFewShot(k=NUM_FEWSHOT)
    compiled = optimizer.compile(student=module, trainset=enriched_fewshot)
    compile_time = time.time() - compile_start
    print(f"[eval] Compile time: {compile_time:.1f}s")

    # Evaluate — note: critique rounds use the same LM so each example takes
    # (1 + 2*max_retries) LM calls in the worst case
    print(f"[eval] Running evaluation (each example may take up to {1 + 2*MAX_RETRIES} LM calls)...")
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
                "critique_rounds": -1,
                "critique_passed": False,
                "feedback": str(e),
                "elapsed_s": round(elapsed, 2),
            })
            continue

        norm_s = normalized_match_metric(example, prediction)
        exact_s = exact_match_metric(example, prediction)
        critique_rounds = getattr(prediction, "critique_rounds", -1)
        critique_passed = getattr(prediction, "critique_passed", False)
        feedback = getattr(prediction, "feedback", "")

        per_example.append({
            "english_text": example.english_text,
            "gold_mirad": example.mirad_text,
            "predicted_mirad": prediction.mirad_text,
            "word_equivalents": prediction.word_equivalents if hasattr(prediction, "word_equivalents") else {},
            "context": prediction.context if hasattr(prediction, "context") else [],
            "normalized_match": norm_s,
            "exact_match": exact_s,
            "critique_rounds": critique_rounds,
            "critique_passed": critique_passed,
            "feedback": feedback,
            "elapsed_s": round(elapsed, 2),
        })

        status = "✓ PASS" if critique_passed else f"✗ {critique_rounds} rounds"
        print(f"  [{i}] ({elapsed:.1f}s) NORM={norm_s} EXACT={exact_s} {status}")
        print(f"       GOLD: {example.mirad_text[:70]}")
        print(f"       PRED: {prediction.mirad_text[:70]}")

    eval_time = time.time() - eval_start

    # Compute scores
    normalized_score = sum(e["normalized_match"] for e in per_example) / len(per_example) * 100
    exact_score = sum(e["exact_match"] for e in per_example) / len(per_example) * 100
    avg_rounds = sum(e["critique_rounds"] for e in per_example if e["critique_rounds"] >= 0) / max(1, sum(1 for e in per_example if e["critique_rounds"] >= 0))
    pass_rate = sum(1 for e in per_example if e["critique_passed"]) / len(per_example) * 100

    summary = {
        "method": "CritiqueAndFix_LabeledFewShot",
        "lm_type": "deepinfra",
        "model": MODEL,
        "num_fewshot": NUM_FEWSHOT,
        "k_context_passages": NUM_CONTEXT,
        "max_retries": MAX_RETRIES,
        "eval_set_size": len(eval_examples),
        "normalized_score": round(normalized_score, 1),
        "exact_score": round(exact_score, 1),
        "avg_critique_rounds": round(avg_rounds, 2),
        "critique_pass_rate": round(pass_rate, 1),
        "compile_time_s": round(compile_time, 2),
        "eval_time_s": round(eval_time, 2),
    }

    # Save results
    results_path = os.path.join(OUT_DIR, "labeled_fewshot_k5_critique.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    per_example_path = os.path.join(OUT_DIR, "labeled_fewshot_k5_critique_per_example.json")
    with open(per_example_path, "w", encoding="utf-8") as f:
        json.dump(per_example, f, indent=2, ensure_ascii=False)

    # Print report
    print(f"\n{'='*60}")
    print(f"CritiqueAndFix Results (k={NUM_CONTEXT}, {NUM_FEWSHOT} demos, max_retries={MAX_RETRIES})")
    print(f"{'='*60}")
    print(f"  Model:              {MODEL}")
    print(f"  Few-shot demos:     {NUM_FEWSHOT}")
    print(f"  RAG passages:       {NUM_CONTEXT}")
    print(f"  Max retries:        {MAX_RETRIES}")
    print(f"  Eval examples:      {len(eval_examples)}")
    print(f"  Normalized match:   {normalized_score:.1f}%")
    print(f"  Exact match:         {exact_score:.1f}%")
    print(f"  Avg critique rounds: {avg_rounds:.2f}")
    print(f"  Critique pass rate:  {pass_rate:.1f}%")
    print(f"  Compile time:        {compile_time:.1f}s")
    print(f"  Eval time:           {eval_time:.1f}s")
    print(f"{'='*60}")

    # Compare with k=5 baseline (no critique)
    k5_path = os.path.join(OUT_DIR, "labeled_fewshot_k5.json")
    if os.path.exists(k5_path):
        k5 = json.load(open(k5_path))
        print(f"\n  vs k=5 baseline (no critique):")
        print(f"    Normalized: {k5['normalized_score']:.1f}% → {normalized_score:.1f}%  ({'+' if normalized_score > k5['normalized_score'] else ''}{normalized_score - k5['normalized_score']:.1f}pp)")
        print(f"    Exact:       {k5['exact_score']:.1f}% → {exact_score:.1f}%  ({'+' if exact_score > k5['exact_score'] else ''}{exact_score - k5['exact_score']:.1f}pp)")

    print(f"\nSaved: {results_path}")
    print(f"Saved: {per_example_path}")


if __name__ == "__main__":
    main()