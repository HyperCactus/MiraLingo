#!/usr/bin/env python3
"""
MIPROv2 optimization for EnMiradGEPA (multi-candidate translation system).

MIPROv2 jointly optimizes instruction prompts and few-shot examples using
Bayesian optimization. It bootstraps candidate demos from the trainset,
proposes instruction variants grounded in the task dynamics, and finds the
best combination via Bayesian search.

Key features:
  - Checkpoint/resume via shared log_dir (pass the SAME --out-dir to resume)
  - Auto "light" mode = reasonable cost (~10-15 Bayesian trials)
  - Trainset from data/eval/val.json (subset), valset held out for BO scoring
  - Full eval on 100 val samples after optimization

Usage:
    # Fresh run (creates new log_dir under --out-dir):
    python run_mipro_optimization.py --out-dir data/eval_results/mipro_light_run

    # Resume interrupted run (same --out-dir reloads log_dir state):
    python run_mipro_optimization.py --out-dir data/eval_results/mipro_light_run

    # Lightweight smoke test (5 trials, 20-sample trainset, 10-sample valset):
    python run_mipro_optimization.py --out-dir data/eval_results/mipro_smoke \
        --auto light --num-trials 5 --trainset-size 20 --valset-size 10

Outputs (in --out-dir):
    program.pkl       — compiled MIPROv2 program (cloudpickle)
    run_summary.json  — config, metrics, timing
    examples.json     — per-example predictions and scores
    report.md         — human-readable summary
    gepa_logs/        — MIPROv2 Bayesian optimization logs (checkpoint state)

Estimated cost/time (auto=light, 50 trainset, 20 valset, ~15 trials):
  Each trial runs both trainset (minibatch, ~20-30s) and valset (full, ~2-3min)
  ~15 trials × ~3 min ≈ 45 min total
  DeepSeek V4 Flash pricing: ~$0.006/min × 45 min ≈ $0.27
  Per 1M output tokens (approx 10k/trial × 15): ~$0.02 for completions
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

# ── Project setup ────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "translator" / "src"))

load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=True)

import dspy
from dspy.teleprompt import MIPROv2
from dspy.utils.usage_tracker import UsageTracker


def _patch_dspy_dump_state_compat() -> None:
    """Patch older DSPy Retrieve.dump_state signature for MIPROv2 save path.

    Some DSPy mixes call Retrieve.dump_state(json_mode=...), while older
    Retrieve implementations accept no json_mode kwarg.
    """
    import inspect

    retrieve_cls = getattr(dspy, "Retrieve", None)
    if retrieve_cls is None or hasattr(retrieve_cls, "dump_state") is False:  # noqa: E711
        return

    try:
        sig = inspect.signature(retrieve_cls.dump_state)
    except Exception:
        return

    if "json_mode" in sig.parameters:
        return

    original = retrieve_cls.dump_state

    def _compat_dump_state(self, json_mode=False):
        try:
            return original(self)
        except AttributeError:
            state = {}
            for key in ("k", "num_passages", "stage", "query", "filters"):
                if hasattr(self, key):
                    state[key] = getattr(self, key)
            if not state:
                state = {k: v for k, v in vars(self).items() if not k.startswith("_")}
            return state

    retrieve_cls.dump_state = _compat_dump_state


_patch_dspy_dump_state_compat()


def _patch_mipro_distributions_bug(optimizer: MIPROv2) -> None:
    """Patch DSPy+Optuna mismatch in MIPROv2 trial creation.

    DSPy may generate params for predictors 0..N while distributions only include
    predictor_0 keys. Optuna then raises ValueError for inconsistent params vs
    distributions. We patch create_trial during optimize() and auto-extend missing
    distributions using a compatible reference distribution.
    """
    import functools
    import optuna

    orig_method = optimizer._optimize_prompt_parameters

    def _clone_distribution(ref_dist):
        if isinstance(ref_dist, optuna.distributions.CategoricalDistribution):
            return optuna.distributions.CategoricalDistribution(choices=ref_dist.choices)
        # Handle numeric distributions (Int/Float) that expose low/high.
        if hasattr(ref_dist, "low") and hasattr(ref_dist, "high"):
            kwargs = {"low": ref_dist.low, "high": ref_dist.high}
            if hasattr(ref_dist, "step"):
                kwargs["step"] = ref_dist.step
            if hasattr(ref_dist, "log"):
                kwargs["log"] = ref_dist.log
            return type(ref_dist)(**kwargs)
        # Fallback (should rarely be needed).
        return ref_dist

    @functools.wraps(orig_method)
    def _wrapped(self, *args, **kwargs):
        frozen_mod = sys.modules["optuna.trial._frozen"]
        trial_mod = sys.modules["optuna.trial"]
        saved_frozen = frozen_mod.create_trial
        saved_trial = trial_mod.create_trial

        def _patched_create_trial(*, params=None, distributions=None, **kw):
            if params and distributions is not None:
                missing = sorted(set(params) - set(distributions))
                if missing and distributions:
                    ref_key = next(
                        (k for k in sorted(distributions) if "instruction" in k or "demos" in k),
                        next(iter(distributions)),
                    )
                    ref_dist = distributions[ref_key]
                    for key in missing:
                        distributions[key] = _clone_distribution(ref_dist)
            return saved_frozen(params=params, distributions=distributions, **kw)

        # Also pad proposer candidate containers so objective indexing doesn't fail.
        args_list = list(args)
        min_preds = 3
        if len(args_list) > 1:
            ic = args_list[1]
            if isinstance(ic, dict) and ic:
                seed = ic.get(0, [""])
                seed_val = seed[0] if seed else ""
                for i in range(min_preds):
                    if i not in ic or not ic[i]:
                        ic[i] = [seed_val]
                    while len(ic[i]) < min_preds:
                        ic[i].append(ic[i][0])
                args_list[1] = ic

        if len(args_list) > 2:
            dc = args_list[2]
            if isinstance(dc, list) and dc:
                while len(dc) < min_preds:
                    dc.append(dc[-1] if dc else [])
                args_list[2] = dc
            elif isinstance(dc, dict) and dc:
                # DSPy may pass demo_candidates as {predictor_idx: list_of_demo_sets}
                seed_list = dc.get(0, [])
                for i in range(min_preds):
                    if i not in dc:
                        dc[i] = seed_list
                args_list[2] = dc

        try:
            setattr(frozen_mod, "create_trial", _patched_create_trial)
            setattr(trial_mod, "create_trial", _patched_create_trial)
            return orig_method(*args_list, **kwargs)
        finally:
            setattr(frozen_mod, "create_trial", saved_frozen)
            setattr(trial_mod, "create_trial", saved_trial)

    optimizer._optimize_prompt_parameters = _wrapped.__get__(optimizer, type(optimizer))


_patch_dspy_dump_state_compat()

# ── Project imports ───────────────────────────────────────────────────────────
from mirad_translator.evaluate import normalized_match_metric
from mirad_translator.multi_candidate import MultiCandidateTranslator

# ────────────────────────────────────────────────────────────────────────────
# Helper: load eval pairs from JSON (mirad-db format)
# ────────────────────────────────────────────────────────────────────────────

def load_eval_pairs(
    json_path: Path,
    min_english_words: int = 0,
    max_samples: int = 0,
    seed: int = 42,
) -> list[dict]:
    """Load English→Mirad pairs from a JSON file (mirad-db format).

    Args:
        json_path: Path to JSON with {"metadata": ..., "pairs": [...]}.
        min_english_words: Skip pairs whose English text has fewer words.
        max_samples: Limit total pairs (0 = no limit).
        seed: Random seed for shuffling before max_samples cutoff.

    Returns:
        List of dicts with "id", "english_text", "mirad_text".
    """
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    pairs = data.get("pairs", [])
    if isinstance(data, list):
        pairs = data

    def count_words(text: str) -> int:
        return len(text.strip().split())

    def normalize_pair(p: dict, i: int) -> dict:
        english = p.get("english_text", p.get("english"))
        mirad = p.get("mirad_text", p.get("mirad"))
        if not english or not mirad:
            raise KeyError(
                f"Pair missing required text fields at index {i}. "
                f"Expected english_text/mirad_text or english/mirad keys."
            )
        return {
            "id": p.get("id", f"pair-{i}"),
            "english_text": english,
            "mirad_text": mirad,
        }

    normalized_pairs = [normalize_pair(p, i) for i, p in enumerate(pairs)]
    filtered = [p for p in normalized_pairs if count_words(p["english_text"]) >= min_english_words]

    if max_samples and len(filtered) > max_samples:
        import random
        rng = random.Random(seed)
        rng.shuffle(filtered)
        filtered = filtered[:max_samples]

    return filtered


# ────────────────────────────────────────────────────────────────────────────

# ── Constants ────────────────────────────────────────────────────────────────
DEFAULT_TRAIN_PATH = PROJECT_ROOT / "data" / "eval" / "train.json"
DEFAULT_VAL_PATH = PROJECT_ROOT / "data" / "eval" / "val.json"
OUT_DIR_BASE = PROJECT_ROOT / "data" / "eval_results"
DEFAULT_TEMPERATURES = [0.1, 0.4, 0.8]

# DeepSeek V4 Flash pricing (per 1M tokens)
DEEPSEEK_INPUT_PER_1M = 0.10
DEEPSEEK_OUTPUT_PER_1M = 0.20
DEEPSEEK_CACHED_PER_1M = 0.02

# ────────────────────────────────────────────────────────────────────────────


def _configure_lm():
    import os

    model = os.environ.get("DEEPINFRA_MODEL") or os.environ.get("DEEPINFRA_TRANSLATION_MODEL") or "deepseek-ai/DeepSeek-V4-Flash"
    if model == "deepseek-ai/DeepSeek-V4-Chat":
        # DeepInfra no longer serves this alias; use Flash as safe default.
        model = "deepseek-ai/DeepSeek-V4-Flash"
    api_key = os.environ.get("DEEPINFRA_API_KEY", os.environ.get("OPENAI_API_KEY", ""))
    api_base = os.environ.get("DEEPINFRA_BASE_URL", "https://api.deepinfra.com/v1/openai")

    if not api_key:
        raise RuntimeError(
            "DEEPINFRA_API_KEY not set. Set it in .env or export it:\n"
            "  export DEEPINFRA_API_KEY=your_key_here\n"
            "Get a key at https://deepinfra.com/deepseek-v4"
        )

    lm = dspy.LM(
        model=f"openai/{model}",
        api_key=api_key,
        api_base=api_base,
        price=[DEEPSEEK_INPUT_PER_1M, DEEPSEEK_OUTPUT_PER_1M],
        cache_version=2,
        num_retries=5,
        timeout=120,
    )
    dspy.settings.configure(lm=lm)
    return lm


def _strip_punct(s: str) -> str:
    s = re.sub(r'[.,!?;:()"\'\[\]{}]', "", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def _load_prior_summary(out_dir: Path) -> Optional[dict]:
    summary_path = out_dir / "run_summary.json"
    if summary_path.exists():
        try:
            with open(summary_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None


def _save_summary(out_dir: Path, data: dict):
    with open(out_dir / "run_summary.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _save_examples(out_dir: Path, examples: list):
    with open(out_dir / "examples.json", "w", encoding="utf-8") as f:
        json.dump(examples, f, indent=2, ensure_ascii=False)


def _save_report(out_dir: Path, summary: dict, examples: list):
    from datetime import datetime as dt

    nm = summary["metrics"]["normalized_match"]
    em = summary["metrics"]["exact_match"]
    avg_j = summary["metrics"]["avg_judge_score"]
    compile_s = summary["timing"]["compile_time_s"]
    eval_s = summary["timing"]["eval_time_s"]
    n = len(examples)

    rows = []
    for i, r in enumerate(examples):
        mark = "✓" if r["normalized_match"] else "✗"
        winner_cand = next((c for c in r["candidates"] if c.get("winner")), None)
        t_str = winner_cand["temp"] if winner_cand else "?"
        rows.append(
            f"| {i:3d} | {mark} | {r['judge_score']:5.1f} | "
            f"T={t_str} | {r['english_text'][:55]} → {r['pred'][:40]} |"
        )

    report = f"""# MIPROv2 Optimization Results

