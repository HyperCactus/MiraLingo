#!/usr/bin/env python3
"""Evaluate the saved BootstrapRS-compiled program using a different LM.

Compares:
  - DeepSeek-V4-Flash baseline (uncompiled)
  - DeepSeek-V4-Flash + BootstrapRS (compiled on DeepSeek)
  - Llama 3.1 8B baseline (uncompiled)
  - Llama 3.1 8B + BootstrapRS (compiled on DeepSeek, same demos)

All on the same 30-example eval set.
"""

import argparse
import csv
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(".env")

import dspy
from mirad_translator.translate import TranslatorModule
from mirad_translator.evaluate import normalized_match_metric

PROJECT_ROOT = Path(__file__).parent
CSV_PATH = PROJECT_ROOT / "data" / "phrases" / "english-mirad-sentence-pairs.csv"
RESULTS_DIR = PROJECT_ROOT / "data" / "eval_results" / "optimizer_comparison"
COMPILED_PROGRAM_DIR = RESULTS_DIR / "compiled_bootstrap_fast_program"


def load_full_dataset():
    """Load all examples from the sentence pairs CSV."""
    examples = []
    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            examples.append(
                dspy.Example(
                    english_text=row["english_text"].strip(),
                    mirad_text=row["mirad_text"].strip(),
                ).with_inputs("english_text")
            )
    return examples


def _normalize(text: str) -> str:
    """Strip punctuation, lowercase, whitespace-normalize."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def eval_on_examples(module, examples, desc=""):
    """Run module on examples, return per-example results."""
    print(f"\n[EVAL] {len(examples)} examples {desc}...")
    eval_start = time.time()
    per_example = []

    for i, ex in enumerate(examples):
        pred = module(english_text=ex.english_text)
        raw_mirad = pred.mirad_text
        gold = ex.mirad_text

        norm_score = normalized_match_metric(ex, pred)
        exact = 1.0 if _normalize(gold) == _normalize(raw_mirad) else 0.0

        per_example.append({
            "english_text": ex.english_text,
            "gold_mirad": gold,
            "predicted_mirad": raw_mirad,
            "normalized_match": norm_score,
            "exact_match": exact,
        })

        if (i + 1) % 10 == 0:
            sofar = sum(e["normalized_match"] for e in per_example)
            print(f"  {i+1}/{len(examples)}: {sofar}/{i+1} = {sofar/(i+1)*100:.1f}%")

    elapsed = time.time() - eval_start
    hits = sum(e["normalized_match"] for e in per_example)
    total = len(per_example)
    print(f"[EVAL] Done in {elapsed:.1f}s — {hits}/{total} = {hits/total*100:.1f}%")
    return per_example, elapsed


def main():
    parser = argparse.ArgumentParser(description="Eval compiled program with a different LM")
    parser.add_argument("--model", type=str,
                        default="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                        help="DeepInfra model to use")
    parser.add_argument("--num-eval", type=int, default=30,
                        help="Number of eval examples (default 30)")
    parser.add_argument("--baseline-only", action="store_true",
                        help="Only run baseline (skip compiled program)")
    args = parser.parse_args()

    import os
    api_key = os.environ.get("DEEPINFRA_API_KEY")
    api_base = os.environ.get("DEEPINFRA_BASE_URL", "https://api.deepinfra.com/v1/openai")

    # Load eval set (first 30 after train split — same as bootstrap fast run)
    all_examples = load_full_dataset()
    eval_examples = all_examples[50:50 + args.num_eval]  # same offset as bootstrap fast

    model_tag = args.model.split("/")[-1]

    for run_type in (["baseline", "compiled"] if not args.baseline_only else ["baseline"]):
        run_label = f"{run_type}__{model_tag}"
        print(f"\n{'='*70}")
        print(f"RUN: {run_label}")
        print(f"{'='*70}")

        # Configure LM
        lm = dspy.LM(
            model=f"openai/{args.model}",
            api_key=api_key,
            api_base=api_base,
            num_retries=5,
            cache=True,
        )
        dspy.settings.configure(lm=lm)

        # Fresh module (uncompiled) for baseline; load compiled for compiled run
        if run_type == "baseline":
            module = TranslatorModule(num_context_passages=5, use_postprocessor=True)
        else:
            if not COMPILED_PROGRAM_DIR.exists():
                print(f"[SKIP] No compiled program at {COMPILED_PROGRAM_DIR}/")
                dspy.settings.reset()
                continue
            print(f"[LOAD] Compiled program from {COMPILED_PROGRAM_DIR}/")
            module = dspy.load(str(COMPILED_PROGRAM_DIR), allow_pickle=True)
            print(f"[LOAD] Type: {type(module).__name__}")

        # Evaluate
        start = time.time()
        per_example, eval_time = eval_on_examples(module, eval_examples, f"({run_label})")
        total_time = time.time() - start

        hits = sum(e["normalized_match"] for e in per_example)
        exact = sum(e["exact_match"] for e in per_example)
        total = len(per_example)
        norm_pct = hits / total * 100
        exact_pct = exact / total * 100

        result = {
            "run_type": run_type,
            "model": args.model,
            "model_tag": model_tag,
            "eval_size": total,
            "normalized_match_pct": round(norm_pct, 1),
            "normalized_match_hits": int(hits),
            "exact_match_pct": round(exact_pct, 1),
            "exact_match_hits": int(exact),
            "eval_time_s": round(eval_time, 1),
            "total_time_s": round(total_time, 1),
            "per_example": per_example,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        run_path = RESULTS_DIR / f"llama_compare_{run_type}_{model_tag}.json"
        with open(run_path, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"[SAVE] {run_path}")

        print(f"\n  Normalized: {norm_pct:.1f}% ({int(hits)}/{total})")
        print(f"  Exact:      {exact_pct:.1f}% ({int(exact)}/{total})")
        print(f"  Eval time:  {eval_time:.1f}s")

        dspy.settings.reset()

    # Print comparison summary
    print(f"\n{'='*70}")
    print("COMPARISON SUMMARY")
    print(f"{'='*70}")

    # DeepSeek baseline
    bpath = RESULTS_DIR / "baseline.json"
    if bpath.exists():
        with open(bpath) as f:
            b = json.load(f)
        bper = b["per_example"]
        bhits = sum(e["normalized_match"] for e in bper)
        print(f"  DeepSeek-V4-Flash baseline (36-item):  {bhits/len(bper)*100:.1f}%")

    # DeepSeek + BootstrapRS
    bfpath = RESULTS_DIR / "bootstrap_fast_results.json"
    if bfpath.exists():
        with open(bfpath) as f:
            bf = json.load(f)
        bfper = bf["per_example"]
        bfhits = sum(e["normalized_match"] for e in bfper)
        print(f"  DeepSeek + BootstrapRS (30-item):      {bfhits/len(bfper)*100:.1f}%")

    # Llama runs
    for rt in ["baseline", "compiled"]:
        rpath = RESULTS_DIR / f"llama_compare_{rt}_{model_tag}.json"
        if rpath.exists():
            with open(rpath) as f:
                r = json.load(f)
            n = r["eval_size"]
            print(f"  Llama-3.1-8B {rt:8s} ({n}-item):       {r['normalized_match_pct']:.1f}%")

    print(f"{'='*70}")


if __name__ == "__main__":
    main()