"""Evaluate semantic lexicon lookup vs. exact-match vs. compiled program.

Compares three configurations:
1. EXACT: TranslatorModule with MiradLexiconLookup (original exact match)
2. SEMANTIC: TranslatorModule with MiradSemanticLexiconLookup (k=3, sim≥0.5)
3. COMPILED: Pre-compiled BootstrapFewShot program (uses exact lookup internally)

All on the same sample set, excluding demo texts from the compiled program.

Usage:
    python run_semantic_eval.py [--n-samples 100] [--top-k 3] [--min-similarity 0.5] [--skip-compiled]
"""
import argparse
import csv
import json
import os
import random
import re
import time
from pathlib import Path

import dspy

_PROJECT_ROOT = Path("/mnt/s/projects/Project_earthlingish/Mirad-phonemes-engine")
EVAL_CSV_PATH = _PROJECT_ROOT / "data" / "phrases" / "english-mirad-sentence-pairs.csv"
COMPILED_PROGRAM_PATH = _PROJECT_ROOT / "data" / "eval_results" / "optimizer_comparison" / "compiled_bootstrap_fast_program" / "program.pkl"
RESULTS_DIR = _PROJECT_ROOT / "data" / "eval_results"


def normalize(text):
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    return text


def strip_punct(s):
    s = re.sub(r'[.,!?;:()"\'][\[\]{}]', "", s)
    return re.sub(r"\s+", " ", s).strip()


def normalized_match(gold, pred):
    return strip_punct(normalize(gold)) == strip_punct(normalize(pred))


def get_demo_texts():
    """Extract demo texts from the compiled program to exclude from eval."""
    import cloudpickle
    with open(COMPILED_PROGRAM_PATH, "rb") as f:
        compiled = cloudpickle.load(f)
    demo_texts = set()
    for name, pred in compiled.named_predictors():
        for demo in pred.demos:
            if "english_text" in demo:
                demo_texts.add(demo["english_text"].strip())
    return demo_texts, compiled


def load_eval_set(csv_path=None, exclude_texts=None):
    path = Path(csv_path or EVAL_CSV_PATH)
    if not path.exists():
        raise FileNotFoundError(f"Evaluation CSV not found: {path}")
    examples = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            english = row.get("English", row.get("english", "")).strip()
            mirad = row.get("Mirad", row.get("mirad", "")).strip()
            if english and mirad:
                examples.append({"english": english, "mirad": mirad})
    if exclude_texts:
        before = len(examples)
        examples = [ex for ex in examples if ex["english"] not in exclude_texts]
        print(f"  Excluded {before - len(examples)} demo examples, {len(examples)} remain")
    return examples


def evaluate_method(module, examples, label, use_postprocessor=True):
    """Run evaluation on a module and return per-example results."""
    from mirad_translator.postprocess import postprocess_mirad
    results = []
    start = time.time()
    for i, ex in enumerate(examples):
        pred = module(english_text=ex["english"])
        mirad_text = pred.mirad_text
        if use_postprocessor:
            mirad_text = postprocess_mirad(mirad_text)
        nm = normalized_match(ex["mirad"], mirad_text)
        em = normalize(ex["mirad"]) == normalize(mirad_text)
        we = pred.word_equivalents if hasattr(pred, "word_equivalents") and pred.word_equivalents else {}
        results.append({
            "english": ex["english"],
            "gold_mirad": ex["mirad"],
            "predicted_mirad": mirad_text,
            "normalized_match": nm,
            "exact_match": em,
            "word_equivalents_count": len(we),
            "method": label,
        })
        if (i + 1) % 10 == 0 or i == 0:
            pct = sum(r["normalized_match"] for r in results) / len(results) * 100
            print(f"  [{label}][{i+1}/{len(examples)}] norm={pct:.1f}%  elapsed={time.time()-start:.0f}s")
    elapsed = time.time() - start
    return results, elapsed


