#!/usr/bin/env python3
"""BootstrapFewShot parameter sweep on DeepSeek-V4-Flash.

Sweeps BootstrapFewShot configurations:
    max_bootstrapped_demos ∈ {2, 4, 8}
    max_labeled_demos ∈ {4, 8, 16}
    max_rounds ∈ {1, 2, 3}
    metric_threshold ∈ {None, 0.5}

Also runs LabeledFewShot baselines for k ∈ {3, 5, 8, 12}.

Dataset: data/phrases/english-mirad-sentence-pairs.csv (44 pairs)
Split: train on first 34, eval on last 10 (per the milestone plan).

Each config writes its own JSON to data/eval_results/bootstrap_sweep/.
A sweep_summary.csv is written at the end.
"""
import csv
import json
import os
import sys
import time
from pathlib import Path

# Ensure packages/translator/src is on path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "packages" / "translator" / "src"))

import dspy
from dotenv import load_dotenv

from mirad_translator.evaluate import (
    load_evaluation_set,
    compile_with_bootstrap,
    normalized_match_metric,
    exact_match_metric,
    run_labeled_fewshot_eval,
    _make_deepinfra_lm,
)
from mirad_translator.translate import DefaultTranslator, TranslatorModule

_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_ROOT / ".env")

OUT_DIR = _ROOT / "data" / "eval_results" / "bootstrap_sweep"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Configure DeepInfra LM ────────────────────────────────────────────────────
DEEPINFRA_MODEL = os.environ.get("DEEPINFRA_TEACHER_MODEL", "deepseek-ai/DeepSeek-V4-Flash")
DEEPINFRA_API_KEY = os.environ.get("DEEPINFRA_API_KEY")
DEEPINFRA_BASE_URL = os.environ.get("DEEPINFRA_BASE_URL", "https://api.deepinfra.com/v1/openai")

lm = dspy.LM(
    model=f"openai/{DEEPINFRA_MODEL}",
    api_key=DEEPINFRA_API_KEY,
    api_base=DEEPINFRA_BASE_URL,
)
dspy.settings.configure(lm=lm)


# ── Load and split dataset ────────────────────────────────────────────────────
all_examples = load_evaluation_set()
# Train on first 34, eval on last 10 (per milestone plan)
TRAIN_SIZE = 34
trainset = all_examples[:TRAIN_SIZE]
evalset = all_examples[TRAIN_SIZE:]
print(f"[sweep] trainset={len(trainset)}, evalset={len(evalset)}")


def run_bfs_config(
    max_bootstrapped_demos: int,
    max_labeled_demos: int,
    max_rounds: int,
    metric_threshold: float | None,
    trainset: list,
    evalset: list,
) -> dict:
    """Compile with BootstrapFewShot and evaluate on evalset."""
    from dspy import Evaluate, BootstrapFewShot

    print(f"\n[ BFS ] d={max_bootstrapped_demos} l={max_labeled_demos} "
          f"r={max_rounds} t={metric_threshold}")

    compile_start = time.time()

    bfs_kwargs = dict(
        metric=normalized_match_metric,
        max_bootstrapped_demos=max_bootstrapped_demos,
        max_labeled_demos=max_labeled_demos,
        max_rounds=max_rounds,
    )
    if metric_threshold is not None:
        bfs_kwargs["metric_threshold"] = metric_threshold

    optimizer = BootstrapFewShot(**bfs_kwargs)
    student = TranslatorModule(num_context_passages=5)
    compiled = optimizer.compile(student, trainset=trainset)
    compile_time = time.time() - compile_start

    # Evaluate
    eval_start = time.time()

    norm_eval = Evaluate(
        devset=evalset,
        metric=normalized_match_metric,
        num_threads=1,
        display_progress=True,
        display_table=0,
    )
    norm_result = norm_eval(compiled)

    exact_eval = Evaluate(
        devset=evalset,
        metric=exact_match_metric,
        num_threads=1,
        display_progress=True,
        display_table=0,
    )
    exact_result = exact_eval(compiled)

    eval_time = time.time() - eval_start
    total_time = time.time() - compile_start

    norm_score = norm_result.score if hasattr(norm_result, "score") else norm_result
    exact_score = exact_result.score if hasattr(exact_result, "score") else exact_result

    print(f"     norm={norm_score:.1f}% exact={exact_score:.1f}%  "
          f"compile={compile_time:.1f}s eval={eval_time:.1f}s")

    return {
        "method": "BootstrapFewShot",
        "lm_type": "deepinfra",
        "model": DEEPINFRA_MODEL,
        "max_bootstrapped_demos": max_bootstrapped_demos,
        "max_labeled_demos": max_labeled_demos,
        "max_rounds": max_rounds,
        "metric_threshold": metric_threshold,
        "k_context_passages": 5,
        "train_size": len(trainset),
        "eval_size": len(evalset),
        "normalized_score": norm_score,
        "exact_score": exact_score,
        "compile_time_s": round(compile_time, 2),
        "eval_time_s": round(eval_time, 2),
        "total_time_s": round(total_time, 2),
    }


