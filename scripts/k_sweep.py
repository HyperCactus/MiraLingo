#!/usr/bin/env python3
"""Sweep k (num_context_passages) across {3, 6, 9, 16} for both directions.

Finds the optimal number of grammar rules to retrieve per query.

Usage:
    python scripts/k_sweep.py
    python scripts/k_sweep.py --k 3 6 16          # custom k values
    python scripts/k_sweep.py --n 30 --parallel 8 # override eval settings
"""
import argparse, csv, json, subprocess, sys, time
from datetime import datetime
from pathlib import Path

_ROOT      = Path(__file__).resolve().parents[1]
SCRIPT_DIR  = _ROOT / "scripts"
EVAL_SCRIPT = SCRIPT_DIR / "run_evaluation.py"
CONFIG_FILE = SCRIPT_DIR / "eval_config.yaml"
OUT_BASE    = _ROOT / "data" / "eval_results" / "k_sweep"
DATA_FILE   = _ROOT / "data" / "eval" / "train.json"

KS = [3, 6, 9, 16]
DIRECTIONS = ["en_to_mir", "mir_to_en"]
N_SAMPLES   = 30
MIN_WORDS   = 5
RANDOM_SEED = 20260526  # deterministic 30-sample selection
PARALLEL    = 8


def run(args) -> int:
    return subprocess.run(args, cwd=_ROOT).returncode


