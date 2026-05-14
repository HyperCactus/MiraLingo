#!/usr/bin/env python3
"""
BootstrapRS fast optimization run for Mir->En translation.

Mirrors run_bootstrap_fast.py (En->Mir) but trains MiradToEnglishModule.
Saves compiled program + results incrementally.

Usage:
    python run_bootstrap_mir2en.py                  # Run optimization
    python run_bootstrap_mir2en.py --skip-compile   # Load cached results
    python run_bootstrap_mir2en.py --train-size 80 --candidates 3  # Override params
"""

import argparse
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
from mirad_translator.translate import MiradToEnglishModule

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


def normalized_match_mir_to_en(example, prediction, trace=None) -> float:
    gold = _normalize(example.english_text)
    pred = _normalize(prediction.english_text)
    if gold == pred:
        return 1.0
    return 1.0 if _strip_punct(gold) == _strip_punct(pred) else 0.0


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_full_dataset():
    """Load all examples from the sentence pairs CSV - REVERSED for Mir->En."""
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
                        mirad_text=mi,
                        english_text=en,
                    ).with_inputs("mirad_text")
                )

    import random
    rng = random.Random(42)
    rng.shuffle(examples)
    return examples


def enrich_examples_mir2en(module, examples):
    """Pre-compute word_equivalents and context for Mir->En examples (local DB lookups, no LLM calls)."""
    enriched = []
    for i, ex in enumerate(examples):
        if (i + 1) % 20 == 0:
            print(f"  Enriching {i+1}/{len(examples)}...")
        try:
            we_pred = module.lexicon_lookup(mirad_text=ex.mirad_text)
            word_equivalents = we_pred.word_equivalents
            we_str = "\n".join(f"{mi} -> {en}" for mi, en in sorted(word_equivalents.items()))

            ctx_pred = module.context_retrieve(query=ex.mirad_text)
            context_passages = list(ctx_pred.passages)
            ctx_str = "\n\n".join(context_passages)

            enriched.append(
                dspy.Example(
                    mirad_text=ex.mirad_text,
                    word_equivalents=we_str,
                    context_passages=ctx_str,
                    english_text=ex.english_text,
                ).with_inputs("mirad_text", "word_equivalents", "context_passages")
            )
        except Exception:
            enriched.append(
                dspy.Example(
                    mirad_text=ex.mirad_text,
                    english_text=ex.english_text,
                ).with_inputs("mirad_text")
            )

    return enriched


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="BootstrapRS Mir->En optimization")
    parser.add_argument("--skip-compile", action="store_true", help="Skip compilation, load cached results")
    parser.add_argument("--train-size", type=int, default=50, help="Train set size (default: 50)")
    parser.add_argument("--eval-size", type=int, default=30, help="Eval set size (0 = use remaining)")
    parser.add_argument("--max-bootstrapped", type=int, default=4, help="Max bootstrapped demos (default: 4)")
    parser.add_argument("--max-labeled", type=int, default=8, help="Max labeled demos (default: 8)")
    parser.add_argument("--max-rounds", type=int, default=1, help="Max bootstrap rounds (default: 1)")
    parser.add_argument("--candidates", type=int, default=2, help="Random candidate programs (default: 2)")
    args = parser.parse_args()

    print("=" * 70)
    print("BootstrapRS Mir->En FAST OPTIMIZATION")
    print(f"  train_size           = {args.train_size}")
    print(f"  eval_size            = {args.eval_size}")
    print(f"  max_bootstrapped     = {args.max_bootstrapped}")
    print(f"  max_labeled          = {args.max_labeled}")
    print(f"  max_rounds           = {args.max_rounds}")
    print(f"  num_candidate_progs  = {args.candidates}")
    print(f"  total_candidates     = 3 (fixed) + {args.candidates} (random) = {3 + args.candidates}")
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

    # Load data (Mir->En direction)
    all_examples = load_full_dataset()
    print(f"\nTotal dataset: {len(all_examples)} examples")

    # Split data
    trainset = all_examples[:args.train_size]
    if args.eval_size > 0:
        eval_examples = all_examples[args.train_size:args.train_size + args.eval_size]
    else:
        eval_examples = all_examples[args.train_size:]

    print(f"Train set: {len(trainset)} examples")
    print(f"Eval set:  {len(eval_examples)} examples")

    # Enrich training examples (LOCAL DB lookups only, no LLM calls)
    print("\n[ENRICH] Adding lexicon lookups and context to training examples...")
    enrich_start = time.time()
    module_for_enrichment = MiradToEnglishModule(num_context_passages=5)
    enriched_trainset = enrich_examples_mir2en(module_for_enrichment, trainset)
    enrich_time = time.time() - enrich_start
    print(f"[ENRICH] Done in {enrich_time:.1f}s ({len(enriched_trainset)} examples enriched)")

    # Output paths
    results_path = RESULTS_DIR / "mir2en_bootstrap_fast_results.json"

    if args.skip_compile and results_path.exists():
        print("\n[SKIP] Loading cached results from", results_path)
        with open(results_path) as f:
            results = json.load(f)
        per_example = results["per_example"]
        compile_time = results.get("compile_time_s", 0)
        eval_time = results.get("eval_time_s", 0)
        save_success = results.get("compiled_program_saved", False)
        compiled = None
    else:
        # Compile with BootstrapRS
        print("\n[COMPILE] Running BootstrapRS Mir->En optimization...")
        print(f"  Estimated LLM calls: ~{len(trainset) * (3 + args.candidates) + len(eval_examples) * (3 + args.candidates)}")
        print(f"  Estimated time: ~15-25 minutes")

        fresh_module = MiradToEnglishModule(num_context_passages=5)

        optimizer = dspy.BootstrapRS(
            metric=normalized_match_mir_to_en,
            max_bootstrapped_demos=args.max_bootstrapped,
            max_labeled_demos=args.max_labeled,
            max_rounds=args.max_rounds,
            num_candidate_programs=args.candidates,
            max_errors=5,
        )

        compile_start = time.time()
        compiled = optimizer.compile(student=fresh_module, trainset=enriched_trainset)
        compile_time = time.time() - compile_start
        print(f"\n[COMPILE] Completed in {compile_time:.1f}s ({compile_time/60:.1f} min)")

        # Save compiled program IMMEDIATELY
        print(f"\n[SAVE] Saving compiled Mir->En program...")
        save_success = False

        compiled_dir = str(RESULTS_DIR / "compiled_mir2en_program")
        try:
            compiled.save(compiled_dir, save_program=True)
            save_success = True
            print(f"[SAVE] Full program saved to {compiled_dir}/")
        except Exception as e:
            print(f"[SAVE] Full program save failed: {e}")

        # Also save state as JSON
        compiled_state_path = str(RESULTS_DIR / "compiled_mir2en_state.json")
        try:
            compiled.save(compiled_state_path, save_program=False)
            print(f"[SAVE] State saved to {compiled_state_path}")
        except Exception as e:
            print(f"[SAVE] State save failed: {e}")

        # Evaluate on held-out set
        print(f"\n[EVAL] Evaluating compiled program on {len(eval_examples)} examples...")
        eval_start = time.time()
        per_example = []
        for i, ex in enumerate(eval_examples):
            pred = compiled(mirad_text=ex.mirad_text)
            raw_english = pred.english_text
            gold = ex.english_text

            norm_score = normalized_match_mir_to_en(ex, pred)
            exact = 1.0 if _normalize(gold) == _normalize(raw_english) else 0.0

            per_example.append({
                "mirad_text": ex.mirad_text,
                "gold_english": gold,
                "predicted_english": raw_english,
                "normalized_match": norm_score,
                "exact_match": exact,
            })

            if (i + 1) % 10 == 0:
                _save_intermediate(results_path, per_example, compile_time,
                                   time.time() - eval_start, args, trainset, eval_examples, save_success)

        eval_time = time.time() - eval_start
        print(f"[EVAL] Completed in {eval_time:.1f}s ({eval_time/60:.1f} min)")

        # Save final results
        results = {
            "optimizer": "BootstrapRS-fast-mir2en",
            "config": {
                "max_bootstrapped_demos": args.max_bootstrapped,
                "max_labeled_demos": args.max_labeled,
                "max_rounds": args.max_rounds,
                "num_candidate_programs": args.candidates,
                "max_errors": 5,
            },
            "model": "deepseek-ai/DeepSeek-V4-Flash",
            "train_size": len(trainset),
            "eval_size": len(eval_examples),
            "num_context_passages": 5,
            "direction": "mir_to_en",
            "per_example": per_example,
            "compile_time_s": round(compile_time, 2),
            "eval_time_s": round(eval_time, 2),
            "compiled_program_dir": "compiled_mir2en_program/",
            "compiled_program_state": "compiled_mir2en_state.json",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n[SAVE] Final results saved to {results_path}")

    # Compute metrics
    norm_hits = sum(e["normalized_match"] for e in per_example)
    exact_hits = sum(e["exact_match"] for e in per_example)
    total = len(per_example)
    norm_pct = norm_hits / total * 100
    exact_pct = exact_hits / total * 100

    print(f"\n{'=' * 70}")
    print(f"RESULTS: BootstrapRS Mir->En Fast Optimization")
    print(f"{'=' * 70}")
    print(f"  Train examples:       {len(trainset)}")
    print(f"  Eval examples:        {total}")
    print(f"  Normalized match:     {norm_pct:.1f}% ({int(norm_hits)}/{total})")
    print(f"  Exact match:          {exact_pct:.1f}% ({int(exact_hits)}/{total})")
    print(f"  Compile time:         {compile_time:.0f}s ({compile_time/60:.1f} min)")
    print(f"  Eval time:            {eval_time:.0f}s ({eval_time/60:.1f} min)")
    print(f"  Program saved:        {'Yes' if save_success else 'No'}")
    print(f"{'=' * 70}")

    # Error analysis
    errors = [e for e in per_example if e["normalized_match"] == 0]
    print(f"\nError analysis: {len(errors)}/{total} mismatches ({len(errors)/total*100:.1f}%)")
    print("Sample errors (first 10):")
    for i, e in enumerate(errors[:10]):
        g = e["gold_english"][:80]
        p = e["predicted_english"][:80]
        mi = e["mirad_text"][:60]
        print(f"  {i+1}. MI: {mi}")
        print(f"     GOLD: {g}")
        print(f"     PRED: {p}")

    if save_success:
        print("\nTo reload the compiled Mir->En program:")
        print("  import dspy")
        print("  compiled = dspy.load('data/eval_results/optimizer_comparison/compiled_mir2en_program/', allow_pickle=True)")

    return results


def _save_intermediate(results_path, per_example, compile_time, eval_elapsed, args, trainset, eval_examples, save_success):
    """Save intermediate results in case of crash/timeout."""
    results = {
        "optimizer": "BootstrapRS-fast-mir2en",
        "config": {
            "max_bootstrapped_demos": args.max_bootstrapped,
            "max_labeled_demos": args.max_labeled,
            "max_rounds": args.max_rounds,
            "num_candidate_programs": args.candidates,
            "max_errors": 5,
        },
        "model": "deepseek-ai/DeepSeek-V4-Flash",
        "train_size": len(trainset),
        "eval_size": len(eval_examples),
        "per_example": per_example,
        "compile_time_s": round(compile_time, 2),
        "eval_time_s": round(eval_elapsed, 2),
        "compiled_program_saved": save_success,
        "direction": "mir_to_en",
        "intermediate": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    try:
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


if __name__ == "__main__":
    main()