**Date:** {dt.now().strftime('%Y-%m-%d %H:%M')} UTC  
**Optimizer:** MIPROv2 (auto={summary['config']['auto']})  
**Trainset:** {summary['config']['trainset_size']} examples  
**Valset:** {summary['config']['valset_size']} examples  
**Num candidates:** {summary['config']['num_candidates']} @ {summary['config']['temperatures']}  
**Context passages:** {summary['config']['num_context_passages']}  
**Trials:** {summary['config'].get('actual_trials', 'N/A')}  
**Log dir:** {summary['config']['log_dir']}  

## Metrics

| Metric | Value |
|--------|-------|
| Normalized Match | {nm:.1%} ({int(nm * n)}/{n}) |
| Exact Match | {em:.1%} ({int(em * n)}/{n}) |
| Avg Judge Score | {avg_j:.1f}/100 |

## Timing

| | |
|-|--|
| Compile time | {compile_s:.0f}s ({compile_s / 60:.1f} min) |
| Eval time | {eval_s:.0f}s ({eval_s / 60:.1f} min) |

## Cost

| | |
|-|--|
| Prompt tokens | {summary['cost']['tokens']['prompt_tokens']:,} |
| Completion tokens | {summary['cost']['tokens']['completion_tokens']:,} |
| Total cost | ${sum(summary['cost']['cost_usd'].values()):.4f} |

