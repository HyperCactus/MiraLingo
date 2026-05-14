#!/usr/bin/env python3
"""Run LabeledFewShot eval with DeepSeek-V4-Flash on DeepInfra, k=5 RAG context.

Compares against the k=0 baseline already run.
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
from mirad_translator.translate import DefaultTranslator, TranslatorModule

MODEL = "deepseek-ai/DeepSeek-V4-Flash"
NUM_FEWSHOT = 5
NUM_CONTEXT = 10
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
    print(f"[eval] {NUM_FEWSHOT} few-shot demos, {len(eval_examples)} eval examples, k={NUM_CONTEXT}")

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

    # Build module with k=5 RAG retrieval
    module = DefaultTranslator(num_context_passages=NUM_CONTEXT)

    # Compile with LabeledFewShot
    print("[eval] Compiling with LabeledFewShot...")
    compile_start = time.time()
    optimizer = LabeledFewShot(k=NUM_FEWSHOT)
    compiled = optimizer.compile(student=module, trainset=enriched_fewshot)
    compile_time = time.time() - compile_start
    print(f"[eval] Compile time: {compile_time:.1f}s")

    # Evaluate
    print("[eval] Running normalized_match evaluation...")
    eval_start = time.time()

    norm_evaluator = Evaluate(
        devset=eval_examples,
        metric=normalized_match_metric,
        num_threads=1,
        display_progress=True,
        display_table=0,
    )
    norm_result = norm_evaluator(compiled)

    exact_evaluator = Evaluate(
        devset=eval_examples,
        metric=exact_match_metric,
        num_threads=1,
        display_progress=True,
        display_table=0,
    )
    exact_result = exact_evaluator(compiled)

    eval_time = time.time() - eval_start
    total_time = time.time() - compile_start

    normalized_score = norm_result.score if hasattr(norm_result, "score") else norm_result
    exact_score = exact_result.score if hasattr(exact_result, "score") else exact_result

    # Per-example predictions
    print("[eval] Collecting per-example predictions...")
    per_example = []
    for ex in eval_examples:
        pred = compiled(ex.english_text)
        norm_s = normalized_match_metric(ex, pred)
        exact_s = exact_match_metric(ex, pred)
        per_example.append({
            "english_text": ex.english_text,
            "gold_mirad": ex.mirad_text,
            "predicted_mirad": pred.mirad_text,
            "word_equivalents": pred.word_equivalents if hasattr(pred, "word_equivalents") else {},
            "context": pred.context if hasattr(pred, "context") else [],
            "normalized_match": norm_s,
            "exact_match": exact_s,
        })

    summary = {
        "method": "LabeledFewShot",
        "lm_type": "deepinfra",
        "model": MODEL,
        "num_fewshot": NUM_FEWSHOT,
        "k_context_passages": NUM_CONTEXT,
        "eval_set_size": len(eval_examples),
        "normalized_score": normalized_score,
        "exact_score": exact_score,
        "compile_time_s": round(compile_time, 2),
        "eval_time_s": round(eval_time, 2),
        "total_time_s": round(total_time, 2),
    }

    # Save results
    results_path = os.path.join(OUT_DIR, "labeled_fewshot_k10.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    per_example_path = os.path.join(OUT_DIR, "labeled_fewshot_k10_per_example.json")
    with open(per_example_path, "w", encoding="utf-8") as f:
        json.dump(per_example, f, indent=2, ensure_ascii=False)

    # Print report
    print(f"\n{'='*60}")
    print(f"LabeledFewShot Results (deepinfra, k={NUM_CONTEXT}, {NUM_FEWSHOT} demos)")
    print(f"{'='*60}")
    print(f"  Model:              {MODEL}")
    print(f"  Few-shot demos:     {NUM_FEWSHOT}")
    print(f"  RAG passages:       {NUM_CONTEXT}")
    print(f"  Eval examples:      {len(eval_examples)}")
    print(f"  Normalized match:   {normalized_score:.1f}%")
    print(f"  Exact match:         {exact_score:.1f}%")
    print(f"  Compile time:        {compile_time:.1f}s")
    print(f"  Eval time:           {eval_time:.1f}s")
    print(f"{'='*60}")

    # Compare with k=5 result
    k5_path = os.path.join(OUT_DIR, "labeled_fewshot_k5.json")
    if os.path.exists(k5_path):
        k5 = json.load(open(k5_path))
        print(f"\n  vs k=5:")
        print(f"    Normalized: {k5['normalized_score']:.1f}% → {normalized_score:.1f}%  ({'+' if normalized_score > k5['normalized_score'] else ''}{normalized_score - k5['normalized_score']:.1f}pp)")
        print(f"    Exact:       {k5['exact_score']:.1f}% → {exact_score:.1f}%  ({'+' if exact_score > k5['exact_score'] else ''}{exact_score - k5['exact_score']:.1f}pp)")

    print(f"\nSaved: {results_path}")
    print(f"Saved: {per_example_path}")


if __name__ == "__main__":
    main()