def run_lfs_config(num_fewshot: int, trainset: list, evalset: list) -> dict:
    """Run LabeledFewShot baseline for comparison."""
    from dspy import LabeledFewShot, Evaluate
    from mirad_translator.translate import TranslatorModule, _format_word_equivalents, _format_context_passages

    print(f"\n[ LFS ] k={num_fewshot}")

    # Enrich few-shot demos with pre-computed word equivalents + no context
    module = DefaultTranslator(num_context_passages=0)
    enriched = []
    for ex in trainset[:num_fewshot]:
        we_pred = module.lexicon_lookup(english_text=ex.english_text)
        we_str = _format_word_equivalents(we_pred.word_equivalents)
        enriched.append(
            dspy.Example(
                english_text=ex.english_text,
                word_equivalents=we_str,
                context_passages="",
                mirad_text=ex.mirad_text,
            ).with_inputs("english_text", "word_equivalents", "context_passages")
        )

    compile_start = time.time()
    compiled = LabeledFewShot(k=num_fewshot).compile(
        student=TranslatorModule(num_context_passages=0),
        trainset=enriched,
    )
    compile_time = time.time() - compile_start

    eval_start = time.time()
    norm_eval = Evaluate(devset=evalset, metric=normalized_match_metric,
                         num_threads=1, display_progress=True, display_table=0)
    norm_result = norm_eval(compiled)
    exact_eval = Evaluate(devset=evalset, metric=exact_match_metric,
                         num_threads=1, display_progress=True, display_table=0)
    exact_result = exact_eval(compiled)
    eval_time = time.time() - eval_start

    norm_score = norm_result.score if hasattr(norm_result, "score") else norm_result
    exact_score = exact_result.score if hasattr(exact_result, "score") else exact_result

    print(f"     norm={norm_score:.1f}% exact={exact_score:.1f}%  "
          f"compile={compile_time:.1f}s eval={eval_time:.1f}s")

    return {
        "method": "LabeledFewShot",
        "lm_type": "deepinfra",
        "model": DEEPINFRA_MODEL,
        "num_fewshot": num_fewshot,
        "k_context_passages": 0,
        "train_size": len(trainset),
        "eval_size": len(evalset),
        "normalized_score": norm_score,
        "exact_score": exact_score,
        "compile_time_s": round(compile_time, 2),
        "eval_time_s": round(eval_time, 2),
        "total_time_s": round(compile_time + eval_time, 2),
    }


def config_slug(d: int, l: int, r: int, t: float | None) -> str:
    if t is None:
        return f"bfs_d{d}_l{l}_r{r}"
    else:
        return f"bfs_d{d}_l{l}_t{int(t*100)}"


# ── BFS Configurations ───────────────────────────────────────────────────────
# 6 configs per the task plan
bfs_configs = [
    # (max_bootstrapped_demos, max_labeled_demos, max_rounds, metric_threshold)
    (2,  4, 1, None),   # bfs_d2_l4_r1
    (4,  8, 1, None),   # bfs_d4_l8_r1
    (4, 16, 1, None),   # bfs_d4_l16_r1
    (8, 16, 2, None),   # bfs_d8_l16_r2  (multi-round)
    (4,  8, 3, None),   # bfs_d4_l8_r3   (multi-round)
    (2,  8, 1, 0.5),    # bfs_d2_l8_t50  (threshold filter)
]

results = []

# Run BFS configs
for d, l, r, t in bfs_configs:
    slug = config_slug(d, l, r, t)
    out_path = OUT_DIR / f"{slug}.json"

    result = run_bfs_config(d, l, r, t, trainset, evalset)
    result["config_slug"] = slug

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    results.append(result)
    print(f"  → saved {out_path}")

# ── LabeledFewShot baselines ──────────────────────────────────────────────────
lfs_configs = [3, 5, 8, 12]

for k in lfs_configs:
    slug = f"lfs_k{k}"
    out_path = OUT_DIR / f"{slug}.json"

    result = run_lfs_config(k, trainset, evalset)
    result["config_slug"] = slug

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    results.append(result)
    print(f"  → saved {out_path}")

# ── Summary CSV ───────────────────────────────────────────────────────────────
csv_path = OUT_DIR / "sweep_summary.csv"
fieldnames = [
    "config_slug", "method", "model", "lm_type",
    "max_bootstrapped_demos", "max_labeled_demos", "max_rounds", "metric_threshold",
    "num_fewshot",
    "k_context_passages", "train_size", "eval_size",
    "normalized_score", "exact_score",
    "compile_time_s", "eval_time_s", "total_time_s",
]

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(results)

print(f"\n[sweep] Summary → {csv_path}")

# ── Print table ──────────────────────────────────────────────────────────────
print(f"\n{'='*80}")
print(f"{'Config':<25} {'Method':<18} {'Norm%':>7} {'Exact%':>7} {'Rounds':>6} {'Thr':>5}  Compile   Eval")
print(f"{'='*80}")
for r in results:
    thr = str(r.get("metric_threshold", "")) if r.get("metric_threshold") is not None else "-"
    rounds = r.get("max_rounds", "-")
    print(f"{r['config_slug']:<25} {r['method']:<18} "
          f"{r['normalized_score']:>7.1f} {r['exact_score']:>7.1f} "
          f"{rounds:>6} {thr:>5}  "
          f"{r['compile_time_s']:>6.1f}s  {r['eval_time_s']:>6.1f}s")
print(f"{'='*80}")
print(f"\nTotal configs run: {len(results)}")