def main():
    from dotenv import load_dotenv
    load_dotenv(_PROJECT_ROOT / ".env")

    parser = argparse.ArgumentParser(description="Evaluate semantic lexicon lookup")
    parser.add_argument("--n-samples", type=int, default=100)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--min-similarity", type=float, default=0.5)
    parser.add_argument("--max-total-pairs", type=int, default=30)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--model", type=str, default="deepseek-ai/DeepSeek-V4-Flash")
    parser.add_argument("--skip-compiled", action="store_true")
    args = parser.parse_args()

    # ── Get demo texts for exclusion ──────────────────────────────────────────
    print("[1/6] Loading compiled program to extract demo texts...")
    demo_texts, compiled = get_demo_texts()
    print(f"  Excluding {len(demo_texts)} demo texts")

    # ── Load eval set ────────────────────────────────────────────────────────
    print("[2/6] Loading evaluation dataset...")
    examples = load_eval_set(exclude_texts=demo_texts)
    rng = random.Random(args.seed)
    if args.n_samples < len(examples):
        examples = rng.sample(examples, args.n_samples)
    print(f"  Evaluating on {len(examples)} examples")

    # ── Configure LM ─────────────────────────────────────────────────────────
    api_key = os.environ.get("DEEPINFRA_API_KEY")
    api_base = os.environ.get("DEEPINFRA_BASE_URL", "https://api.deepinfra.com/v1/openai")
    lm = dspy.LM(model=f"openai/{args.model}", api_key=api_key, api_base=api_base)
    dspy.settings.configure(lm=lm)

    # ── EXACT lookup ──────────────────────────────────────────────────────────
    print("[3/6] EXACT lexicon lookup (baseline)...")
    from mirad_translator.translate import TranslatorModule
    exact_module = TranslatorModule(db_path=None, num_context_passages=5, use_postprocessor=True)
    exact_results, exact_time = evaluate_method(exact_module, examples, "EXACT")
    exact_norm = sum(1 for r in exact_results if r["normalized_match"]) / len(exact_results) * 100
    exact_exact = sum(1 for r in exact_results if r["exact_match"]) / len(exact_results) * 100
    exact_avg_we = sum(r["word_equivalents_count"] for r in exact_results) / len(exact_results)
    print(f"  EXACT: norm={exact_norm:.1f}%  exact={exact_exact:.1f}%  avg_we={exact_avg_we:.1f}  time={exact_time:.0f}s")

    # ── SEMANTIC lookup ────────────────────────────────────────────────────────
    print(f"[4/6] SEMANTIC lexicon lookup (k={args.top_k}, sim≥{args.min_similarity})...")
    from mirad_translator.semantic_lexicon import MiradSemanticLexiconLookup
    semantic_module = TranslatorModule(db_path=None, num_context_passages=5, use_postprocessor=True)
    semantic_module.lexicon_lookup = MiradSemanticLexiconLookup(
        db_path=None, top_k_per_word=args.top_k, max_total_pairs=args.max_total_pairs, min_similarity=args.min_similarity,
    )
    semantic_results, semantic_time = evaluate_method(semantic_module, examples, "SEMANTIC")
    semantic_norm = sum(1 for r in semantic_results if r["normalized_match"]) / len(semantic_results) * 100
    semantic_exact = sum(1 for r in semantic_results if r["exact_match"]) / len(semantic_results) * 100
    semantic_avg_we = sum(r["word_equivalents_count"] for r in semantic_results) / len(semantic_results)
    print(f"  SEMANTIC: norm={semantic_norm:.1f}%  exact={semantic_exact:.1f}%  avg_we={semantic_avg_we:.1f}  time={semantic_time:.0f}s")

    # ── COMPILED program ──────────────────────────────────────────────────────
    compiled_results = None
    compiled_time = None
    if not args.skip_compiled:
        print("[5/6] COMPILED program (BootstrapFewShot with exact lookup)...")
        compiled_results, compiled_time = evaluate_method(compiled, examples, "COMPILED")
        compiled_norm = sum(1 for r in compiled_results if r["normalized_match"]) / len(compiled_results) * 100
        compiled_exact = sum(1 for r in compiled_results if r["exact_match"]) / len(compiled_results) * 100
        compiled_avg_we = sum(r["word_equivalents_count"] for r in compiled_results) / len(compiled_results)
        print(f"  COMPILED: norm={compiled_norm:.1f}%  exact={compiled_exact:.1f}%  avg_we={compiled_avg_we:.1f}  time={compiled_time:.0f}s")
    else:
        print("[5/6] Skipping compiled program evaluation (--skip-compiled)")

    # ── Pairwise comparisons ──────────────────────────────────────────────────
    print("[6/6] Computing pairwise comparisons...")

    def compare(r1, r2, n1, n2):
        d = {"both_correct": 0, f"{n1}_wins": 0, f"{n2}_wins": 0, "both_wrong": 0,
             f"punct_only_{n1}": 0, f"punct_only_{n2}": 0}
        for a, b in zip(r1, r2):
            a_nm, b_nm = a["normalized_match"], b["normalized_match"]
            if a_nm and not b_nm:
                d[f"{n1}_wins"] += 1
                if strip_punct(a["predicted_mirad"]) == strip_punct(a["gold_mirad"]):
                    d[f"punct_only_{n1}"] += 1
            elif b_nm and not a_nm:
                d[f"{n2}_wins"] += 1
                if strip_punct(b["predicted_mirad"]) == strip_punct(b["gold_mirad"]):
                    d[f"punct_only_{n2}"] += 1
            elif a_nm and b_nm:
                d["both_correct"] += 1
            else:
                d["both_wrong"] += 1
        d["substantive_delta"] = d[f"{n2}_wins"] - d[f"{n1}_wins"] + d[f"punct_only_{n1}"] - d[f"punct_only_{n2}"]
        return d

    es = compare(exact_results, semantic_results, "exact", "semantic")
    ec = compare(exact_results, compiled_results, "exact", "compiled") if compiled_results else None
    cs = compare(compiled_results, semantic_results, "compiled", "semantic") if compiled_results else None

    # ── Summary ──────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("SEMANTIC LEXICON EVALUATION RESULTS")
    print("=" * 70)
    print(f"  Eval samples:     {len(examples)}")
    print(f"  Demo-excluded:    {len(demo_texts)} texts")
    print(f"  Model:            {args.model}")
    print(f"  Top-K per word:   {args.top_k}")
    print(f"  Min similarity:   {args.min_similarity}")
    print(f"  Max total pairs: {args.max_total_pairs}")
    print()
    print(f"  {'Method':<30} {'Norm%':>8} {'Exact%':>8} {'Avg WE':>8} {'Time':>8}")
    print(f"  {'-'*30} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
    print(f"  {'EXACT (baseline)':<30} {exact_norm:>7.1f}% {exact_exact:>7.1f}% {exact_avg_we:>7.1f} {exact_time:>7.0f}s")
    print(f"  {'SEMANTIC (k=' + str(args.top_k) + ', sim=' + str(args.min_similarity) + ')':<30} {semantic_norm:>7.1f}% {semantic_exact:>7.1f}% {semantic_avg_we:>7.1f} {semantic_time:>7.0f}s")
    if compiled_results:
        print(f"  {'COMPILED (BootstrapFast)':<30} {compiled_norm:>7.1f}% {compiled_exact:>7.1f}% {compiled_avg_we:>7.1f} {compiled_time:>7.0f}s")
    print()
    for label, delta in [("Exact vs Semantic", es), ("Exact vs Compiled", ec), ("Compiled vs Semantic", cs)]:
        if delta is None:
            continue
        print(f"  {label}:")
        print(f"    Both correct:    {delta['both_correct']}")
        n1 = label.split(" vs ")[0].lower().replace(" ", "_")
        n2 = label.split(" vs ")[1].lower().replace(" ", "_")
        print(f"    {n1.title()} wins:    {delta[f'{n1}_wins']} (punct-only: {delta[f'punct_only_{n1}']})")
        print(f"    {n2.title()} wins:    {delta[f'{n2}_wins']} (punct-only: {delta[f'punct_only_{n2}']})")
        print(f"    Both wrong:       {delta['both_wrong']}")
        print(f"    Substantive Δ:    {delta['substantive_delta']:+d}")
        print()

    # ── Show semantic wins ────────────────────────────────────────────────────
    print("=== EXAMPLES WHERE SEMANTIC WINS OVER EXACT ===")
    for e, s in zip(exact_results, semantic_results):
        if s["normalized_match"] and not e["normalized_match"]:
            is_substantive = strip_punct(e["predicted_mirad"]) != strip_punct(e["gold_mirad"])
            print(f"  EN: {e['english'][:80]}")
            print(f"  GOLD:  {e['gold_mirad'][:80]}")
            print(f"  EXACT({e['word_equivalents_count']} WE): {e['predicted_mirad'][:80]}")
            print(f"  SEM({s['word_equivalents_count']} WE):   {s['predicted_mirad'][:80]}")
            print(f"  Substantive: {is_substantive}")
            print()

    # ── Save ──────────────────────────────────────────────────────────────────
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    comparison = {
        "method": "semantic_vs_exact_compiled",
        "n_samples": len(examples), "n_excluded_demos": len(demo_texts),
        "top_k_per_word": args.top_k, "min_similarity": args.min_similarity,
        "max_total_pairs": args.max_total_pairs, "seed": args.seed, "model": args.model,
        "exact_lookup": {"normalized_match_pct": round(exact_norm, 1), "exact_match_pct": round(exact_exact, 1),
                         "avg_word_equivalents": round(exact_avg_we, 1), "time_s": round(exact_time, 1)},
        "semantic_lookup": {"normalized_match_pct": round(semantic_norm, 1), "exact_match_pct": round(semantic_exact, 1),
                            "avg_word_equivalents": round(semantic_avg_we, 1), "time_s": round(semantic_time, 1)},
    }
    if compiled_results:
        comparison["compiled_program"] = {"normalized_match_pct": round(compiled_norm, 1), "exact_match_pct": round(compiled_exact, 1),
                                            "avg_word_equivalents": round(compiled_avg_we, 1), "time_s": round(compiled_time, 1)}
    comparison["exact_vs_semantic"] = es
    if ec: comparison["exact_vs_compiled"] = ec
    if cs: comparison["compiled_vs_semantic"] = cs

    out_path = RESULTS_DIR / "semantic_lexicon_comparison.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)
    for results, label in [(exact_results, "exact"), (semantic_results, "semantic")]:
        with open(RESULTS_DIR / f"semantic_lexicon_comparison_{label}_per_example.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    if compiled_results:
        with open(RESULTS_DIR / "semantic_lexicon_comparison_compiled_per_example.json", "w", encoding="utf-8") as f:
            json.dump(compiled_results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()