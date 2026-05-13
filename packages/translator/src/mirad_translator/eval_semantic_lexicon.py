"""Evaluate semantic lexicon lookup vs. exact-match lookup on the translation task.

Compares the pre-compiled DSPy program (BootstrapFewShot) with two configurations:
1. EXACT: MiradLexiconLookup (original exact match)
2. SEMANTIC: MiradSemanticLexiconLookup (top-k semantic neighbors)

Both use the SAME compiled program — we only swap the lexicon_lookup module.
The evaluation set excludes examples that appear in the compiled program's few-shot demos.

Usage:
    python -m mirad_translator.eval_semantic_lexicon
"""
import csv
import json
import time
import os
import sys
from pathlib import Path
from typing import Optional

import dspy

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
EVAL_CSV_PATH = _PROJECT_ROOT / "data" / "phrases" / "english-mirad-sentence-pairs.csv"
COMPILED_PROGRAM_PATH = _PROJECT_ROOT / "data" / "eval_results" / "optimizer_comparison" / "compiled_bootstrap_fast_program" / "program.pkl"
RESULTS_DIR = _PROJECT_ROOT / "data" / "eval_results"

# ── Exclusion set: demo texts from the compiled program ───────────────────────

def get_demo_texts(compiled_program) -> set[str]:
    """Extract all english_text values from the compiled program's demos."""
    demo_texts = set()
    for name, pred in compiled_program.named_predictors():
        for demo in pred.demos:
            if "english_text" in demo:
                demo_texts.add(demo["english_text"].strip())
    return demo_texts


# ── Dataset loading ────────────────────────────────────────────────────────────

def load_eval_set(csv_path: Optional[str] = None, exclude_texts: Optional[set] = None) -> list[dict]:
    """Load the evaluation CSV, optionally excluding demo texts."""
    path = Path(csv_path or EVAL_CSV_PATH)
    if not path.exists():
        raise FileNotFoundError(f"Evaluation CSV not found: {path}")

    examples = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Handle both uppercase and lowercase column names
            english = row.get("English", row.get("english", "")).strip()
            mirad = row.get("Mirad", row.get("mirad", "")).strip()
            if english and mirad:
                examples.append({"english": english, "mirad": mirad})

    if exclude_texts:
        before = len(examples)
        examples = [ex for ex in examples if ex["english"] not in exclude_texts]
        after = len(examples)
        print(f"[load_eval_set] Excluded {before - after} demo examples, {after} remain")

    return examples


# ── Metrics ─────────────────────────────────────────────────────────────────────

def normalize(text: str) -> str:
    """Normalize text for comparison."""
    import re
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    return text


def strip_punct(s: str) -> str:
    import re
    s = re.sub(r'[.,!?;:()"\'][\[\]{}]', "", s)
    return re.sub(r"\s+", " ", s).strip()


def normalized_match(gold: str, pred: str) -> bool:
    return strip_punct(normalize(gold)) == strip_punct(normalize(pred))


def exact_match(gold: str, pred: str) -> bool:
    return normalize(gold) == normalize(pred)


# ── Main evaluation ─────────────────────────────────────────────────────────────