## Results

| # | NM | Judge | Temp | Sample |
|---|----|-------|------|--------|
"""
    report += "\n".join(rows) + "\n\n## Output Files\n\n- `program.pkl` — Compiled MIPROv2 program\n- `examples.json` — Per-example predictions and scores\n- `run_summary.json` — Machine-readable summary\n- `gepa_logs/` — MIPROv2 Bayesian optimization checkpoint logs\n"

    with open(out_dir / "report.md", "w", encoding="utf-8") as f:
        f.write(report)


def _write_timing_estimate(out_dir: Path, config: dict, compile_time: float, eval_time: float,
                            n_train: int, n_val: int, trials: Optional[int] = None):
    """Write a timing and cost estimate document."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    full_n = 330
    full_compile = compile_time * (full_n / max(n_train, 1))
    full_eval = eval_time * (full_n / max(n_val, 1))

    estimate = f"""# Timing Estimate

**Generated:** {ts}  
**Base:** {n_train} train + {n_val} val sample run

## Observed (this run)

| | Compile | Eval | Total |
|--|---------|------|-------|
| Actual | {compile_time:.0f}s | {eval_time:.0f}s | {compile_time + eval_time:.0f}s |
| Per sample | {compile_time / max(n_train, 1):.2f}s | {eval_time / max(n_val, 1):.2f}s | — |

## Extrapolated (full val set, {full_n} samples)

| | Compile | Eval | Total |
|--|---------|------|-------|
| Estimated | {full_compile:.0f}s ({full_compile / 60:.1f} min) | {full_eval:.0f}s ({full_eval / 60:.1f} min) | {(full_compile + full_eval) / 60:.1f} min |
| Cost (DeepSeek V4 Flash) | — | — | ~$0.27 (auto=light, ~15 trials) |

## Notes

- Compile scales with number of trainset examples (MIPROv2 bootstraps demos per example).
- Eval scales with valset size per trial (minibatch=true uses ~35-sample batches).
- `auto=light` runs ~10-15 Bayesian trials. Each trial runs trainset minibatch
  (~30s) + valset full eval (~2-3 min). Total ~45 min on 50+20 split.
- Resume: run with the SAME `--out-dir` — the shared `gepa_logs/` dir acts as
  the MIPROv2 checkpoint. Bayesian state is reloaded; unfinished trials continue.
- `auto=medium` = ~2× trials, `auto=heavy` = ~4× trials.
"""
    with open(out_dir / "timing_estimate.md", "w", encoding="utf-8") as f:
        f.write(estimate)


