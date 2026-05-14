#!/usr/bin/env python3
"""Run trace inspection with DeepSeek-V4-Flash on DeepInfra.

Runs the first N examples through DefaultTranslator with DeepSeek-V4-Flash
and saves per-example predictions + retrieval context.
"""
import json
import os
import sys
import time

# Ensure project root is on the path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "packages", "translator", "src"))

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

import dspy
from mirad_translator.evaluate import (
    load_evaluation_set,
    normalized_match_metric,
    exact_match_metric,
    _make_deepinfra_lm,
)
from mirad_translator.translate import DefaultTranslator

MODEL = "deepseek-ai/DeepSeek-V4-Flash"
NUM_EXAMPLES = 5
OUT_DIR = os.path.join(PROJECT_ROOT, "data", "eval_results")
OUT_PATH = os.path.join(OUT_DIR, "deepseek_v4_flash_trace.json")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    print(f"Configuring LM: {MODEL} on DeepInfra...")
    lm = _make_deepinfra_lm(model=MODEL)
    dspy.settings.configure(lm=lm)

    devset = load_evaluation_set()
    examples = devset[:NUM_EXAMPLES]
    module = DefaultTranslator()

    print(f"Running {len(examples)} examples through DefaultTranslator + {MODEL}...\n")

    traces = []
    for i, example in enumerate(examples):
        start = time.time()
        try:
            prediction = module(example.english_text)
            elapsed = time.time() - start
            norm_score = normalized_match_metric(example, prediction)
            exact_score = exact_match_metric(example, prediction)
        except Exception as e:
            elapsed = time.time() - start
            print(f"  [{i}] ERROR: {e}")
            traces.append({
                "english_text": example.english_text,
                "gold_mirad": example.mirad_text,
                "predicted_mirad": f"ERROR: {e}",
                "word_equivalents": {},
                "context_passages": [],
                "normalized_score": 0.0,
                "exact_score": 0.0,
                "elapsed_s": round(elapsed, 2),
            })
            continue

        we = prediction.word_equivalents if hasattr(prediction, "word_equivalents") else {}
        ctx = prediction.context if hasattr(prediction, "context") else []

        trace = {
            "english_text": example.english_text,
            "gold_mirad": example.mirad_text,
            "predicted_mirad": prediction.mirad_text,
            "word_equivalents": we,
            "context_passages": ctx,
            "normalized_score": norm_score,
            "exact_score": exact_score,
            "elapsed_s": round(elapsed, 2),
        }
        traces.append(trace)

        print(f"  [{i}] ({elapsed:.1f}s)")
        print(f"       EN:    {example.english_text[:70]}")
        print(f"       GOLD:  {example.mirad_text[:70]}")
        print(f"       PRED:  {prediction.mirad_text[:70]}")
        print(f"       NORM={norm_score}  EXACT={exact_score}")
        print()

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump({"model": MODEL, "traces": traces}, f, indent=2, ensure_ascii=False)

    avg_norm = sum(t["normalized_score"] for t in traces) / len(traces)
    avg_exact = sum(t["exact_score"] for t in traces) / len(traces)
    print(f"\n{'='*60}")
    print(f"DeepSeek-V4-Flash Trace Results (first {NUM_EXAMPLES})")
    print(f"{'='*60}")
    print(f"  Avg normalized match: {avg_norm:.1%}")
    print(f"  Avg exact match:       {avg_exact:.1%}")
    print(f"  Saved to: {OUT_PATH}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()