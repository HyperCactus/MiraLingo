#!/usr/bin/env python3
"""Sweep top_k_per_word across {0, 3, 5, 8} for both translation directions.

Sweep the semantic lexicon lookup neighbors-per-word setting and find the
optimal value for normalized match accuracy.

Usage:
    python scripts/top_k_sweep.py          # runs all k × 2 directions (16 runs)
    python scripts/top_k_sweep.py --skip   # load existing results from disk
    python scripts/top_k_sweep.py --n 30 --parallel 8  # override defaults
"""
import argparse, csv, json, subprocess, sys, time
from datetime import datetime
from pathlib import Path

_ROOT      = Path(__file__).resolve().parents[1]
EVAL_SCRIPT = _ROOT / "scripts" / "run_evaluation.py"
CONFIG_FILE = _ROOT / "scripts" / "eval_config.yaml"
OUT_BASE   = _ROOT / "data" / "eval_results" / "top_k_sweep"
DATA_FILE  = _ROOT / "data" / "eval" / "train.json"

TOP_K_VALUES = [0, 3, 5, 8]
DIRECTIONS   = ["en_to_mir", "mir_to_en"]
N_SAMPLES    = 30
MIN_WORDS    = 5
RANDOM_SEED  = 20260526
PARALLEL     = 8


def run(args) -> int:
    return subprocess.run(args, cwd=_ROOT).returncode


def run_eval(top_k: int, direction: str, n: int, parallel: int, overwrite: bool) -> Path | None:
    """Run one evaluation and return the path to run_summary.json."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = OUT_BASE / f"topk{top_k}" / direction / ts

    cmd = [
        sys.executable, str(EVAL_SCRIPT),
        "--config",     str(CONFIG_FILE),
        "--data",       str(DATA_FILE),
        "--direction",  direction,
        "--n",          str(n),
        "--min-words",  str(MIN_WORDS),
        "--seed",       str(RANDOM_SEED),
        "--parallel",   str(parallel),
        "--num-context-passages", "3",   # lock k=3 from prior sweep
        "--top-k-per-word",       str(top_k),
        "--out-dir",    str(out_dir),
    ]
    if overwrite:
        cmd.append("--overwrite")

    print(f"\n{'='*60}")
    print(f"  top_k_per_word={top_k}  direction={direction}  n={n}  parallel={parallel}")
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
    nm = data.get("metrics", {}).get("normalized_match", 0)
    acc_pct = round(nm * 100, 1)
    avg_ms  = data.get("timing", {}).get("avg_per_sample_ms", "N/A")
    total   = data.get("counts", {}).get("total", "N/A")
    print(f"     normalized_match: {acc_pct}%")
    print(f"     avg_ms/sample:   {avg_ms}")
    return summary


def collect_results() -> list[dict]:
    """Read all run_summary.json files from OUT_BASE."""
    rows = []
    for top_k in TOP_K_VALUES:
        for direction in DIRECTIONS:
            run_dir = OUT_BASE / f"topk{top_k}" / direction
            if not run_dir.exists():
                continue
            runs = sorted(run_dir.iterdir())
            if not runs:
                continue
            summary_path = runs[-1] / "run_summary.json"
            if not summary_path.exists():
                continue
            with open(summary_path) as f:
                data = json.load(f)
            nm  = data.get("metrics", {}).get("normalized_match", 0)
            acc = round(nm * 100, 1)
            ms  = data.get("timing", {}).get("avg_per_sample_ms", 0)
            tot = data.get("counts", {}).get("total", 0)
            rows.append({
                "top_k": top_k,
                "direction": direction,
                "accuracy_percent": acc,
                "avg_ms_per_sample": round(ms, 1) if ms else "N/A",
                "total_samples": tot,
                "summary_path": str(summary_path.relative_to(_ROOT)),
            })
    return rows


def print_table(rows: list[dict]):
    print("\n" + "=" * 80)
    print("  top_k_per_word SWEEP RESULTS — normalized_match accuracy")
    print("=" * 80)
    print(f"{'top_k':>6}  {'direction':<12}  {'accuracy':>10}  {'ms/sample':>10}  {'n':>4}")
    print("-" * 80)
    for r in rows:
        print(f"{r['top_k']:>6}  {r['direction']:<12}  "
              f"{str(r['accuracy_percent']):>10}  "
              f"{str(r['avg_ms_per_sample']):>10}  "
              f"{str(r['total_samples']):>4}")

    print("-" * 80)
    for direction in DIRECTIONS:
        dr = [r for r in rows if r["direction"] == direction]
        if not dr:
            continue
        best = max(dr, key=lambda r: float(r["accuracy_percent"] or 0))
        print(f"\n  Best for {direction}: top_k_per_word={best['top_k']} "
              f"({best['accuracy_percent']}%)")

    print()
    for top_k in TOP_K_VALUES:
        kr = [r for r in rows if r["top_k"] == top_k and
              r["direction"] in ("en_to_mir", "mir_to_en")]
        if len(kr) < 2:
            continue
        accs = [float(r["accuracy_percent"]) for r in kr
                if r["accuracy_percent"] not in ("N/A", None)]
        if accs:
            avg = sum(accs) / len(accs)
            print(f"  top_k={top_k}: avg accuracy across directions = {avg:.1f}%")


def write_csv(rows: list[dict]):
    if not rows:
        return
    path = OUT_BASE / "top_k_sweep_results.csv"
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "top_k", "direction", "accuracy_percent",
            "avg_ms_per_sample", "total_samples", "summary_path"])
        w.writeheader()
        w.writerows(rows)
    print(f"\n  CSV saved: {path.relative_to(_ROOT)}")


def write_md(rows: list[dict]):
    path = OUT_BASE / "top_k_sweep_results.md"
    lines = [
        "# top_k_per_word Sweep Results\n",
        f"Run at: {datetime.now().isoformat()}",
        f"Data: {DATA_FILE.relative_to(_ROOT)} | n={N_SAMPLES} | seed={RANDOM_SEED}",
        f"k (num_context_passages): locked at 3 (from prior sweep)\n\n",
        "| top_k | direction | accuracy | ms/sample | n |",
        "|-------|-----------|----------|-----------|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['top_k']} | {r['direction']} | "
            f"{r['accuracy_percent']}% | {r['avg_ms_per_sample']} | "
            f"{r['total_samples']} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  Markdown saved: {path.relative_to(_ROOT)}")


def main():
    p = argparse.ArgumentParser(description="Sweep top_k_per_word for semantic lexicon lookup")
    p.add_argument("--k", type=int, nargs="+", default=TOP_K_VALUES,
                   help=f"top_k_per_word values to test (default: {TOP_K_VALUES})")
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
        for top_k in args.k:
            for direction in DIRECTIONS:
                summary = run_eval(top_k=top_k, direction=direction,
                                   n=args.n, parallel=args.parallel,
                                   overwrite=True)
                if summary:
                    with open(summary) as f:
                        data = json.load(f)
                    nm   = data.get("metrics", {}).get("normalized_match", 0)
                    rows.append({
                        "top_k": top_k,
                        "direction": direction,
                        "accuracy_percent": round(nm * 100, 1),
                        "avg_ms_per_sample": round(
                            data.get("timing", {}).get("avg_per_sample_ms", 0), 1),
                        "total_samples": data.get("counts", {}).get("total", 0),
                        "summary_path": str(summary.relative_to(_ROOT)),
                    })

    print_table(rows)
    write_csv(rows)
    write_md(rows)
    total_runs = len(args.k) * len(DIRECTIONS)
    print(f"\n  {len(rows)}/{total_runs} runs collected.")


if __name__ == "__main__":
    main()