def main():
    parser = argparse.ArgumentParser(
        description="MIPROv2 optimization for EnMiradGEPA multi-candidate translation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory. Auto-generated if not provided. Pass SAME dir to resume.",
    )
    parser.add_argument(
        "--auto",
        choices=["light", "medium", "heavy"],
        default="light",
        help="MIPROv2 auto mode (default: light). Sets num_trials automatically.",
    )
    parser.add_argument(
        "--num-trials",
        type=int,
        default=None,
        help="Override number of Bayesian trials (use only with --auto none). "
             "With auto=light: ~10-15 trials; medium: ~20-30; heavy: ~40-60.",
    )
    parser.add_argument(
        "--trainset-size",
        type=int,
        default=None,
        help="Number of trainset examples (default: all from --train-path).",
    )
    parser.add_argument(
        "--train-path",
        type=str,
        default=None,
        help="Path to training set JSON (default: data/eval/train.json).",
    )
    parser.add_argument(
        "--val-path",
        type=str,
        default=None,
        help="Path to val set JSON (default: data/eval/val.json).",
    )
    parser.add_argument(
        "--valset-size",
        type=int,
        default=20,
        help="Number of valset examples for Bayesian scoring (default: 20).",
    )
    parser.add_argument(
        "--num-candidates",
        type=int,
        default=2,
        help="Number of translation candidates (default: 2)",
    )
    parser.add_argument(
        "--temperatures",
        type=float,
        nargs=3,
        default=[0.1, 0.4, 0.8],
        metavar=("T1", "T2", "T3"),
        help="Candidate temperatures (default: 0.1 0.4 0.8)",
    )
    parser.add_argument(
        "--num-context-passages",
        type=int,
        default=3,
        help="Number of context passages for retrieval (default: 3)",
    )
    parser.add_argument(
        "--top-k-per-word",
        type=int,
        default=2,
        help="Semantic lexicon neighbors per word (default: 2; 0 disables semantic expansion)",
    )
    parser.add_argument(
        "--minibatch-size",
        type=int,
        default=35,
        help="MIPROv2 minibatch size for trainset eval (default: 35)",
    )
    parser.add_argument(
        "--max-bootstrapped-demos",
        type=int,
        default=16,
        help="Max bootstrapped demos per predictor (default: 16)",
    )
    parser.add_argument(
        "--max-labeled-demos",
        type=int,
        default=0,
        help="Max labeled demos per predictor (default: 0)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed (default: 42)",
    )
    parser.add_argument(
        "--max-errors",
        type=int,
        default=20,
        help="Max errors before stopping a trial (default: 20)",
    )
    parser.add_argument(
        "--skip-final-eval",
        action="store_true",
        help="Skip full 100-sample eval after optimization (faster, no metrics).",
    )
    args = parser.parse_args()

    # ── Output directory ───────────────────────────────────────────────────
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    if args.out_dir:
        out_dir = Path(args.out_dir)
    else:
        suffix = f"mipro_{args.auto}_{ts}"
        out_dir = OUT_DIR_BASE / suffix
    out_dir.mkdir(parents=True, exist_ok=True)
    gepa_log_dir = str(out_dir / "gepa_logs")
    print(f"\n[OUT] Output directory: {out_dir}")
    print(f"[LOG] MIPROv2 checkpoint dir: {gepa_log_dir}")

    prior = _load_prior_summary(out_dir)
    if prior:
        print(f"[RESUME] Found prior run_summary.json — will attempt to resume MIPROv2 from checkpoint.")
        print(f"  Prior metrics: NM={prior['metrics']['normalized_match']:.1%}, "
              f"EM={prior['metrics']['exact_match']:.1%}")

    # ── Configure LM ─────────────────────────────────────────────────────
    print("\n[LM] Configuring DeepInfra LM...")
    tracker = UsageTracker()
    dspy.settings.usage_tracker = tracker
    lm = _configure_lm()
    print("[LM] Configured")
    print("[COST] Usage tracking enabled (DeepSeek V4 Flash pricing)")

    # ── Load dataset ───────────────────────────────────────────────────────
    train_path = Path(args.train_path) if args.train_path else DEFAULT_TRAIN_PATH
    val_path = Path(args.val_path) if args.val_path else DEFAULT_VAL_PATH

    print(f"\n[DATA] Loading trainset from {train_path}...")
    train_examples = load_eval_pairs(
        train_path,
        min_english_words=0,
        max_samples=args.trainset_size,
        seed=args.seed,
    )
    n_train = len(train_examples)
    print(f"[DATA] Loaded {n_train} train examples")

    print(f"[DATA] Loading valset from {val_path}...")
    val_examples = load_eval_pairs(
        val_path,
        min_english_words=0,
        max_samples=args.valset_size,
        seed=args.seed,
    )
    n_val = len(val_examples)
    print(f"[DATA] Loaded {n_val} val examples")

    # Convert to dspy.Example with mirad_text label
    def to_example(pair: dict) -> dspy.Example:
        return dspy.Example(
            english_text=pair["english_text"],
            mirad_text=pair["mirad_text"],
        ).with_inputs("english_text")

    trainset_dspy = [to_example(p) for p in train_examples]
    valset_dspy = [to_example(p) for p in val_examples]
    print(f"[DATA] Trainset: {n_train} | Valset: {n_val}")

    # ── Build student program ─────────────────────────────────────────────
    # MultiCandidateTranslator has english_text → mirad_text signature,
    # compatible with MIPROv2 and the normalized_match_metric.
    print("\n[BUILD] Building MultiCandidateTranslator student...")
    program = MultiCandidateTranslator(
        num_candidates=args.num_candidates,
        temperatures=args.temperatures,
        num_context_passages=args.num_context_passages,
        top_k_per_word=args.top_k_per_word,
        use_compiled=False,
    )
    print(f"[BUILD] MultiCandidateTranslator: {args.num_candidates} candidates @ {args.temperatures}")

    # ── MIPROv2 optimizer ─────────────────────────────────────────────────
    # log_dir enables checkpoint/resume: same --out-dir on rerun = resume from state
    auto_mode = None if args.num_trials is not None else args.auto
    mipro_num_candidates = args.num_candidates if auto_mode is None else None
    optimizer = MIPROv2(
        metric=normalized_match_metric,
        auto=auto_mode,
        num_candidates=mipro_num_candidates,
        log_dir=gepa_log_dir,
        max_errors=args.max_errors,
        seed=args.seed,
        max_bootstrapped_demos=args.max_bootstrapped_demos,
        max_labeled_demos=args.max_labeled_demos,
        num_threads=24,
        verbose=True,
        track_stats=True,
    )

    # Fix DSPy MIPRO distributions bug: distributions dict only covers predictor_0
    # but the suggest loop generates params for ALL proposers → create_trial fails.
    _patch_mipro_distributions_bug(optimizer)

    print(f"\n[MIPRO] auto={auto_mode}, log_dir={gepa_log_dir}")
    if args.num_trials:
        print(f"[MIPRO] num_trials={args.num_trials} (manual override)")
    else:
        print(f"[MIPRO] num_trials set automatically by auto={args.auto}")

    # ── Compile ───────────────────────────────────────────────────────────
    print("\n[COMPILE] Starting MIPROv2 optimization...")
    compile_start = time.time()

    effective_minibatch_size = min(args.minibatch_size, n_train)
    if effective_minibatch_size != args.minibatch_size:
        print(
            f"[MIPRO] Adjusting minibatch_size {args.minibatch_size} -> {effective_minibatch_size} "
            f"to fit trainset size {n_train}"
        )

    compiled = optimizer.compile(
        student=program,
        trainset=trainset_dspy,
        valset=valset_dspy,
        num_trials=args.num_trials,
        minibatch=True,
        minibatch_size=effective_minibatch_size,
        minibatch_full_eval_steps=8,
        requires_permission_to_run=False,
    )

    compile_elapsed = time.time() - compile_start
    print(f"\n[COMPILE] Done in {compile_elapsed:.0f}s ({compile_elapsed / 60:.1f} min)")

    # ── Save compiled program ─────────────────────────────────────────────
    program_path = out_dir / "program.pkl"
    compiled.save(str(program_path))
    print(f"[SAVE] Program saved → {program_path}")

    # ── Final eval: full 100 val samples ──────────────────────────────────
    if args.skip_final_eval:
        print("\n[SKIP] --skip-final-eval: skipping full evaluation")
        nm_rate = 0.0
        em_rate = 0.0
        avg_judge = 0.0
        eval_elapsed = 0.0
        eval_results = []
    else:
        print("\n[EVAL] Running final evaluation on 100 val samples...")
        eval_target = load_eval_pairs(
            DEFAULT_VAL_PATH,
            min_english_words=0,
            max_samples=100,
            seed=42,
        )
        print(f"[EVAL] {len(eval_target)} examples")

        eval_start = time.time()
        eval_results, eval_elapsed = _evaluate_compiled(compiled, eval_target)
        eval_elapsed = time.time() - eval_start

        nm_hits = sum(1 for r in eval_results if r["normalized_match"])
        em_hits = sum(1 for r in eval_results if r["exact_match"])
        n = len(eval_results)
        nm_rate = nm_hits / n
        em_rate = em_hits / n
        avg_judge = sum(r["judge_score"] for r in eval_results) / n

        print(f"\n[EVAL] Normalized match: {nm_rate:.1%} ({nm_hits}/{n})")
        print(f"[EVAL] Exact match: {em_rate:.1%} ({em_hits}/{n})")
        print(f"[EVAL] Avg judge score: {avg_judge:.1f}")
        print(f"[EVAL] Eval time: {eval_elapsed:.0f}s ({eval_elapsed / 60:.1f} min)")

    # ── Save artifacts ─────────────────────────────────────────────────────
    _save_summary(out_dir, _build_summary(
        config=vars(args),
        metrics={"normalized_match": nm_rate, "exact_match": em_rate, "avg_judge_score": avg_judge},
        timing={"compile_time_s": compile_elapsed, "eval_time_s": eval_elapsed},
        tracker=tracker,
        out_dir=out_dir,
        gepa_log_dir=gepa_log_dir,
    ))
    _save_examples(out_dir, eval_results if eval_results else [])
    _save_report(out_dir, _build_summary(
        config=vars(args),
        metrics={"normalized_match": nm_rate, "exact_match": em_rate, "avg_judge_score": avg_judge},
        timing={"compile_time_s": compile_elapsed, "eval_time_s": eval_elapsed},
        tracker=tracker,
        out_dir=out_dir,
        gepa_log_dir=gepa_log_dir,
    ), eval_results if eval_results else [])
    _write_timing_estimate(out_dir, vars(args), compile_elapsed, eval_elapsed,
                            n_train, n_val)

    print(f"\n[SAVE] All artifacts → {out_dir}")
    print(f"[DONE]")


