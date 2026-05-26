#!/usr/bin/env python3
"""
4-way en→mir eval on 100 random samples.
Tests grammar retrieval (k=3 vs k=0) × word semantic lookup (k=0 vs k=2).

Samples: seed=20260526, min_english_words=0 (no filter), from train.json
Metric: normalized match
Model: deepseek-ai/DeepSeek-V4-Flash
Direction: en_to_mir only

Results → data/eval_results/four_way_sweep/
Each run is tagged: g{N}_w{N} where N is grammar k and word top_k_per_word.
"""

import csv, json, os, random, subprocess, sys, time
from datetime import datetime
from pathlib import Path

OUT_DIR = Path("data/eval_results/four_way_sweep")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Fixed eval params
MODEL      = "deepseek-ai/DeepSeek-V4-Flash"
SEED       = 20260526
N_SAMPLES  = 100
MIN_WORDS  = 0
DIRECTION  = "en_to_mir"

# The 4 configurations
CONFIGS = [
    {"tag": "g3_w0", "grammar_k": 3, "word_k": 0},
    {"tag": "g0_w0", "grammar_k": 0, "word_k": 0},
    {"tag": "g3_w2", "grammar_k": 3, "word_k": 2},
    {"tag": "g0_w2", "grammar_k": 0, "word_k": 2},
]

def run_config(cfg: dict) -> dict:
    tag      = cfg["tag"]
    grammar_k = cfg["grammar_k"]
    word_k    = cfg["word_k"]

    run_dir = OUT_DIR / tag
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_subdir = run_dir / timestamp
    run_subdir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, "scripts/run_evaluation.py",
        "--direction",  DIRECTION,
        "--n",         str(N_SAMPLES),
        "--seed",      str(SEED),
        "--min-words", str(MIN_WORDS),
        "--model",     MODEL,
        "--num-context-passages", str(grammar_k),
        "--top-k-per-word",        str(word_k),
        "--out-dir",    str(run_subdir),
        "--parallel",  "8",
    ]

    print(f"\n{'='*60}")
    print(f"  Running [{tag}]  grammar_k={grammar_k}  word_k={word_k}")
    print(f"  Output: {run_subdir}")
    print(f"  Command: {' '.join(cmd)}")
    t0 = time.time()

    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - t0

    print(f"  Exit: {result.returncode}  Time: {elapsed:.1f}s")
    if result.returncode != 0:
        print(f"  STDERR: {result.stderr[-500:]}")
        return {**cfg, "error": result.stderr, "elapsed_s": elapsed, "success": False}

    # Parse run_summary.json
    summaries = sorted(run_subdir.glob("*/run_summary.json"))
    if not summaries:
        # Maybe the output went somewhere else — search
        summaries = sorted(run_subdir.glob("run_summary.json"))
    if summaries:
        summary = json.load(open(summaries[-1]))
    else:
        summary = None

    # Parse examples.json to compute metrics
    examples_files = sorted(run_subdir.glob("*/examples.json"))
    if not examples_files:
        examples_files = sorted(run_subdir.glob("examples.json"))
    if examples_files:
        examples = json.load(open(examples_files[-1]))
    else:
        examples = []

    nm_count = sum(1 for e in examples if e.get("normalized_match", False))
    exact_count = sum(1 for e in examples if e.get("exact_match", False))

    metrics = summary.get("metrics", {}) if summary else {}
    norm_match = metrics.get("normalized_match", nm_count / len(examples) if examples else 0)
    exact_match = metrics.get("exact_match", exact_count / len(examples) if examples else 0)

    return {
        **cfg,
        "elapsed_s":      elapsed,
        "samples":        len(examples),
        "normalized_match": round(norm_match, 4),
        "exact_match":    round(exact_match, 4),
        "nm_count":       nm_count,
        "exact_count":   exact_count,
        "avg_ms_per_sample": (elapsed / len(examples) * 1000) if examples else 0,
        "summary_path":   str(summaries[-1]) if summaries else None,
        "success":        True,
    }


def write_csv(results: list, path: Path):
    cols = ["tag", "grammar_k", "word_k", "normalized_match", "exact_match",
            "nm_count", "exact_count", "samples", "elapsed_s", "avg_ms_per_sample"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in results:
            row = {k: r.get(k, "") for k in cols}
            w.writerow(row)
    print(f"\n  CSV → {path}")


def write_md(results: list, path: Path):
    rows = []
    for r in sorted([x for x in results if x.get("success")], key=lambda x: -x["normalized_match"]):
        nm  = f"{r['normalized_match']:.1%}"
        em  = f"{r['exact_match']:.1%}"
        tag = r["tag"]
        gk  = r["grammar_k"]
        wk  = r["word_k"]
        elapsed = f"{r['elapsed_s']:.0f}s"
        avg_ms  = f"{r.get('avg_ms_per_sample', 0):.0f}ms"
        rows.append(f"| {tag} | grammar_k={gk} | word_k={wk} | {nm} | {em} | {elapsed} ({avg_ms}/sample) |")

    winner = max(results, key=lambda x: x["normalized_match"])
    content = f"""# Four-Way en→mir Eval Sweep

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Samples:** {N_SAMPLES} (seed={SEED}, min_words={MIN_WORDS})  
**Direction:** {DIRECTION}  
**Model:** {MODEL}

## Results

| Config | Grammar k | Word k | Normalized Match | Exact Match | Time |
|--------|-----------|--------|-----------------|-------------|------|
{chr(10).join(rows)}

## Winner

**{winner['tag']}** (grammar_k={winner['grammar_k']}, word_k={winner['word_k']})  
Normalized match: {winner['normalized_match']:.1%}  
Exact match: {winner['exact_match']:.1%}

## Analysis

See output below.
"""
    with open(path, "w") as f:
        f.write(content)
    print(f"  MD → {path}")


def main():
    results = []
    for cfg in CONFIGS:
        r = run_config(cfg)
        results.append(r)
        # Save incremental CSV so we can check progress
        write_csv(results, OUT_DIR / "four_way_sweep_results.csv")

    write_md(results, OUT_DIR / "four_way_sweep_results.md")
    write_csv(results, OUT_DIR / "four_way_sweep_results.csv")

    print(f"\n{'='*60}")
    print("FINAL RESULTS")
    print(f"{'='*60}")
    print(f"{'Tag':<10} {'Gr k':>5} {'Wd k':>5} {'NormMatch':>12} {'Exact':>8} {'Time':>10}")
    print("-" * 60)
    for r in sorted(results, key=lambda x: -x.get("normalized_match", 0)):
        nm = r.get("normalized_match", 0)
        em = r.get("exact_match", 0)
        elapsed = r.get("elapsed_s", 0)
        print(f"{r['tag']:<10} {r['grammar_k']:>5} {r['word_k']:>5} "
              f"{nm:>12.1%} {em:>8.1%} "
              f"{elapsed:>8.0f}s")

    return 0 if all(r.get("success", False) for r in results) and len(results) == len(CONFIGS) else 1


if __name__ == "__main__":
    sys.exit(main())