def run_semantic_eval(
    n_samples: int = 100,
    top_k: int = 5,
    min_similarity: float = 0.35,
    max_total_pairs: int = 50,
    seed: int = 42,
    model: str = "deepseek-ai/DeepSeek-V4-Flash",
):
    """Run the evaluation comparing exact-match vs. semantic lexicon lookup."""
    import cloudpickle
    from dotenv import load_dotenv
    from mirad_translator.translate import MiradLexiconLookup, MiradContextRetrieve, _format_word_equivalents, _format_context_passages, TranslatorModule
    from mirad_translator.semantic_lexicon import MiradSemanticLexiconLookup

    load_dotenv(_PROJECT_ROOT / ".env")

    # ── Load compiled program ──────────────────────────────────────────────
    print(f"[eval] Loading compiled program from {COMPILED_PROGRAM_PATH}")
    with open(COMPILED_PROGRAM_PATH, "rb") as f:
        compiled = cloudpickle.load(f)

    # ── Get demo texts for exclusion ────────────────────────────────────────
    demo_texts = get_demo_texts(compiled)
    print(f"[eval] Excluding {len(demo_texts)} demo texts from evaluation")

    # ── Load eval set, excluding demos ──────────────────────────────────────
    all_examples = load_eval_set(exclude_texts=demo_texts)
    print(f"[eval] Total eval examples (after exclusion): {len(all_examples)}")

    # Sample N examples
    import random
    rng = random.Random(seed)
    if n_samples < len(all_examples):
        examples = rng.sample(all_examples, n_samples)
    else:
        examples = all_examples
    print(f"[eval] Evaluating on {len(examples)} examples")

    # ── Configure LM ───────────────────────────────────────────────────────
    api_key = os.environ.get("DEEPINFRA_API_KEY")
    api_base = os.environ.get("DEEPINFRA_BASE_URL", "https://api.deepinfra.com/v1/openai")
    lm = dspy.LM(model=f"openai/{model}", api_key=api_key, api_base=api_base)
    dspy.settings.configure(lm=lm)

    # ── Evaluate with EXACT lookup (baseline) ───────────────────────────────
    print("\n[eval] === EXACT lexicon lookup (baseline) ===")
    exact_module = TranslatorModule(db_path=None, num_context_passages=5, use_postprocessor=True)

    exact_results = []
    exact_start = time.time()
    for i, ex in enumerate(examples):
        pred = exact_module(english_text=ex["english"])
        nm = normalized_match(ex["mirad"], pred.mirad_text)
        em = exact_match(ex["mirad"], pred.mirad_text)
        exact_results.append({
            "english": ex["english"],
            "gold_mirad": ex["mirad"],
            "predicted_mirad": pred.mirad_text,
            "normalized_match": nm,
            "exact_match": em,
            "word_equivalents": pred.word_equivalents if hasattr(pred, "word_equivalents") else {},
        })
        if (i + 1) % 10 == 0:
            print(f"  [{i+1}/{len(examples)}] norm={sum(r['normalized_match'] for r in exact_results)/(i+1)*100:.1f}%")
    exact_time = time.time() - exact_start

    exact_norm = sum(1 for r in exact_results if r["normalized_match"]) / len(exact_results) * 100
    exact_exact = sum(1 for r in exact_results if r["exact_match"]) / len(exact_results) * 100

    print(f"\n  EXACT: norm={exact_norm:.1f}%  exact={exact_exact:.1f}%  time={exact_time:.1f}s")

    # ── Evaluate with SEMANTIC lookup ───────────────────────────────────────
    print("\n[eval] === SEMANTIC lexicon lookup (top_k={top_k}, min_sim={min_similarity}) ===")

    # Create a TranslatorModule that uses semantic lookup
    # We build a fresh module and swap the lexicon_lookup submodule
    semantic_module = TranslatorModule(db_path=None, num_context_passages=5, use_postprocessor=True)
    semantic_module.lexicon_lookup = MiradSemanticLexiconLookup(
        db_path=None,
        top_k_per_word=top_k,
        max_total_pairs=max_total_pairs,
        min_similarity=min_similarity,
    )

    semantic_results = []
    semantic_start = time.time()
    for i, ex in enumerate(examples):
        pred = semantic_module(english_text=ex["english"])
        nm = normalized_match(ex["mirad"], pred.mirad_text)
        em = exact_match(ex["mirad"], pred.mirad_text)
        semantic_results.append({
            "english": ex["english"],
            "gold_mirad": ex["mirad"],
            "predicted_mirad": pred.mirad_text,
            "normalized_match": nm,
            "exact_match": em,
            "word_equivalents": pred.word_equivalents if hasattr(pred, "word_equivalents") else {},
        })
        if (i + 1) % 10 == 0:
            print(f"  [{i+1}/{len(examples)}] norm={sum(r['normalized_match'] for r in semantic_results)/(i+1)*100:.1f}%")
    semantic_time = time.time() - semantic_start

    semantic_norm = sum(1 for r in semantic_results if r["normalized_match"]) / len(semantic_results) * 100
    semantic_exact = sum(1 for r in semantic_results if r["exact_match"]) / len(semantic_results) * 100

    print(f"\n  SEMANTIC: norm={semantic_norm:.1f}%  exact={semantic_exact:.1f}%  time={semantic_time:.1f}s")

    # ── Evaluate with COMPILED program (uses original exact lookup internally) ─
    print("\n[eval] === COMPILED program (BootstrapFewShot) ===")

    compiled_results = []
    compiled_start = time.time()
    for i, ex in enumerate(examples):
        pred = compiled(english_text=ex["english"])

        # Handle postprocessing (compiled program doesn't have use_postprocessor)
        from mirad_translator.postprocess import postprocess_mirad
        mirad_text = postprocess_mirad(pred.mirad_text)

        nm = normalized_match(ex["mirad"], mirad_text)
        em = exact_match(ex["mirad"], mirad_text)
        compiled_results.append({
            "english": ex["english"],
            "gold_mirad": ex["mirad"],
            "predicted_mirad": mirad_text,
            "normalized_match": nm,
            "exact_match": em,
        })
        if (i + 1) % 10 == 0:
            print(f"  [{i+1}/{len(examples)}] norm={sum(r['normalized_match'] for r in compiled_results)/(i+1)*100:.1f}%")
    compiled_time = time.time() - compiled_start

    compiled_norm = sum(1 for r in compiled_results if r["normalized_match"]) / len(compiled_results) * 100
    compiled_exact = sum(1 for r in compiled_results if r["exact_match"]) / len(compiled_results) * 100

    print(f"\n  COMPILED: norm={compiled_norm:.1f}%  exact={compiled_exact:.1f}%  time={compiled_time:.1f}s")

    # ── Compare ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("COMPARISON RESULTS")
    print("=" * 70)
    print(f"  Eval samples:     {len(examples)}")
    print(f"  Demo-excluded:    {len(demo_texts)} texts")
    print(f"  Top-K per word:   {top_k}")
    print(f"  Min similarity:    {min_similarity}")
    print(f"  Max total pairs:  {max_total_pairs}")
    print()
    print(f"  {'Method':<25} {'Norm Match':>12} {'Exact Match':>12} {'Time (s)':>10}")
    print(f"  {'-'*25} {'-'*12} {'-'*12} {'-'*10}")
    print(f"  {'EXACT (baseline)':<25} {exact_norm:>11.1f}% {exact_exact:>11.1f}% {exact_time:>9.1f}s")
    print(f"  {'SEMANTIC (k=' + str(top_k) + ')':<25} {semantic_norm:>11.1f}% {semantic_exact:>11.1f}% {semantic_time:>9.1f}s")
    print(f"  {'COMPILED (BootstrapFast)':<25} {compiled_norm:>11.1f}% {compiled_exact:>11.1f}% {compiled_time:>9.1f}s")
    print()

    # ── Compute per-example delta ───────────────────────────────────────────
    print("PER-EXAMPLE ANALYSIS:")
    semantic_wins = 0
    exact_wins = 0
    both_right = 0
    both_wrong = 0
    for er, sr in zip(exact_results, semantic_results):
        e_nm = er["normalized_match"]
        s_nm = sr["normalized_match"]
        if s_nm and not e_nm:
            semantic_wins += 1
        elif e_nm and not s_nm:
            exact_wins += 1
        elif e_nm and s_nm:
            both_right += 1
        else:
            both_wrong += 1

    print(f"  Both correct:        {both_right}")
    print(f"  Semantic wins:       {semantic_wins}")
    print(f"  Exact wins:          {exact_wins}")
    print(f"  Both wrong:          {both_wrong}")

    # ── Show examples where semantic wins ──────────────────────────────────
    if semantic_wins > 0:
        print("\nEXAMPLES WHERE SEMANTIC WINS:")
        for er, sr in zip(exact_results, semantic_results):
            if sr["normalized_match"] and not er["normalized_match"]:
                print(f"  EN: {er['english'][:80]}")
                print(f"    GOLD:   {er['gold_mirad'][:80]}")
                print(f"    EXACT:  {er['predicted_mirad'][:80]}")
                print(f"    SEM:    {sr['predicted_mirad'][:80]}")
                print()

    # ── Save results ────────────────────────────────────────────────────────
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    comparison = {
        "method": "semantic_vs_exact_lexicon",
        "n_samples": len(examples),
        "n_excluded_demos": len(demo_texts),
        "top_k_per_word": top_k,
        "min_similarity": min_similarity,
        "max_total_pairs": max_total_pairs,
        "seed": seed,
        "model": model,
        "exact_lookup": {
            "normalized_match_pct": round(exact_norm, 1),
            "exact_match_pct": round(exact_exact, 1),
            "time_s": round(exact_time, 1),
        },
        "semantic_lookup": {
            "normalized_match_pct": round(semantic_norm, 1),
            "exact_match_pct": round(semantic_exact, 1),
            "time_s": round(semantic_time, 1),
        },
        "compiled_program": {
            "normalized_match_pct": round(compiled_norm, 1),
            "exact_match_pct": round(compiled_exact, 1),
            "time_s": round(compiled_time, 1),
        },
        "per_example_delta": {
            "both_correct": both_right,
            "semantic_wins": semantic_wins,
            "exact_wins": exact_wins,
            "both_wrong": both_wrong,
        },
    }

    out_path = RESULTS_DIR / "semantic_lexicon_comparison.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)

    # Save per-example results for deeper analysis
    for results, label in [
        (exact_results, "exact"),
        (semantic_results, "semantic"),
        (compiled_results, "compiled"),
    ]:
        per_path = RESULTS_DIR / f"semantic_lexicon_comparison_{label}_per_example.json"
        with open(per_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to:")
    print(f"  {out_path}")
    print(f"  {RESULTS_DIR / 'semantic_lexicon_comparison_*_per_example.json'}")
    return comparison


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate semantic lexicon lookup vs. exact match")
    parser.add_argument("--n-samples", type=int, default=100, help="Number of samples to evaluate")
    parser.add_argument("--top-k", type=int, default=5, help="Top-k semantic neighbors per word")
    parser.add_argument("--min-similarity", type=float, default=0.35, help="Minimum cosine similarity")
    parser.add_argument("--max-total-pairs", type=int, default=50, help="Max total word equivalent pairs")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for sampling")
    parser.add_argument("--model", type=str, default="deepseek-ai/DeepSeek-V4-Flash", help="LM model name")
    args = parser.parse_args()

    run_semantic_eval(
        n_samples=args.n_samples,
        top_k=args.top_k,
        min_similarity=args.min_similarity,
        max_total_pairs=args.max_total_pairs,
        seed=args.seed,
        model=args.model,
    )