def _evaluate_compiled(compiled: dspy.Module, eval_pairs: list[dict]) -> tuple[list, float]:
    """Evaluate a compiled program on a list of eval pairs.

    Returns (eval_results, elapsed_seconds).
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import time

    results = []
    errors = []

    def eval_one(pair: dict) -> dict:
        try:
            pred = compiled(english_text=pair["english_text"])
            mirad_pred = str(getattr(pred, "mirad_text", ""))

            def strip(s):
                s = re.sub(r'[.,!?;:()"\'\[\]{}]', "", s)
                return re.sub(r"\s+", " ", s).strip().lower()

            gold = strip(pair["mirad_text"])
            pred_n = strip(mirad_pred)
            nm = 1.0 if gold == pred_n else 0.0
            em = 1.0 if pair["mirad_text"].strip() == mirad_pred.strip() else 0.0

            winner_score = float(getattr(pred, "total_score", 0.0))
            candidates_data = getattr(pred, "candidates", [])

            # Collect candidate summaries
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
                "elapsed_s": 0.0,
            }
        except Exception as exc:
            errors.append({"english_text": pair.get("english_text", ""), "error": str(exc)})
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

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=24) as exc:
        futures = {exc.submit(eval_one, p): p for p in eval_pairs}
        for fut in as_completed(futures):
            results.append(fut.result())
    elapsed = time.time() - t0

    if errors:
        print(f"[EVAL] {len(errors)}/{len(eval_pairs)} examples errored")
        for e in errors[:5]:
            print(f"  ERROR: {e['english_text'][:50]}: {e['error']}")

    return results, elapsed


def _build_summary(config: dict, metrics: dict, timing: dict, tracker, out_dir: Path, gepa_log_dir: str) -> dict:
    import os

    cost_data = {"input": 0.0, "output": 0.0, "cached": 0.0, "total": 0.0}
    tokens = {"prompt_tokens": 0, "prompt_cache_hit_tokens": 0, "completion_tokens": 0}

    try:
        stats = tracker.get_total_usage()
        if stats:
            inp = float(stats.get("prompt_tokens", 0)) * DEEPSEEK_INPUT_PER_1M / 1_000_000
            out = float(stats.get("completion_tokens", 0)) * DEEPSEEK_OUTPUT_PER_1M / 1_000_000
            cached = float(stats.get("prompt_cache_hit_tokens", 0)) * DEEPSEEK_CACHED_PER_1M / 1_000_000
            cost_data = {"input": inp, "output": out, "cached": cached, "total": inp + out + cached}
            tokens = {
                "prompt_tokens": int(stats.get("prompt_tokens", 0)),
                "prompt_cache_hit_tokens": int(stats.get("prompt_cache_hit_tokens", 0)),
                "completion_tokens": int(stats.get("completion_tokens", 0)),
            }
    except Exception:
        pass

    actual_trials = None
    trial_log = out_dir / "gepa_logs" / "trial_results.json"
    if trial_log.exists():
        try:
            with open(trial_log) as f:
                trials_data = json.load(f)
                actual_trials = len(trials_data) if isinstance(trials_data, list) else None
        except Exception:
            pass

    return {
        "optimizer": "MIPROv2",
        "config": {
            "auto": config.get("auto", "light"),
            "num_trials": config.get("num_trials"),
            "actual_trials": actual_trials,
            "trainset_size": config.get("trainset_size", 50),
            "valset_size": config.get("valset_size", 100),
            "minibatch_size": config.get("minibatch_size", 35),
            "num_candidates": config.get("num_candidates", 2),
            "temperatures": config.get("temperatures", [0.1, 0.4, 0.8]),
            "num_context_passages": config.get("num_context_passages", 3),
            "max_bootstrapped_demos": config.get("max_bootstrapped_demos", 16),
            "max_labeled_demos": config.get("max_labeled_demos", 0),
            "seed": config.get("seed", 42),
            "log_dir": gepa_log_dir,
        },
        "metrics": metrics,
        "timing": {
            "compile_time_s": timing["compile_time_s"],
            "compile_time_min": timing["compile_time_s"] / 60,
            "eval_time_s": timing["eval_time_s"],
            "eval_time_min": timing["eval_time_s"] / 60,
        },
        "output": {
            "program_path": str(out_dir / "program.pkl"),
            "log_dir": gepa_log_dir,
        },
        "cost": {
            "model": "deepseek-ai/DeepSeek-V4-Chat",
            "pricing": {
                "input_per_1m": DEEPSEEK_INPUT_PER_1M,
                "output_per_1m": DEEPSEEK_OUTPUT_PER_1M,
                "cached_per_1m": DEEPSEEK_CACHED_PER_1M,
                "currency": "USD",
            },
            "tokens": tokens,
            "cost_usd": cost_data,
            "total_llm_calls": None,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    main()