def run_eval(k: int, direction: str, n: int, parallel: int, overwrite: bool) -> Path | None:
    """Run one evaluation and return the path to run_summary.json."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = OUT_BASE / f"k{k}" / direction / ts

    cmd = [
        sys.executable, str(EVAL_SCRIPT),
        "--config",     str(CONFIG_FILE),
        "--data",       str(DATA_FILE),
        "--direction",  direction,
        "--n",          str(n),
        "--min-words",  str(MIN_WORDS),
        "--seed",       str(RANDOM_SEED),
        "--parallel",   str(parallel),
        "--num-context-passages", str(k),
        "--out-dir",    str(out_dir),
    ]
    if overwrite:
        cmd.append("--overwrite")

    print(f"\n{'='*60}")
    print(f"  k={k}  direction={direction}  n={n}  parallel={parallel}")
    print(f"  out: {out_dir.relative_to(_ROOT)}")
    print(f"{'='*60}")
    sys.stdout.flush()

    t0 = time.time()
    rc = run(cmd)
    elapsed = time.time() - t0

    if rc != 0:
        print(f"  ❌ FAILED (exit {rc}) after {elapsed:.0f}s")
        return None

    summary = out_dir / "run_summary.json"
    if not summary.exists():
        print(f"  ⚠️  No run_summary.json at {summary}")
        return None

    print(f"  ✅ done in {elapsed:.0f}s")
    with open(summary) as f:
        data = json.load(f)
    pct = data.get("normalized_match", {}).get("accuracy_percent", "N/A")
    avg_ms = data.get("normalized_match", {}).get("avg_ms_per_sample", "N/A")
    print(f"     normalized_match: {pct}%")
    print(f"     avg_ms/sample:   {avg_ms}")
    return summary


def collect_results() -> list[dict]:
    """Read all run_summary.json files from the sweep."""
    rows = []
    for k in KS:
        for direction in DIRECTIONS:
            run_dir = OUT_BASE / f"k{k}" / direction
            if not run_dir.exists():
                continue
            # Pick the latest run for this k/direction combo
            runs = sorted(run_dir.iterdir())
            if not runs:
                continue
            summary_path = runs[-1] / "run_summary.json"
            if not summary_path.exists():
                continue
            with open(summary_path) as f:
                data = json.load(f)
            nm = data.get("normalized_match", {})
            rows.append({
                "k": k,
                "direction": direction,
                "accuracy_percent": nm.get("accuracy_percent", "N/A"),
                "avg_ms_per_sample": nm.get("avg_ms_per_sample", "N/A"),
                "total_samples": nm.get("total_samples", "N/A"),
                "total_seconds": round((runs[-1].stat().st_mtime -
                    (runs[-1].stat().st_ctime if False else 0)), 1),
                "summary_path": str(summary_path.relative_to(_ROOT)),
            })
    return rows


def print_table(rows: list[dict]):
    print("\n" + "=" * 80)
    print("  k-SWEEP RESULTS — normalized_match accuracy")
    print("=" * 80)
    print(f"{'k':>4}  {'direction':<12}  {'accuracy':>10}  {'ms/sample':>10}  {'n':>4}")
    print("-" * 80)
    for r in rows:
        print(f"{r['k']:>4}  {r['direction']:<12}  "
              f"{str(r['accuracy_percent']):>10}  "
              f"{str(r['avg_ms_per_sample']):>10}  "
              f"{str(r['total_samples']):>4}")

    # Per-direction summary
    print("-" * 80)
    for direction in DIRECTIONS:
        dir_rows = [r for r in rows if r["direction"] == direction]
        if not dir_rows:
            continue
        best = max(dir_rows, key=lambda r: float(r["accuracy_percent"] or 0))
        print(f"\n  Best for {direction}: k={best['k']} "
              f"({best['accuracy_percent']}%)")

    # Overall best (average across both directions)
    print()
    for k in KS:
        k_rows = [r for r in rows if r["k"] == k]
        if len(k_rows) < 2:
            continue
        accs = [float(r["accuracy_percent"]) for r in k_rows
                if r["accuracy_percent"] not in ("N/A", None)]
        if accs:
            avg = sum(accs) / len(accs)
            print(f"  k={k:>2}: avg accuracy across directions = {avg:.1f}%")


def write_csv(rows: list[dict], path: Path):
    if not rows:
        return
    fieldnames = ["k", "direction", "accuracy_percent", "avg_ms_per_sample",
                  "total_samples", "summary_path"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"\n  CSV saved: {path.relative_to(_ROOT)}")


def write_md(rows: list[dict], path: Path):
    lines = [
        "# k-Sweep Results",
        "",
        f"Run at: {datetime.now().isoformat()}",
        f"Data: {DATA_FILE.relative_to(_ROOT)} | n={N_SAMPLES} | seed={RANDOM_SEED}",
        "",
        "| k | direction | accuracy | ms/sample | n |",
        "|---|-----------|----------|-----------|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['k']} | {r['direction']} | "
            f"{r['accuracy_percent']} | {r['avg_ms_per_sample']} | "
            f"{r['total_samples']} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  Markdown saved: {path.relative_to(_ROOT)}")


def main():
    p = argparse.ArgumentParser(description="Run k-sweep for grammar rule retrieval")
    p.add_argument("--k", type=int, nargs="+", default=KS,
                   help=f"K values to test (default: {KS})")
    p.add_argument("--n", type=int, default=N_SAMPLES,
                   help=f"Number of samples per run (default: {N_SAMPLES})")
    p.add_argument("--parallel", type=int, default=PARALLEL,
                   help=f"Parallel workers (default: {PARALLEL})")
    p.add_argument("--skip", action="store_true",
                   help="Skip runs; load existing results from disk.")
    args = p.parse_args()

    OUT_BASE.mkdir(parents=True, exist_ok=True)

    if args.skip:
        rows = collect_results()
    else:
        rows = []
        for k in args.k:
            for direction in DIRECTIONS:
                summary = run_eval(k=k, direction=direction,
                                  n=args.n, parallel=args.parallel,
                                  overwrite=True)
                if summary:
                    with open(summary) as f:
                        data = json.load(f)
                    nm = data.get("normalized_match", {})
                    rows.append({
                        "k": k,
                        "direction": direction,
                        "accuracy_percent": nm.get("accuracy_percent", "N/A"),
                        "avg_ms_per_sample": nm.get("avg_ms_per_sample", "N/A"),
                        "total_samples": nm.get("total_samples", "N/A"),
                        "summary_path": str(summary.relative_to(_ROOT)),
                    })

    print_table(rows)
    write_csv(rows, OUT_BASE / "k_sweep_results.csv")
    write_md(rows, OUT_BASE / "k_sweep_results.md")

    total_runs = len(args.k) * len(DIRECTIONS)
    print(f"\n  {len(rows)}/{total_runs} runs collected.")


if __name__ == "__main__":
    main()