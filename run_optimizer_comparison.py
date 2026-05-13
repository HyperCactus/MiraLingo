#!/usr/bin/env python3
"""
Lightweight optimizer comparison: SIMBA, GEPA, BootstrapRS, MIPROv2.

Runs each optimizer with minimal iterations to compare their effect on
En→Mir translation quality. Saves compiled programs and per-example results.

Usage:
    python run_optimizer_comparison.py [--skip-compile] [--optimizer SIMBA]

With no flags, runs all 4 optimizers sequentially.
--skip-compile loads cached results (if they exist) and skips compilation.
--optimizer runs only the named optimizer.
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
from mirad_translator.evaluate import (
    load_evaluation_set,
    normalized_match_metric,
    save_compiled_program,
)

OUT_DIR = PROJECT_ROOT / "data" / "eval_results" / "optimizer_comparison"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    """Normalize text for comparison: strip, collapse whitespace, normalize quotes."""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    return text


def _strip_punct(s: str) -> str:
    """Strip punctuation for normalized match."""
    s = re.sub(r'[.,!?;:()"\'\[\]{}]', "", s)
    return re.sub(r"\s+", " ", s).strip()


def normalized_match_en_to_mir(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    """Normalized exact match: ignores whitespace and most punctuation."""
    gold = _normalize(example.mirad_text)
    pred = _normalize(prediction.mirad_text)
    if gold == pred:
        return 1.0
    return 1.0 if _strip_punct(gold) == _strip_punct(pred) else 0.0


# ---------------------------------------------------------------------------
# Optimizer runners
# ---------------------------------------------------------------------------

def configure_lm():
    """Configure DeepInfra LM for compilation."""
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
    return lm


def get_data():
    """Load evaluation set, split into train/eval."""
    all_examples = load_evaluation_set()
    # First 5 always for few-shot; rest for evaluation
    trainset = all_examples[:8]  # Small train set for lightweight run
    eval_examples = all_examples[8:]
    return trainset, eval_examples


def enrich_examples(module, examples):
    """Pre-compute word_equivalents and context for examples so DSPy demos include them."""
    enriched = []
    for ex in examples:
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
    return enriched


def run_simba(trainset, eval_examples, module, lm):
    """Run SIMBA optimizer (lightweight config)."""
    print("\n" + "=" * 70)
    print("SIMBA Optimizer (lightweight: 2 candidates, 3 steps)")
    print("=" * 70)

    optimizer = dspy.SIMBA(
        metric=normalized_match_en_to_mir,
        bsize=8,
        num_candidates=2,     # Light: only 2 candidate programs
        max_steps=3,          # Light: only 3 optimization steps
        max_demos=4,
        prompt_model=lm,
    )

    compile_start = time.time()
    compiled = optimizer.compile(student=module, trainset=trainset)
    compile_time = time.time() - compile_start
    print(f"[SIMBA] Compile time: {compile_time:.1f}s")

    return compiled, compile_time


def run_gepa(trainset, eval_examples, module, lm):
    """Run GEPA optimizer (lightweight config)."""
    print("\n" + "=" * 70)
    print("GEPA Optimizer (lightweight: auto=light)")
    print("=" * 70)

    # GEPA requires a specific feedback metric signature
    # The metric must accept (example, prediction, trace) and return feedback
    def gepa_metric(example, prediction, trace=None):
        score = normalized_match_en_to_mir(example, prediction, trace)
        return score

    optimizer = dspy.GEPA(
        metric=gepa_metric,
        auto="light",             # Light auto mode
        max_full_evals=3,        # Light: only 3 full evals
        num_threads=1,
        seed=42,
    )

    compile_start = time.time()
    compiled = optimizer.compile(student=module, trainset=trainset)
    compile_time = time.time() - compile_start
    print(f"[GEPA] Compile time: {compile_time:.1f}s")

    return compiled, compile_time


def run_bootstrap_rs(trainset, eval_examples, module, lm):
    """Run BootstrapRS optimizer (lightweight config)."""
    print("\n" + "=" * 70)
    print("BootstrapRS Optimizer (lightweight: 4 candidates, 1 round)")
    print("=" * 70)

    optimizer = dspy.BootstrapRS(
        metric=normalized_match_en_to_mir,
        max_bootstrapped_demos=4,
        max_labeled_demos=8,
        max_rounds=1,
        num_candidate_programs=4,  # Light: only 4 candidates
        max_errors=5,
    )

    compile_start = time.time()
    compiled = optimizer.compile(student=module, trainset=trainset)
    compile_time = time.time() - compile_start
    print(f"[BootstrapRS] Compile time: {compile_time:.1f}s")

    return compiled, compile_time


def run_miprov2(trainset, eval_examples, module, lm):
    """Run MIPROv2 optimizer (lightweight config)."""
    print("\n" + "=" * 70)
    print("MIPROv2 Optimizer (lightweight: auto=light)")
    print("=" * 70)

    optimizer = dspy.MIPROv2(
        metric=normalized_match_en_to_mir,
        prompt_model=lm,
        max_bootstrapped_demos=4,
        max_labeled_demos=8,
        auto="light",            # Light mode (sets num_candidates and num_trials automatically)
        max_errors=5,
        num_threads=1,
    )

    compile_start = time.time()
    compiled = optimizer.compile(student=module, trainset=trainset)
    compile_time = time.time() - compile_start
    print(f"[MIPROv2] Compile time: {compile_time:.1f}s")

    return compiled, compile_time


def evaluate_on_set(compiled, eval_examples):
    """Run evaluation and return per-example results."""
    per_example = []
    for ex in eval_examples:
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
    return per_example


def run_optimizer(name: str, trainset, eval_examples, module, lm):
    """Dispatch to the named optimizer."""
    runners = {
        "SIMBA": run_simba,
        "GEPA": run_gepa,
        "BootstrapRS": run_bootstrap_rs,
        "MIPROv2": run_miprov2,
    }
    if name not in runners:
        raise ValueError(f"Unknown optimizer: {name}. Choose from: {list(runners.keys())}")
    return runners[name](trainset, eval_examples, module, lm)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Lightweight optimizer comparison")
    parser.add_argument("--skip-compile", action="store_true", help="Skip compilation, load cached results")
    parser.add_argument("--optimizer", choices=["SIMBA", "GEPA", "BootstrapRS", "MIPROv2"],
                        help="Run only the named optimizer")
    parser.add_argument("--eval-size", type=int, default=0,
                        help="Limit eval set size (0 = use all)")
    args = parser.parse_args()

    print("=" * 70)
    print("OPTIMIZER COMPARISON: SIMBA vs GEPA vs BootstrapRS vs MIPROv2")
    print("Lightweight config (minimal candidates, few rounds)")
    print("=" * 70)

    lm = configure_lm()
    module = TranslatorModule(num_context_passages=5, use_postprocessor=True)
    trainset, eval_examples = get_data()

    # Optionally limit eval set size for faster testing
    if args.eval_size > 0:
        eval_examples = eval_examples[:args.eval_size]

    print(f"Train set: {len(trainset)} examples")
    print(f"Eval set: {len(eval_examples)} examples")

    # Enrich training examples with pre-computed intermediates
    # (so DSPy can include them in demos)
    print("Enriching training examples with lexicon lookups and context...")
    enriched_trainset = enrich_examples(module, trainset)

    # Baseline: unoptimized module
    baseline_path = OUT_DIR / "baseline.json"
    if args.skip_compile and baseline_path.exists():
        print("\n[BASELINE] Loading cached baseline results...")
        with open(baseline_path) as f:
            baseline_data = json.load(f)
        baseline_examples = baseline_data["per_example"]
    else:
        print("\n[BASELINE] Evaluating unoptimized TranslatorModule...")
        eval_start = time.time()
        baseline_examples = evaluate_on_set(module, eval_examples)
        eval_time = time.time() - eval_start

        baseline_data = {
            "optimizer": "baseline",
            "method": "TranslatorModule (unoptimized)",
            "model": "deepseek-ai/DeepSeek-V4-Flash",
            "num_context_passages": 5,
            "use_postprocessor": True,
            "per_example": baseline_examples,
            "eval_time_s": round(eval_time, 2),
        }
        with open(baseline_path, "w") as f:
            json.dump(baseline_data, f, indent=2, ensure_ascii=False)

    baseline_norm = sum(e["normalized_match"] for e in baseline_examples)
    baseline_exact = sum(e["exact_match"] for e in baseline_examples)
    baseline_total = len(baseline_examples)
    baseline_pct = baseline_norm / baseline_total * 100
    print(f"  Baseline: normalized={baseline_pct:.1f}% ({int(baseline_norm)}/{baseline_total})")

    # Run each optimizer
    optimizers = [args.optimizer] if args.optimizer else ["SIMBA", "GEPA", "BootstrapRS", "MIPROv2"]
    all_results = {
        "baseline": {
            "name": "Baseline (unoptimized)",
            "normalized_pct": baseline_pct,
            "normalized_hits": int(baseline_norm),
            "exact_pct": baseline_exact / baseline_total * 100,
            "total": baseline_total,
        }
    }

    for opt_name in optimizers:
        opt_key = opt_name.lower()
        result_path = OUT_DIR / f"{opt_key}_results.json"
        compiled_path = str(OUT_DIR / f"compiled_{opt_key}.json")

        if args.skip_compile and result_path.exists():
            print(f"\n[{opt_name}] Loading cached results...")
            with open(result_path) as f:
                opt_data = json.load(f)
            opt_examples = opt_data["per_example"]
            compile_time = opt_data.get("compile_time_s", 0)
            eval_time = opt_data.get("eval_time_s", 0)
        else:
            # Fresh module for each optimizer
            module = TranslatorModule(num_context_passages=5, use_postprocessor=True)
            try:
                compiled, compile_time = run_optimizer(opt_name, enriched_trainset, eval_examples, module, lm)
            except Exception as e:
                print(f"\n[{opt_name}] FAILED: {e}")
                import traceback
                traceback.print_exc()
                all_results[opt_key] = {
                    "name": opt_name,
                    "error": str(e),
                    "normalized_pct": 0,
                    "normalized_hits": 0,
                    "exact_pct": 0,
                    "total": baseline_total,
                }
                continue

            # Save compiled program
            try:
                save_compiled_program(compiled, compiled_path)
            except Exception as e:
                print(f"[{opt_name}] Warning: Could not save compiled program: {e}")

            # Evaluate
            print(f"[{opt_name}] Evaluating on {len(eval_examples)} examples...")
            eval_start = time.time()
            opt_examples = evaluate_on_set(compiled, eval_examples)
            eval_time = time.time() - eval_start
            print(f"[{opt_name}] Eval time: {eval_time:.1f}s")

            # Save results
            opt_data = {
                "optimizer": opt_name,
                "model": "deepseek-ai/DeepSeek-V4-Flash",
                "num_context_passages": 5,
                "use_postprocessor": True,
                "per_example": opt_examples,
                "compile_time_s": round(compile_time, 2),
                "eval_time_s": round(eval_time, 2),
            }
            with open(result_path, "w") as f:
                json.dump(opt_data, f, indent=2, ensure_ascii=False)

        opt_norm = sum(e["normalized_match"] for e in opt_examples)
        opt_exact = sum(e["exact_match"] for e in opt_examples)
        opt_total = len(opt_examples)
        opt_pct = opt_norm / opt_total * 100
        opt_exact_pct = opt_exact / opt_total * 100
        delta = opt_pct - baseline_pct
        print(f"  {opt_name}: normalized={opt_pct:.1f}% ({int(opt_norm)}/{opt_total}), "
              f"exact={opt_exact_pct:.1f}% ({int(opt_exact)}/{opt_total}), "
              f"Δ={delta:+.1f}pp vs baseline")

        all_results[opt_key] = {
            "name": opt_name,
            "normalized_pct": round(opt_pct, 1),
            "normalized_hits": int(opt_norm),
            "exact_pct": round(opt_exact_pct, 1),
            "exact_hits": int(opt_exact),
            "total": opt_total,
            "compile_time_s": compile_time if not isinstance(compile_time, float) else round(compile_time, 2),
            "eval_time_s": round(eval_time, 2) if isinstance(eval_time, float) else eval_time,
            "delta_vs_baseline_pp": round(delta, 1),
        }

    # ── Print comparison table ─────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("COMPARISON TABLE (En→Mir direction)")
    print("=" * 70)
    print(f"{'Optimizer':<20} {'Norm%':>7} {'Ex%':>7} {'Hits':>5} {'Δpp':>6} {'Time(s)':>8}")
    print("-" * 70)

    for key, data in all_results.items():
        name = data["name"]
        norm = data["normalized_pct"]
        exact = data["exact_pct"]
        hits = data["normalized_hits"]
        delta = data.get("delta_vs_baseline_pp", 0)
        ctime = data.get("compile_time_s", 0)
        print(f"  {name:<18} {norm:>6.1f}% {exact:>6.1f}% {hits:>5} {delta:>+5.1f} {ctime:>8.1f}")

    # ── Save comparison summary ────────────────────────────────────────────
    summary_path = OUT_DIR / "comparison_summary.json"
    summary = {
        "task": "Optimizer comparison: SIMBA vs GEPA vs BootstrapRS vs MIPROv2",
        "direction": "en_to_mir",
        "model": "deepseek-ai/DeepSeek-V4-Flash",
        "train_size": len(trainset),
        "eval_size": len(eval_examples),
        "baseline": all_results["baseline"],
        "optimizers": {k: v for k, v in all_results.items() if k != "baseline"},
        "recommendation": "",
    }

    # Determine best optimizer
    valid_results = {k: v for k, v in all_results.items()
                     if "error" not in v and k != "baseline"}
    if valid_results:
        best_key = max(valid_results, key=lambda k: valid_results[k]["normalized_pct"])
        best = valid_results[best_key]
        summary["recommendation"] = (
            f"Best optimizer: {best['name']} at {best['normalized_pct']}% normalized match "
            f"(+{best['delta_vs_baseline_pp']}pp vs baseline). "
            f"Recommend running {best['name']} with heavier configs (more candidates, rounds, "
            f"or auto=medium/heavy) as the next step."
        )
    else:
        summary["recommendation"] = "All optimizers failed. Check error logs."

    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\nSummary saved to {summary_path}")
    print(f"\n{summary['recommendation']}")

    return summary


if __name__ == "__main__":
    main()