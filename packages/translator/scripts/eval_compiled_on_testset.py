#!/usr/bin/env python3
"""
Evaluate a compiled MIPROv2 program on the full hold-out test set.

Loads the compiled MultiCandidateTranslator from program.pkl produced by
run_mipro_optimization.py and runs evaluation on data/eval/test.json
with 24 parallel threads. Reports normalized match, exact match, and avg judge score.

Usage:
    python eval_compiled_on_testset.py \
        --program data/eval_results/mipro_full_660/program.pkl \
        --test data/eval/test.json \
        --num-threads 24
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "translator" / "src"))

load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=True)

import dspy

from mirad_translator.multi_candidate import (
    MultiCandidateTranslator,
    _make_lm,
    _rerank_verified_candidates,
    CandidateSetVerifier,
)
from mirad_translator.evaluate import normalized_match_metric


def load_test_pairs(json_path: Path) -> list[dict]:
    """Load test pairs from JSON, normalizing to english_text/mirad_text keys."""
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    pairs = data.get("pairs", []) if isinstance(data, dict) else data
    result = []
    for i, p in enumerate(pairs):
        english = p.get("english_text", p.get("english", ""))
        mirad = p.get("mirad_text", p.get("mirad", ""))
        if not english or not mirad:
            continue
        result.append({
            "id": p.get("id", f"pair-{i}"),
            "english_text": english.strip(),
            "mirad_text": mirad.strip(),
        })
    return result


def strip_punct(s: str) -> str:
    s = re.sub(r'[.,!?;:()"\'\[\]{}]', "", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def eval_one(
    pair: dict,
    compiled: dspy.Module,
) -> dict:
    """Evaluate a single test pair using the compiled program."""
    try:
        pred = compiled(english_text=pair["english_text"])
        mirad_pred = str(getattr(pred, "mirad_text", ""))

        gold_norm = strip_punct(pair["mirad_text"])
        pred_norm = strip_punct(mirad_pred)
        nm = gold_norm == pred_norm
        em = pair["mirad_text"].strip() == mirad_pred.strip()

        winner_score = float(getattr(pred, "total_score", 0.0))
        candidates_data = getattr(pred, "candidates", [])

        cand_summaries = []
        for c in (candidates_data or []):
            j = c.get("judge", {})
            cand_summaries.append({
                "candidate_id": c.get("candidate_id"),
                "rank": c.get("rank"),
                "winner": c.get("winner", False),
                "temp": c.get("temperature"),
                "mirad": c.get("mirad_text"),
                "total_score": j.get("total_score", 0),
                "semantic_fidelity": j.get("semantic_fidelity", 0),
                "grammar": j.get("grammar_score", 0),
                "morphology": j.get("morphology_score", 0),
                "rule_hard_failures": c.get("rule_precheck", {}).get("hard_failures", []),
                "rule_soft_errors": c.get("rule_precheck", {}).get("soft_errors", []),
                "verifier_hard_failures": c.get("verifier", {}).get("hard_failures", []),
                "verifier_soft_errors": c.get("verifier", {}).get("verifier_soft_errors", []),
                "weighted_score": c.get("verifier", {}).get("weighted_score", 0),
                "rationale": j.get("rationale", ""),
            })

        return {
            "id": pair.get("id", ""),
            "english_text": pair["english_text"],
            "gold": pair["mirad_text"],
            "pred": mirad_pred,
            "normalized_match": bool(nm),
            "exact_match": bool(em),
            "judge_score": winner_score,
            "winner_index": int(getattr(pred, "winner_index", 0)),
            "rationale": getattr(pred, "rationale", ""),
            "candidates": cand_summaries,
            "error": None,
        }
    except Exception as exc:
        return {
            "id": pair.get("id", ""),
            "english_text": pair["english_text"],
            "gold": pair["mirad_text"],
            "pred": "ERROR",
            "normalized_match": False,
            "exact_match": False,
            "judge_score": 0.0,
            "candidates": [],
            "error": str(exc),
        }


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate compiled MIPROv2 program on test set"
    )
    parser.add_argument(
        "--program",
        type=Path,
        default=PROJECT_ROOT / "data" / "eval_results" / "mipro_full_660" / "program.pkl",
        help="Path to compiled program.pkl",
    )
    parser.add_argument(
        "--test",
        type=Path,
        default=PROJECT_ROOT / "data" / "eval" / "test.json",
        help="Path to test set JSON",
    )
    parser.add_argument(
        "--num-threads",
        type=int,
        default=24,
        help="Number of parallel threads (default: 24)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory for results (default: same as program dir)",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir) if args.out_dir else args.program.parent

    # ── Configure LM ─────────────────────────────────────────────────────
    print("[LM] Configuring DeepInfra LM...")
    lm = _make_lm(0.4)
    dspy.settings.configure(lm=lm)
    print(f"[LM] Configured: {lm.model if hasattr(lm, 'model') else 'openai/deepseek-ai/DeepSeek-V4-Flash'}")

    # ── Load compiled program ────────────────────────────────────────────
    print(f"\n[LOAD] Loading compiled program from {args.program}...")

    # First, read the pickle to extract metadata about original config
    import cloudpickle as _cp
    with open(args.program, "rb") as f:
        _saved_state = _cp.load(f)

    n_candidates = 3
    temps = [0.1, 0.4, 0.8]
    ctx_passages = 3

    print(f"[LOAD] Reconstructing with num_candidates={n_candidates}, temperatures={temps}, num_context_passages={ctx_passages}")

    compiled = MultiCandidateTranslator(
        num_candidates=n_candidates,
        temperatures=temps,
        num_context_passages=ctx_passages,
        use_compiled=False,
    )

    # Apply the compiled state (bootstrapped demos, optimized prompts)
    # Prime the LM so module can initialize its sub-modules
    compiled._ensure_translator()
    compiled.load(str(args.program), allow_pickle=True)
    print(f"[LOAD] Loaded compiled state successfully")
    print(f"[LOAD] Module: {type(compiled).__name__}")

    # ── Load test set ────────────────────────────────────────────────────
    print(f"\n[DATA] Loading test set from {args.test}...")
    test_pairs = load_test_pairs(args.test)
    print(f"[DATA] Loaded {len(test_pairs)} test pairs")

    # ── Evaluate ─────────────────────────────────────────────────────────
    print(f"\n[EVAL] Running evaluation with {args.num_threads} threads via dspy.Evaluate...")
    t0 = time.time()

    evalset = [
        dspy.Example(
            english_text=p["english_text"],
            mirad_text=p["mirad_text"],
            id=p.get("id", ""),
        ).with_inputs("english_text")
        for p in test_pairs
    ]

    evaluator = dspy.Evaluate(
        devset=evalset,
        metric=normalized_match_metric,
        num_threads=args.num_threads,
        display_progress=True,
        display_table=0,
    )
    result = evaluator(compiled)
    elapsed = time.time() - t0

    results = []
    for i, row in enumerate(getattr(result, "results", []) or []):
        example = test_pairs[i] if i < len(test_pairs) else {}
        if isinstance(row, tuple):
            if len(row) >= 3:
                ex, pred, metric_value = row[0], row[1], row[2]
            elif len(row) == 2:
                ex, pred = row
                metric_value = normalized_match_metric(ex, pred)
            else:
                ex = example
                pred = row[0]
                metric_value = normalized_match_metric(ex, pred)
        else:
            ex = example
            pred = row
            metric_value = normalized_match_metric(ex, pred)

        mirad_pred = str(getattr(pred, "mirad_text", ""))
        gold_text = example.get("mirad_text", getattr(ex, "mirad_text", ""))
        nm = bool(metric_value)
        em = gold_text.strip() == mirad_pred.strip()

        winner_score = float(getattr(pred, "total_score", 0.0))
        candidates_data = getattr(pred, "candidates", [])
        cand_summaries = []
        for c in (candidates_data or []):
            j = c.get("judge", {})
            cand_summaries.append({
                "candidate_id": c.get("candidate_id"),
                "rank": c.get("rank"),
                "winner": c.get("winner", False),
                "temp": c.get("temperature"),
                "mirad": c.get("mirad_text"),
                "total_score": j.get("total_score", 0),
                "semantic_fidelity": j.get("semantic_fidelity", 0),
                "grammar": j.get("grammar_score", 0),
                "morphology": j.get("morphology_score", 0),
                "rule_hard_failures": c.get("rule_precheck", {}).get("hard_failures", []),
                "rule_soft_errors": c.get("rule_precheck", {}).get("soft_errors", []),
                "verifier_hard_failures": c.get("verifier", {}).get("hard_failures", []),
                "verifier_soft_errors": c.get("verifier", {}).get("verifier_soft_errors", []),
                "weighted_score": c.get("verifier", {}).get("weighted_score", 0),
                "rationale": j.get("rationale", ""),
            })

        results.append({
            "id": example.get("id", getattr(ex, "id", "")),
            "english_text": example.get("english_text", getattr(ex, "english_text", "")),
            "gold": gold_text,
            "pred": mirad_pred,
            "normalized_match": nm,
            "exact_match": em,
            "judge_score": winner_score,
            "winner_index": int(getattr(pred, "winner_index", 0)),
            "rationale": getattr(pred, "rationale", ""),
            "candidates": cand_summaries,
            "error": None,
        })

    error_results = [r for r in results if r.get("error")]
    if error_results:
        print(f"\n[EVAL] {len(error_results)}/{len(results)} examples errored:")
        for e in error_results[:5]:
            print(f"  ERROR: {e['english_text'][:50]}: {e['error']}")

    n = len(results)
    nm_hits = sum(1 for r in results if r["normalized_match"])
    em_hits = sum(1 for r in results if r["exact_match"])
    nm_rate = nm_hits / n if n else 0
    em_rate = em_hits / n if n else 0
    avg_judge = sum(r["judge_score"] for r in results) / n if n else 0

    print(f"\n{'='*60}")
    print(f"TEST SET EVALUATION RESULTS")
    print(f"{'='*60}")
    print(f"  Test set size:      {n}")
    print(f"  Normalized match:   {nm_rate:.1%} ({nm_hits}/{n})")
    print(f"  Exact match:        {em_rate:.1%} ({em_hits}/{n})")
    print(f"  Avg judge score:    {avg_judge:.1f}/100")
    print(f"  Wall time:          {elapsed:.0f}s ({elapsed/60:.1f} min)")
    print(f"  Avg per sample:     {elapsed/n:.1f}s" if n else "")
    print(f"{'='*60}")

    # ── Save results ─────────────────────────────────────────────────────
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "eval_type": "test_set_holdout",
        "program_path": str(args.program),
        "test_path": str(args.test),
        "config": {
            "num_threads": args.num_threads,
        },
        "metrics": {
            "normalized_match": nm_rate,
            "exact_match": em_rate,
            "avg_judge_score": avg_judge,
        },
        "counts": {
            "total": n,
            "normalized_match_correct": nm_hits,
            "exact_match_correct": em_hits,
            "errors": len(error_results),
        },
        "timing": {
            "wall_time_s": round(elapsed, 1),
            "avg_per_sample_s": round(elapsed / n, 2) if n else 0,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    summary_path = out_dir / "test_set_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\n[SAVE] Summary → {summary_path}")

    examples_path = out_dir / "test_set_examples.json"
    with open(examples_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"[SAVE] Examples → {examples_path}")

    # ── Also write a simple report ───────────────────────────────────────
    rows = []
    for i, r in enumerate(results):
        mark = "✓" if r["normalized_match"] else "✗"
        winner_cand = next((c for c in r.get("candidates", []) if c.get("winner")), None)
        t_str = f"T={winner_cand['temp']}" if winner_cand else "?"
        rows.append(
            f"| {i:3d} | {mark} | {r['judge_score']:5.1f} | {t_str} | "
            f"{r['english_text'][:55]} → {r['pred'][:40]} |"
        )

    report = f"""# Test Set Evaluation: Compiled MIPROv2 Program

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC  
**Program:** {args.program}  
**Test set:** {args.test} ({n} examples)  
**Threads:** {args.num_threads}  

## Metrics

| Metric | Value |
|--------|-------|
| Normalized Match | {nm_rate:.1%} ({nm_hits}/{n}) |
| Exact Match | {em_rate:.1%} ({em_hits}/{n}) |
| Avg Judge Score | {avg_judge:.1f}/100 |

## Timing

| | |
|-|--|
| Wall time | {elapsed:.0f}s ({elapsed:.1f} min) |
| Per sample | {elapsed/n:.1f}s |

## Results

| # | NM | Judge | Temp | Sample |
|---|----|-------|------|--------|
"""
    report += "\n".join(rows) + "\n"

    report_path = out_dir / "test_set_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"[SAVE] Report → {report_path}")
    print("[DONE]")


if __name__ == "__main__":
    main()
