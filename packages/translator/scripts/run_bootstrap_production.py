#!/usr/bin/env python3
"""
BootstrapRS production optimization run for En→Mir translation.

Uses all available data with a robust BootstrapRS configuration.
Saves the compiled program for later reuse (no need to re-run expensive optimization).

Usage:
    python run_bootstrap_production.py [--skip-compile]

With no flags, runs the full optimization (~1-2 hours).
--skip-compile loads cached results if they exist.
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "translator" / "src"))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

import dspy
from mirad_translator.translate import TranslatorModule
from mirad_translator.evaluate import save_compiled_program

RESULTS_DIR = PROJECT_ROOT / "data" / "eval_results" / "optimizer_comparison"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


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


def normalized_match_en_to_mir(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    gold = _normalize(example.mirad_text)
    pred = _normalize(prediction.mirad_text)
    if gold == pred:
        return 1.0
    return 1.0 if _strip_punct(gold) == _strip_punct(pred) else 0.0


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_full_dataset():
    """Load all 613 examples from the sentence pairs CSV."""
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

    # Shuffle deterministically for reproducibility
    import random
    rng = random.Random(42)
    rng.shuffle(examples)

    return examples


def split_data(examples, train_ratio=0.85):
    """Split examples into train and eval sets."""
    split_idx = int(len(examples) * train_ratio)
    return examples[:split_idx], examples[split_idx:]


def enrich_examples(module, examples):
    """Pre-compute word_equivalents and context for examples so DSPy demos include them."""
    enriched = []
    for ex in examples:
        try:
            we_pred = module.lexicon_lookup(english_text=ex.english_text)
            word_equivalents = we_pred.word_equivalents
            we_str = "\n".join(f"{en} → {mi}" for en, mi in sorted(word_equivalents.items()))

            ctx_pred = module.context_retrieve(query=ex.english_text)
            context_passages = list(ctx_pred.passages)
            ctx_str = "\n\n".join(context_passages)

            enriched.append(
                dspy.Example(
                    english_text=ex.english_text,
                    word_equivalents=we_str,
                    context_passages=ctx_str,
                    mirad_text=ex.mirad_text,
                ).with_inputs("english_text", "word_equivalents", "context_passages")
            )
        except Exception as e:
            # Fall back to un-enriched example
            enriched.append(
                dspy.Example(
                    english_text=ex.english_text,
                    mirad_text=ex.mirad_text,
                ).with_inputs("english_text")
            )

    return enriched


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="BootstrapRS production optimization")
    parser.add_argument("--skip-compile", action="store_true", help="Skip compilation, load cached results")
    parser.add_argument("--train-size", type=int, default=0, help="Override train set size (0 = use 85%%)")
    parser.add_argument("--max-bootstrapped", type=int, default=8, help="Max bootstrapped demos")
    parser.add_argument("--max-labeled", type=int, default=16, help="Max labeled demos")
    parser.add_argument("--max-rounds", type=int, default=2, help="Max bootstrap rounds")
    parser.add_argument("--candidates", type=int, default=4, help="Number of candidate programs")
    args = parser.parse_args()

    print("=" * 70)
    print("BootstrapRS PRODUCTION OPTIMIZATION")
    print(f"  max_bootstrapped_demos={args.max_bootstrapped}")
    print(f"  max_labeled_demos={args.max_labeled}")
    print(f"  max_rounds={args.max_rounds}")
    print(f"  num_candidate_programs={args.candidates}")
    print("=" * 70)

    # Configure LM
    api_key = os.environ.get("DEEPINFRA_API_KEY")
    api_base = os.environ.get("DEEPINFRA_BASE_URL", "https://api.deepinfra.com/v1/openai")
    lm = dspy.LM(
        model="openai/deepseek-ai/DeepSeek-V4-Flash",
        api_key=api_key,
        api_base=api_base,
        num_retries=5,
        cache=True,
    )
    dspy.settings.configure(lm=lm)

    # Load data
    all_examples = load_full_dataset()
    print(f"\nTotal dataset: {len(all_examples)} examples")

    if args.train_size > 0:
        trainset = all_examples[:args.train_size]
        eval_examples = all_examples[args.train_size:]
    else:
        trainset, eval_examples = split_data(all_examples, train_ratio=0.85)

    print(f"Train set: {len(trainset)} examples")
    print(f"Eval set: {len(eval_examples)} examples")

    # Enrich training examples
    print("\nEnriching training examples with lexicon lookups and context...")
    module_for_enrichment = TranslatorModule(num_context_passages=5, use_postprocessor=True)
    enriched_trainset = enrich_examples(module_for_enrichment, trainset)
    print(f"Enriched {len(enriched_trainset)} training examples")

    # Output paths
    compiled_path = str(RESULTS_DIR / "compiled_bootstrap_production.json")
    results_path = RESULTS_DIR / "bootstrap_production_results.json"

    if args.skip_compile and results_path.exists():
        print("\n[SKIP] Loading cached results from", results_path)
        with open(results_path) as f:
            results = json.load(f)
        per_example = results["per_example"]
        compile_time = results.get("compile_time_s", 0)
        eval_time = results.get("eval_time_s", 0)
    else:
        # Compile with BootstrapRS
        print("\n[COMPILE] Running BootstrapRS optimization...")
        print(f"  This will take approximately 30-90 minutes depending on API speed.")
        print(f"  Saving compiled program to: {compiled_path}")

        fresh_module = TranslatorModule(num_context_passages=5, use_postprocessor=True)

        optimizer = dspy.BootstrapRS(
            metric=normalized_match_en_to_mir,
            max_bootstrapped_demos=args.max_bootstrapped,
            max_labeled_demos=args.max_labeled,
            max_rounds=args.max_rounds,
            num_candidate_programs=args.candidates,
            max_errors=10,  # Tolerate API failures
        )

        compile_start = time.time()
        compiled = optimizer.compile(student=fresh_module, trainset=enriched_trainset)
        compile_time = time.time() - compile_start
        print(f"\n[COMPILE] Completed in {compile_time:.1f}s ({compile_time/60:.1f} min)")

        # Save compiled program
        print(f"\n[SAVE] Saving compiled program...")
        try:
            save_compiled_program(compiled, compiled_path)
        except Exception as e:
            print(f"[SAVE] Warning: Could not save compiled program: {e}")
            # Try alternative save method
            try:
                import datetime
                save_data = dspy.export(program=compiled)
                meta = {
                    "saved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "module_type": type(compiled).__name__,
                    "optimizer": "BootstrapRS",
                    "config": {
                        "max_bootstrapped_demos": args.max_bootstrapped,
                        "max_labeled_demos": args.max_labeled,
                        "max_rounds": args.max_rounds,
                        "num_candidate_programs": args.candidates,
                    },
                    "train_size": len(trainset),
                    "model": "deepseek-ai/DeepSeek-V4-Flash",
                    "note": "Reload with: from mirad_translator.evaluate import load_compiled_program; module = load_compiled_program(path)",
                }
                payload = {**save_data, "_meta": meta}
                with open(compiled_path, "w", encoding="utf-8") as f:
                    json.dump(payload, f, indent=2, ensure_ascii=False)
                print(f"[SAVE] Compiled program saved to {compiled_path}")
            except Exception as e2:
                print(f"[SAVE] Failed to save compiled program: {e2}")

        # Evaluate on held-out set
        print(f"\n[EVAL] Evaluating compiled program on {len(eval_examples)} examples...")
        eval_start = time.time()
        per_example = []
        for i, ex in enumerate(eval_examples):
            if (i + 1) % 10 == 0:
                print(f"  Evaluated {i+1}/{len(eval_examples)}...")
            pred = compiled(english_text=ex.english_text)
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

        eval_time = time.time() - eval_start
        print(f"[EVAL] Completed in {eval_time:.1f}s ({eval_time/60:.1f} min)")

        # Save results
        results = {
            "optimizer": "BootstrapRS",
            "config": {
                "max_bootstrapped_demos": args.max_bootstrapped,
                "max_labeled_demos": args.max_labeled,
                "max_rounds": args.max_rounds,
                "num_candidate_programs": args.candidates,
                "max_errors": 10,
            },
            "model": "deepseek-ai/DeepSeek-V4-Flash",
            "train_size": len(trainset),
            "eval_size": len(eval_examples),
            "num_context_passages": 5,
            "use_postprocessor": True,
            "per_example": per_example,
            "compile_time_s": round(compile_time, 2),
            "eval_time_s": round(eval_time, 2),
            "compiled_program_path": compiled_path,
        }
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n[SAVE] Results saved to {results_path}")

    # Compute metrics
    norm_hits = sum(e["normalized_match"] for e in per_example)
    exact_hits = sum(e["exact_match"] for e in per_example)
    total = len(per_example)
    norm_pct = norm_hits / total * 100
    exact_pct = exact_hits / total * 100

    # Load baseline for comparison
    baseline_path = RESULTS_DIR / "baseline.json"
    if baseline_path.exists():
        with open(baseline_path) as f:
            baseline_data = json.load(f)
        baseline_examples = baseline_data["per_example"]
        b_norm = sum(e["normalized_match"] for e in baseline_examples)
        b_total = len(baseline_examples)
        b_pct = b_norm / b_total * 100
        delta = norm_pct - b_pct
        print(f"\n{'=' * 70}")
        print(f"RESULTS: BootstrapRS Production Optimization")
        print(f"{'=' * 70}")
        print(f"  Train examples:    {len(trainset)}")
        print(f"  Eval examples:      {total}")
        print(f"  Normalized match:   {norm_pct:.1f}% ({int(norm_hits)}/{total})")
        print(f"  Exact match:        {exact_pct:.1f}% ({int(exact_hits)}/{total})")
        print(f"  Baseline:           {b_pct:.1f}%")
        print(f"  Delta vs baseline:  {delta:+.1f}pp")
        print(f"  Compile time:       {compile_time:.0f}s ({compile_time/60:.1f} min)")
        print(f"  Eval time:          {eval_time:.0f}s ({eval_time/60:.1f} min)")
        print(f"  Compiled program:   {compiled_path}")
        print(f"{'=' * 70}")
    else:
        print(f"\n{'=' * 70}")
        print(f"RESULTS: BootstrapRS Production Optimization")
        print(f"{'=' * 70}")
        print(f"  Train examples:    {len(trainset)}")
        print(f"  Eval examples:    {total}")
        print(f"  Normalized match: {norm_pct:.1f}% ({int(norm_hits)}/{total})")
        print(f"  Exact match:      {exact_pct:.1f}% ({int(exact_hits)}/{total})")
        print(f"  Compile time:     {compile_time:.0f}s ({compile_time/60:.1f} min)")
        print(f"  Eval time:        {eval_time:.0f}s ({eval_time/60:.1f} min)")
        print(f"  Compiled program: {compiled_path}")
        print(f"{'=' * 70}")

    # Error analysis
    errors = [e for e in per_example if e["normalized_match"] == 0]
    print(f"\nError analysis: {len(errors)}/{total} mismatches ({len(errors)/total*100:.1f}%)")
    print("Top 10 errors:")
    for i, e in enumerate(errors[:10]):
        g = e["gold_mirad"][:60]
        p = e["predicted_mirad"][:60]
        print(f"  {i+1}. GOLD: {g}")
        print(f"     PRED: {p}")
        print()

    # How to reload
    print("To reload the compiled program later:")
    print("  from mirad_translator.evaluate import load_compiled_program")
    print(f"  module = load_compiled_program('{compiled_path}')")
    print("  result = module(english_text='The house is big.')")
    print("  print(result.mirad_text)")

    return results


if __name__ == "__main__":
    main()