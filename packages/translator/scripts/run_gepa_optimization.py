#!/usr/bin/env python3
"""
GEPA optimization for the English → Mirad multi-candidate translation system.

Single DSPy module (EnMiradGEPA) wrapping MultiCandidateTranslator:
  - Generates N candidates at different temperatures via TranslatorModule
  - Judges each candidate via CandidateJudge
  - Returns the highest-scoring Mirad prediction

GEPA optimizes the translator's generate-prompt and the judge's scoring rubric
against normalized match on the training set.

Usage:
    python run_gepa_optimization.py              # Quick test (3 samples) + timing estimate
    python run_gepa_optimization.py --full       # Run on all 100 train samples
    python run_gepa_optimization.py --test-only   # Run test only, no full estimate

Outputs (in data/eval_results/gepa_optimization_<timestamp>/):
    program.pkl                   — compiled GEPA program (cloudpickle)
    run_summary.json              — config, metrics, timing
    examples.json                 — per-example predictions and scores
    report.md                     — human-readable summary
    timing_estimate.md            — full-run timing extrapolation
    log_dir/                      — raw GEPA optimization logs
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

# ── Project setup ────────────────────────────────────────────────────────────
# Must be 4 levels up: scripts/ → translator/ → packages/ → <repo>/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "translator" / "src"))

load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=True)

import dspy

# ── Constants ────────────────────────────────────────────────────────────────
DATA_PATH = PROJECT_ROOT / "data" / "eval" / "train.json"
GEPA_VAL_PATH = PROJECT_ROOT / "data" / "eval" / "gepa_val_set.json"
BOOTSTRAP_PROGRAM_PATH = PROJECT_ROOT / "data" / "eval_results" / "bsfs_optimization_20260529_141519" / "compiled_program" / "program.pkl"
OUT_DIR_BASE = PROJECT_ROOT / "data" / "eval_results"
TEST_SAMPLE_SIZE = 3      # Quick smoke test
FULL_TRAIN_SIZE = 100     # Full optimization run (on train.json)
GEPA_VAL_SIZE = 20        # Hand-picked GEPA val set size (gepa_val_set.json)

# Default multi-candidate config
DEFAULT_NUM_CANDIDATES = 3
DEFAULT_TEMPERATURES = [0.1, 0.4, 0.8]

# ── DeepSeek V4 Flash pricing (per 1M tokens) ───────────────────────────────
# Used for cost estimation. Update if your API pricing changes.
DEEPSEEK_V4_FLASH_INPUT_PER_1M = 0.10    # $ / 1M input tokens
DEEPSEEK_V4_FLASH_OUTPUT_PER_1M = 0.20   # $ / 1M output tokens
DEEPSEEK_V4_FLASH_CACHED_PER_1M = 0.02    # $ / 1M cached input tokens

# Estimated token counts per predict call (used for pre-run cost estimation).
# These are rough averages; actual counts vary with prompt/response length.
# Based on observed sizes: analyze ≈400 in/200 out, generate ≈500 in/50 out,
# judge ≈600 in/200 out → weighted avg ≈480 in / 150 out.
EST_PROMPT_TOKENS_PER_PREDICT = 480   # avg input tokens per predict() LLM call
EST_COMPLETION_TOKENS_PER_PREDICT = 150  # avg output tokens per predict() LLM call

# Cost per predict call (input + output)
_COST_PER_PREDICT_IN = DEEPSEEK_V4_FLASH_INPUT_PER_1M * EST_PROMPT_TOKENS_PER_PREDICT / 1_000_000
_COST_PER_PREDICT_OUT = DEEPSEEK_V4_FLASH_OUTPUT_PER_1M * EST_COMPLETION_TOKENS_PER_PREDICT / 1_000_000
COST_PER_PREDICT_CALL = _COST_PER_PREDICT_IN + _COST_PER_PREDICT_OUT
# ≈ $0.0000797 per predict call = $0.0797 per 1,000 calls
# Per metric call: 3 predict calls (analyze + generate + judge) per candidate × num_candidates


# ============================================================================
# Metric
# ============================================================================

def _normalize(text: str) -> str:
    """Strip, collapse whitespace, normalize Unicode quotes."""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    return text


def _strip_punct(s: str) -> str:
    """Strip punctuation for normalized match."""
    s = re.sub(r'[.,!?;:()"\'\[\]{}]', "", s)
    return re.sub(r"\s+", " ", s).strip()


def normalized_match(
    example: dspy.Example,
    prediction: dspy.Prediction,
    trace=None,
    pred_name: str | None = None,
    pred_trace=None,
) -> float:
    """
    GEPA-compatible normalized match metric for En→Mir translation.

    Returns 1.0 if the predicted Mirad text matches the gold after
    whitespace/punctuation normalization; 0.0 otherwise.

    GEPA's metric signature (DSPy 3.x):
        metric(example, prediction, trace, pred_name, pred_trace) -> float

    Both fields come from the top-level module forward() return value,
    so prediction.mirad_text is the best candidate selected by the judge.
    """
    gold = _normalize(example.mirad_text)
    pred = _normalize(prediction.mirad_text)
    if gold == pred:
        return 1.0
    return 1.0 if _strip_punct(gold) == _strip_punct(pred) else 0.0


# ============================================================================
# DSPy Module: EnMiradGEPA
# ============================================================================

class EnMiradGEPA(dspy.Module):
    """
    Single DSPy module wrapping the full multi-candidate translation pipeline.

    GEPA optimizes the predictor prompts inside TranslatorModule and
    CandidateJudge by treating them as named DSPy predictors that can be
    traced and instrumented.

    Forward pass:
      1. Translate english_text → N candidates at different temperatures
         (via TranslatorModule at k=3 context passages)
      2. Judge each candidate (via CandidateJudge)
      3. Return the highest-scoring candidate's mirad_text as output

    GEPA metric: normalized_match on mirad_text output.

    Args:
        num_candidates: Number of translation candidates (default 3).
        temperatures: Candidate temperatures (default [0.1, 0.4, 0.8]).
        num_context_passages: Grammar retrieval k (default 3, winning value).
    """

    def __init__(
        self,
        num_candidates: int = DEFAULT_NUM_CANDIDATES,
        temperatures: list[float] | None = None,
        num_context_passages: int = 3,
    ):
        super().__init__()
        from mirad_translator.multi_candidate import MultiCandidateTranslator

        self._mc = MultiCandidateTranslator(
            num_candidates=num_candidates,
            temperatures=temperatures,
            num_context_passages=num_context_passages,
        )

    def forward(self, english_text: str) -> dspy.Prediction:
        """
        Run the full multi-candidate pipeline and return the best translation.

        Returns a dspy.Prediction with fields:
          mirad_text   — highest-judge-score candidate translation
          total_score  — judge's score for the winning candidate (0–100)
          winner_index — index of winning candidate in the candidate list
          candidates   — raw candidate list with judge scores
          rationale    — judge's explanation for the winner
        """
        result = self._mc(english_text=english_text)
        return dspy.Prediction(
            mirad_text=result.mirad_text,
            total_score=result.total_score,
            winner_index=result.winner_index,
            candidates=result.candidates,
            rationale=result.rationale,
        )


# ============================================================================
# Data Loading
# ============================================================================

def load_train_data(
    path: Path = DATA_PATH,
    min_english_words: int = 5,
    max_samples: int = 0,
    seed: int = 20260526,
) -> list[dspy.Example]:
    """
    Load English→Mirad pairs from train.json, filter by word count, and
    convert to dspy.Example objects.

    Args:
        path: Path to train.json (supports {"pairs": [...]} or flat list).
        min_english_words: Minimum English words per sentence.
        max_samples: 0 = all, otherwise cap at this count.
        seed: Random seed for sampling.

    Returns:
        List of dspy.Example with english_text and mirad_text fields.
    """
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    if isinstance(raw, dict) and "pairs" in raw:
        pairs = raw["pairs"]
    elif isinstance(raw, list):
        pairs = raw
    else:
        raise ValueError(f"Unexpected train.json format: {type(raw)}")

    def normalize(d: dict) -> dict:
        english = d.get("english") or d.get("source") or ""
        mirad = d.get("mirad") or d.get("target") or ""
        return {"english": english, "mirad": mirad, "id": d.get("id", "")}

    filtered = [
        normalize(d) for d in pairs
        if len((d.get("english") or d.get("source") or "").split()) >= min_english_words
    ]

    rng = random.Random(seed)
    rng.shuffle(filtered)

    if max_samples > 0:
        filtered = filtered[:max_samples]

    return [
        dspy.Example(english_text=d["english"], mirad_text=d["mirad"], id=d["id"])
        .with_inputs("english_text")
        for d in filtered
    ]


def load_gepa_val_data(path: Path) -> list[dspy.Example]:
    """
    Load the hand-picked 20-example GEPA val set from gepa_val_set.json.

    Each entry has: {id, english, mirad, notes}
    """
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    examples = []
    for item in raw:
        ex = dspy.Example(
            english_text=item["english"],
            mirad_text=item["mirad"],
            id=item.get("id", ""),
        ).with_inputs("english_text")
        examples.append(ex)
    return examples


def load_eval_pairs(
    path: Path,
    *,
    min_english_words: int = 0,
    max_samples: int = 0,
    seed: int = 42,
) -> list[dspy.Example]:
    """Load eval/train/test/val pairs from json and return dspy.Example rows."""
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    if isinstance(raw, dict) and "pairs" in raw:
        pairs = raw["pairs"]
    elif isinstance(raw, list):
        pairs = raw
    else:
        raise ValueError(f"Unexpected dataset format for {path}: {type(raw)}")

    normalized = [
        {
            "english": d.get("english") or d.get("source") or "",
            "mirad": d.get("mirad") or d.get("target") or "",
            "id": d.get("id", ""),
        }
        for d in pairs
    ]

    if min_english_words > 0:
        normalized = [
            d for d in normalized if len(d["english"].split()) >= min_english_words
        ]

    rng = random.Random(seed)
    rng.shuffle(normalized)

    if max_samples > 0:
        normalized = normalized[:max_samples]

    return [
        dspy.Example(english_text=d["english"], mirad_text=d["mirad"], id=d["id"])
        .with_inputs("english_text")
        for d in normalized
    ]


def load_bootstrap_program(path: Path) -> dspy.Module | None:
    """
    Load a compiled bootstrap program from a cloudpickle .pkl file.

    Returns None if the file does not exist; the caller should fall back to
    building EnMiradGEPA from scratch.

    Requires cloudpickle and matching Python version (3.12 was used to save
    bsfs_optimization_20260529_141519; 3.10 may not be able to load it).
    """
    if not path.exists():
        print(f"[BOOTSTRAP] Program not found at {path} — using default student")
        return None
    try:
        import cloudpickle
        with open(path, "rb") as f:
            prog = cloudpickle.load(f)
        print(f"[BOOTSTRAP] Loaded compiled program from {path}")
        print(f"  Type: {type(prog).__name__}")
        print(f"  Predictors: {[type(p).__name__ for p in prog.predictors()]}")
        return prog
    except Exception as e:
        print(f"[BOOTSTRAP] Failed to load program ({e}) — using default student")
        return None


# ============================================================================
# LM Configuration
# ============================================================================

def configure_lm():
    """Configure DeepInfra LM and set as global DSPy LM."""
    api_key = os.environ.get("DEEPINFRA_API_KEY", "")
    api_base = os.environ.get("DEEPINFRA_BASE_URL", "https://api.deepinfra.com/v1/openai")

    if not api_key:
        raise ValueError(
            "DEEPINFRA_API_KEY not set. Add it to .env or the environment."
        )

    lm = dspy.LM(
        model="openai/deepseek-ai/DeepSeek-V4-Flash",
        api_key=api_key,
        api_base=api_base,
        num_retries=5,
        cache=True,
    )
    dspy.settings.configure(lm=lm)
    return lm


# ============================================================================
# GEPA Compilation
# ============================================================================

def run_gepa(
    student: dspy.Module,
    trainset: list[dspy.Example],
    *,
    auto: str = "light",
    num_threads: int = 24,
    log_dir: str | None = None,
    track_stats: bool = True,
    seed: int = 42,
    reflection_lm: dspy.LM | None = None,
    valset: list[dspy.Example] | None = None,
) -> tuple[dspy.Module, float]:
    """
    Run GEPA optimization on the student module.

    Args:
        student: The DSPy module to optimize (EnMiradGEPA).
        trainset: Training examples for reflective updates.
        auto: GEPA budget setting — "light" (6 candidates), "medium" (12), "heavy" (18).
        num_threads: Parallel evaluation threads.
        log_dir: Directory for GEPA run logs. Auto-generated if None.
        track_stats: Save detailed per-step statistics.
        seed: Random seed.
        reflection_lm: Language model for GEPA's reflection/instruction-proposing step.
            Uses the configured DeepInfra LM with temperature=1.0, max_tokens=16000
            if not provided.
        valset: Validation set for GEPA's metric evaluation. If None, uses trainset
            (which causes overfitting but is faster for inference-time scaling).
            Using a separate valset is strongly recommended.

    Returns:
        The optimized compiled program (as (compiled, compile_time_s) tuple).
    """
    print(f"\n[GEPA] Configuring optimizer (auto={auto}, threads={num_threads})...")

    # Build reflection LM if not provided
    if reflection_lm is None:
        api_key = os.environ.get("DEEPINFRA_API_KEY", "")
        api_base = os.environ.get("DEEPINFRA_BASE_URL", "https://api.deepinfra.com/v1/openai")
        reflection_lm = dspy.LM(
            model="openai/deepseek-ai/DeepSeek-V4-Flash",
            api_key=api_key,
            api_base=api_base,
            temperature=1.0,
            max_tokens=16000,
            cache=True,
        )

    optimizer_kwargs = dict(
        metric=normalized_match,
        auto=auto,
        num_threads=num_threads,
        log_dir=log_dir,
        track_stats=track_stats,
        seed=seed,
        reflection_lm=reflection_lm,
    )
    # Note: valset is NOT passed to GEPA.__init__() — it goes to compile() only.
    optimizer = dspy.GEPA(**optimizer_kwargs)

    print(f"[GEPA] Compiling {student.__class__.__name__} on {len(trainset)} train samples...")
    print(f"[GEPA] Valset size: {len(valset) if valset else 'trainset (overfitting mode)'}")
    print(f"[GEPA] Estimated metric calls: ~{optimizer.max_metric_calls}")
    print(f"[GEPA] Log directory: {log_dir}")
    print("[GEPA] Starting optimization...")

    compile_start = time.time()
    compile_kwargs = dict(student=student, trainset=trainset)
    if valset is not None:
        compile_kwargs["valset"] = valset
    compiled = optimizer.compile(**compile_kwargs)
    compile_time = time.time() - compile_start

    print(f"[GEPA] Compilation complete in {compile_time:.1f}s ({compile_time / 60:.1f} min)")
    return compiled, compile_time


# ============================================================================
# Evaluation
# ============================================================================

def evaluate(
    program: dspy.Module,
    examples: list[dspy.Example],
    *,
    parallel: int = 1,
    num_candidates: int = DEFAULT_NUM_CANDIDATES,
    temperatures: list[float] = DEFAULT_TEMPERATURES,
) -> tuple[list[dict], float]:
    """
    Evaluate the compiled program on examples and return per-example results.

    Args:
        program: Compiled DSPy program.
        examples: dspy.Example list with english_text and mirad_text.
        parallel: Thread count for eval.
        num_candidates: Must match the program config.
        temperatures: Must match the program config.

    Returns:
        (per_example_results, total_wall_time_s)
    """
    print(f"[EVAL] Running evaluation on {len(examples)} examples (parallel={parallel})...")

    if parallel <= 1:
        results = [_eval_one(program, ex) for ex in examples]
    else:
        from concurrent.futures import ThreadPoolExecutor, as_completed

        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = {
                executor.submit(_eval_one, program, example): i
                for i, example in enumerate(examples)
            }
            results = [None] * len(examples)
            for future in as_completed(futures):
                i = futures[future]
                results[i] = future.result()

    elapsed = sum(r["elapsed_s"] for r in results)
    return results, elapsed


def _eval_one(program: dspy.Module, example: dspy.Example) -> dict:
    """Evaluate a single example, return result dict."""
    t0 = time.time()
    pred = program(english_text=example.english_text)
    elapsed = time.time() - t0

    gold = _normalize(example.mirad_text)
    raw = _normalize(pred.mirad_text)
    nm = 1.0 if gold == raw else (1.0 if _strip_punct(gold) == _strip_punct(raw) else 0.0)
    em = 1.0 if gold == raw else 0.0

    # Collect candidate summaries
    cand_summaries = []
    for c in (pred.candidates or []):
        j = c.get("judge", {})
        cand_summaries.append({
            "temp": c.get("temperature"),
            "mirad": c.get("mirad_text"),
            "total_score": j.get("total_score", 0),
            "grammar": j.get("grammar_score", 0),
            "morphology": j.get("morphology_score", 0),
            "vocab": j.get("vocabulary_score", 0),
            "bleed": j.get("english_bleed_score", 0),
            "complete": j.get("completeness_score", 0),
        })

    return {
        "id": getattr(example, "id", ""),
        "english_text": example.english_text,
        "gold": example.mirad_text,
        "pred": pred.mirad_text,
        "normalized_match": bool(nm),
        "exact_match": bool(em),
        "judge_score": pred.total_score,
        "winner_index": pred.winner_index,
        "rationale": pred.rationale,
        "candidates": cand_summaries,
        "elapsed_s": round(elapsed, 3),
    }


# ============================================================================
# Cost Tracking
# ============================================================================

def compute_cost_from_usage(
    usage_by_model: dict[str, dict],
    price_in: float = DEEPSEEK_V4_FLASH_INPUT_PER_1M,
    price_out: float = DEEPSEEK_V4_FLASH_OUTPUT_PER_1M,
    price_cached: float = DEEPSEEK_V4_FLASH_CACHED_PER_1M,
) -> dict:
    """
    Compute cost breakdown from DSPy UsageTracker token counts.

    Args:
        usage_by_model:  from UsageTracker.get_total_tokens(), e.g.
            {"deepinfra/deepseek-chat": {"prompt_tokens": N, "completion_tokens": M, ...}}
        price_in/out/cached:  price per million tokens (default: DeepSeek V4 Flash)

    Returns a cost breakdown dict with dollar amounts.
    """
    total_input = 0
    total_output = 0
    total_cached = 0
    total_calls = 0

    for model, usage in usage_by_model.items():
        prompt = usage.get("prompt_tokens", 0) or 0
        completion = usage.get("completion_tokens", 0) or 0
        cached = usage.get("prompt_cache_hit_tokens", 0) or 0

        # Un-cached prompt tokens (full price); cached tokens at reduced rate
        uncached_prompt = max(0, prompt - cached)
        total_input += uncached_prompt
        total_cached += cached
        total_output += completion
        total_calls += 1

    cost_input = (total_input / 1_000_000) * price_in
    cost_cached = (total_cached / 1_000_000) * price_cached
    cost_output = (total_output / 1_000_000) * price_out
    cost_total = cost_input + cost_cached + cost_output

    return {
        "model": "deepseek-chat",
        "pricing": {
            "input_per_1m": price_in,
            "output_per_1m": price_out,
            "cached_per_1m": price_cached,
            "currency": "USD",
        },
        "tokens": {
            "prompt_tokens": total_input,
            "prompt_cache_hit_tokens": total_cached,
            "completion_tokens": total_output,
        },
        "cost_usd": {
            "input": round(cost_input, 4),
            "cached": round(cost_cached, 4),
            "output": round(cost_output, 4),
            "total": round(cost_total, 4),
        },
        "total_llm_calls": total_calls,
    }


def estimate_run_cost(
    num_metric_calls: int,
    num_candidates: int = DEFAULT_NUM_CANDIDATES,
    num_predict_per_candidate: int = 3,
) -> dict:
    """
    Estimate cost of a GEPA run before it runs (uses EST_TOKEN constants).

    Returns a dict with cost breakdown and token estimates.
    """
    calls_per_metric = num_candidates * num_predict_per_candidate
    total_calls = num_metric_calls * calls_per_metric

    total_prompt = total_calls * EST_PROMPT_TOKENS_PER_PREDICT
    total_completion = total_calls * EST_COMPLETION_TOKENS_PER_PREDICT

    cost_prompt = (total_prompt / 1_000_000) * DEEPSEEK_V4_FLASH_INPUT_PER_1M
    cost_completion = (total_completion / 1_000_000) * DEEPSEEK_V4_FLASH_OUTPUT_PER_1M
    cost_total = cost_prompt + cost_completion

    return {
        "total_llm_calls": total_calls,
        "total_prompt_tokens": int(total_prompt),
        "total_completion_tokens": int(total_completion),
        "cost_input_usd": round(cost_prompt, 4),
        "cost_output_usd": round(cost_completion, 4),
        "cost_total_usd": round(cost_total, 4),
        "per_predict_call_usd": COST_PER_PREDICT_CALL,
        "calls_per_metric_call": calls_per_metric,
        "pricing_model": "DeepSeek V4 Flash",
    }


# ============================================================================
# Save Results
# ============================================================================

def save_results(
    out_dir: Path,
    compiled: dspy.Module,
    compile_time: float,
    eval_results: list[dict],
    eval_elapsed: float,
    config: dict,
    n_samples: int,
    geoparam_log_dir: str | None = None,
    cost_info: dict | None = None,
) -> dict:
    """
    Save compiled program, run summary, examples, report, and timing estimate.

    Returns the run_summary dict.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── 1. Save compiled program (cloudpickle) ──────────────────────────────
    program_path = out_dir / "program.pkl"
    try:
        import cloudpickle
        with open(program_path, "wb") as f:
            cloudpickle.dump(compiled, f)
        program_saved = True
        print(f"[SAVE] Program saved to {program_path}")
    except Exception as e:
        program_saved = False
        print(f"[SAVE] Program save failed: {e}")

    # ── 2. Compute metrics ──────────────────────────────────────────────────
    n = len(eval_results)
    nm_hits = sum(1 for r in eval_results if r["normalized_match"])
    em_hits = sum(1 for r in eval_results if r["exact_match"])
    nm_rate = nm_hits / n if n else 0
    em_rate = em_hits / n if n else 0
    avg_judge = sum(r["judge_score"] for r in eval_results) / n if n else 0
    avg_elapsed = eval_elapsed / n if n else 0

    # ── 3. Run summary ──────────────────────────────────────────────────────
    summary = {
        "optimizer": "GEPA",
        "config": {
            "auto": config["auto"],
            "num_threads": config["num_threads"],
            "log_dir": geoparam_log_dir,
            "num_candidates": config["num_candidates"],
            "temperatures": config["temperatures"],
            "num_context_passages": config["num_context_passages"],
            "track_stats": config["track_stats"],
            "seed": config["seed"],
            "metric": "normalized_match",
        },
        "data": {
            "n_samples": n_samples,
            "min_english_words": 5,
            "data_path": str(DATA_PATH),
        },
        "metrics": {
            "normalized_match": nm_rate,
            "exact_match": em_rate,
            "avg_judge_score": round(avg_judge, 1),
        },
        "counts": {
            "total": n,
            "normalized_match_correct": nm_hits,
            "exact_match_correct": em_hits,
        },
        "timing": {
            "compile_time_s": round(compile_time, 1),
            "compile_time_min": round(compile_time / 60, 2),
            "eval_time_s": round(eval_elapsed, 1),
            "eval_time_min": round(eval_elapsed / 60, 2),
            "avg_per_sample_s": round(avg_elapsed, 3),
        },
        "output": {
            "program_path": str(program_path) if program_saved else None,
            "log_dir": geoparam_log_dir,
        },
        "cost": cost_info,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "run_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"[SAVE] Summary saved to {out_dir / 'run_summary.json'}")

    # ── 4. Per-example results ───────────────────────────────────────────────
    (out_dir / "examples.json").write_text(
        json.dumps(eval_results, indent=2, ensure_ascii=False)
    )
    print(f"[SAVE] Examples saved to {out_dir / 'examples.json'}")

    # ── 5. Human-readable report ────────────────────────────────────────────
    rows = []
    for i, r in enumerate(eval_results):
        mark = "✓" if r["normalized_match"] else "✗"
        winner_temp = "?"
        if r["candidates"]:
            winner_temp = r["candidates"][r["winner_index"]].get("temp", "?")
        rows.append(
            f"| {i:3d} | {mark} | {r['judge_score']:5.1f} | "
            f"T={winner_temp} | {r['english_text'][:55]} → {r['pred'][:40]} |"
        )

    report = f"""# GEPA Optimization Results

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC  
**Optimizer:** GEPA (auto={config['auto']})  
**Train samples:** {n_samples} (min 5 English words)  
**Num candidates:** {config['num_candidates']} @ {config['temperatures']}  
**Context passages:** {config['num_context_passages']}  
**Threads:** {config['num_threads']}  
**Log dir:** {geoparam_log_dir}  

## Metrics

| Metric | Value |
|--------|-------|
| Normalized Match | {nm_rate:.1%} ({nm_hits}/{n}) |
| Exact Match | {em_rate:.1%} ({em_hits}/{n}) |
| Avg Judge Score | {avg_judge:.1f}/100 |

## Timing

| | |
|-|--|
| Compile time | {compile_time:.0f}s ({compile_time / 60:.1f} min) |
| Eval time | {eval_elapsed:.0f}s ({eval_elapsed / 60:.1f} min) |
| Avg per sample | {avg_elapsed / n:.2f}s |

## Results

| # | NM | Judge | Winner T | Sample |
|---|----|-------|----------|--------|
{chr(10).join(rows)}

## Output Files

- `program.pkl` — Compiled GEPA program (cloudpickle)
- `examples.json` — Per-example predictions and scores
- `run_summary.json` — Machine-readable summary
- `log_dir/` — Raw GEPA optimization logs
"""
    (out_dir / "report.md").write_text(report)
    print(f"[SAVE] Report saved to {out_dir / 'report.md'}")

    return summary


def estimate_full_run_time(
    test_n: int,
    test_compile_s: float,
    test_eval_s: float,
    full_n: int,
    num_threads: int = 24,
    auto: str = "light",
    full_val_n: int = GEPA_VAL_SIZE,
) -> dict:
    """
    Extrapolate full-run timing from a test run.

    The compilation scales with num_trials × minibatch_size + full_evals,
    which is determined by the auto budget formula. The eval phase scales
    linearly with sample count.

    GEPA auto_budget formula (DSPy 3.2.1):
        num_trials = max(2 * (num_preds * 2) * log2(num_candidates), 1.5 * num_candidates)
        total_metric_calls = val_n + num_candidates*5 + num_trials*35

    Args:
        test_n: Number of samples in the test run (on GEPA val set).
        test_compile_s: Compile time in seconds (from test run).
        test_eval_s: Eval time in seconds (from test run, on GEPA val set).
        full_n: Number of train samples for full run (data/eval/train.json).
        num_threads: Thread parallelism used.
        auto: GEPA auto mode ("light", "medium", "heavy").
        full_val_n: Val set size used for GEPA compilation (default: 20).

    Returns:
        dict with estimated times and breakdown.
    """
    AUTO_CANDIDATES = {"light": 6, "medium": 12, "heavy": 18}
    n_candidates = AUTO_CANDIDATES.get(auto, 6)

    # GEPA budget formula (DSPy 3.2.1 gepa.py auto_budget)
    num_preds = 1  # One predictor in TranslatorModule
    import math
    num_trials = max(int(2 * (num_preds * 2) * math.log2(n_candidates)),
                     int(1.5 * n_candidates))

    minibatch_size = 35
    est_metric_calls_full = full_val_n + n_candidates * 5 + num_trials * minibatch_size

    # Per-val-set-eval second: test measured eval on test_n val examples
    per_val_eval_s = (test_eval_s / test_n) if test_n > 0 else 30.0

    # Compile budget is driven by GEPA auto/val settings, not by full_n train sample count.
    # Use measured compile time directly when extrapolating a same-config full run.
    est_full_compile_s = test_compile_s

    # Full eval on trainset: per-sample timing (measured ~73s/sample at 1-thread baseline)
    per_train_sample_s = 73.0
    est_full_eval_s = per_train_sample_s * full_n  # final eval on trainset

    # GEPA compilation time dominates; final eval is secondary
    est_full_total_s = est_full_compile_s + est_full_eval_s

    llm_per_metric_call = 3 * DEFAULT_NUM_CANDIDATES

    est_metric_calls_test = est_metric_calls_full
    est_llm_calls_test = est_metric_calls_test * llm_per_metric_call

    return {
        "auto": auto,
        "num_candidates": n_candidates,
        "num_trials": num_trials,
        "minibatch_size": minibatch_size,
        "est_metric_calls_test": est_metric_calls_test,
        "est_metric_calls_full": est_metric_calls_full,
        "est_llm_calls_test": est_llm_calls_test,
        "est_llm_calls_full": est_metric_calls_full * llm_per_metric_call,
        "test_n": test_n,
        "full_n": full_n,
        "full_val_n": full_val_n,
        "test_compile_s": round(test_compile_s, 1),
        "test_eval_s": round(test_eval_s, 1),
        "est_full_compile_s": round(est_full_compile_s, 1),
        "est_full_eval_s": round(est_full_eval_s, 1),
        "est_val_eval_s": round(per_val_eval_s * full_val_n, 1),
        "est_full_total_s": round(est_full_total_s, 1),
        "est_full_total_min": round(est_full_total_s / 60, 1),
        "num_threads": num_threads,
    }


def write_timing_estimate(out_dir: Path, estimate: dict, full_run_cost: dict | None = None) -> None:
    """Write a human-readable timing + cost estimate document."""
    e = estimate
    report = f"""# GEPA Full-Run Timing Estimate

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC  
**Based on test run:** {e['test_n']} samples, {e['test_compile_s']:.1f}s compile, {e['test_eval_s']:.1f}s eval

---

## GEPA Budget (auto={e['auto']})

| Parameter | Value |
|-----------|-------|
| GEPA candidates (n) | {e['num_candidates']} |
| Num trials (num_trials) | {e['num_trials']} |
| Minibatch size | {e['minibatch_size']} |
| Estimated metric calls (test) | ~{e['est_metric_calls_test']} |
| Estimated metric calls (full) | ~{e['est_metric_calls_full']} |
| Estimated LLM calls (test) | ~{e['est_llm_calls_test']:,} |
| Estimated LLM calls (full) | ~{e['est_llm_calls_full']:,} |

**Formula:** total_calls ≈ V + n×5 + num_trials×35
  where V = valset size, n = candidate count, num_trials = max(2×(num_preds×2)×log₂(n), 1.5n)

---

## Timing Extrapolation

The compile phase budget is determined by the `auto` setting (not by sample count),
so the compile time estimate is the measured test compile time.

The eval phase scales linearly with sample count (each sample runs through
the module once for evaluation).

| Phase | Test ({e['test_n']} samples) | Full ({e['full_n']} samples) |
|-------|------------------------------|-------------------------------|
| Compile | {e['test_compile_s']:.0f}s ({e['test_compile_s']/60:.1f} min) | ~{e['est_full_compile_s']:.0f}s ({e['est_full_compile_s']/60:.1f} min) |
| Eval | {e['test_eval_s']:.0f}s ({e['test_eval_s']/60:.1f} min) | ~{e['est_full_eval_s']:.0f}s ({e['est_full_eval_s']/60:.1f} min) |
| **Total** | **{e['test_compile_s'] + e['test_eval_s']:.0f}s** | **~{e['est_full_total_s']:.0f}s (~{e['est_full_total_min']} min)** |

---

## Per-Sample Breakdown

Each sample evaluation involves:
- {DEFAULT_NUM_CANDIDATES} translation candidates × (generate + judge) = {3 * DEFAULT_NUM_CANDIDATES} LLM calls
- Total: ~{e['est_llm_calls_full']:,} LLM calls for the full run

---

## Caveats

- Compile time is determined by GEPA budget (`auto` setting), not sample count.
  The estimate assumes the test and full run use the same `auto` setting.
- Eval time scales linearly with sample count; actual time depends on API
  latency variance and rate limiting.
- With `num_threads=24`, API parallelism may be limited by DeepInfra rate limits.
  Consider reducing threads if hitting rate limit errors.
- The `auto="heavy"` setting (n=18) would approximately triple the compile time
  vs `auto="light"` (n=6) due to more candidate evaluations.

---

## Recommendation

For an initial run, `auto="light"` is sufficient — the test run validates that
the pipeline works correctly. After confirming the setup, re-run with
`auto="medium"` (12 candidates) for better prompt optimization, or `auto="heavy"`
(18 candidates) for production-quality results.
"""
    if full_run_cost:
        cost_report = f"""
---

## Estimated API Cost (DeepSeek V4 Flash)

**Pricing:** $0.10 input / $0.20 output per 1M tokens (no cache assumed for compile phase)

| Phase | LLM Calls | Prompt Tokens | Completion Tokens | Cost |
|-------|-----------|---------------|-------------------|------|
| Compile (~{e['est_metric_calls_full']} metric calls) | ~{full_run_cost['compile_llm_calls']:,} | ~{full_run_cost['compile_prompt_tokens']:,} | ~{full_run_cost['compile_completion_tokens']:,} | ~${full_run_cost['compile_cost_usd']:.4f} |
| Final trainset eval (100 samples) | ~{full_run_cost['eval_llm_calls']:,} | ~{full_run_cost['eval_prompt_tokens']:,} | ~{full_run_cost['eval_completion_tokens']:,} | ~${full_run_cost['final_eval_cost_usd']:.4f} |
| **Total (compile + trainset eval)** | ~{full_run_cost['total_llm_calls']:,} | — | — | **~${full_run_cost['estimate_total_usd']:.4f}** |

**Notes:**
- Compile phase uses `num_threads=24`; actual calls depend on parallelism.
- Estimate assumes ~480 prompt + ~150 completion tokens per predict() call.
- If DeepInfra caches prompt tokens (~$0.02/1M), actual cost may be lower.
"""
        report += cost_report
    (out_dir / "timing_estimate.md").write_text(report)
    print(f"[SAVE] Timing estimate saved to {out_dir / 'timing_estimate.md'}")


# ============================================================================
# Main
# ============================================================================

def _load_prior_summary(out_dir: Path) -> dict | None:
    summary_path = out_dir / "run_summary.json"
    if not summary_path.exists():
        return None
    try:
        return json.loads(summary_path.read_text())
    except Exception:
        return None


def _resolve_estimate_compile_time(current_compile_time: float, prior_summary: dict | None) -> float:
    if current_compile_time > 0:
        return current_compile_time
    if prior_summary:
        try:
            prior = float(prior_summary.get("timing", {}).get("compile_time_s", 0))
            if prior > 0:
                return prior
        except Exception:
            pass
    return current_compile_time


def main():
    parser = argparse.ArgumentParser(description="GEPA optimization for En→Mir translator")
    parser.add_argument(
        "--test-only",
        action="store_true",
        help="Run quick test only (3 samples), print estimate, exit",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run full optimization on all 100 train samples",
    )
    parser.add_argument(
        "--train-size",
        type=int,
        default=TEST_SAMPLE_SIZE,
        help=f"Number of train samples (default: {TEST_SAMPLE_SIZE} for test, 100 for --full)",
    )
    parser.add_argument(
        "--auto",
        choices=["light", "medium", "heavy"],
        default="light",
        help="GEPA auto budget (default: light)",
    )
    parser.add_argument(
        "--num-candidates",
        type=int,
        default=DEFAULT_NUM_CANDIDATES,
        help=f"Number of translation candidates (default: {DEFAULT_NUM_CANDIDATES})",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=24,
        help="Evaluation threads (default: 24)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory (auto-generated if not provided)",
    )
    parser.add_argument(
        "--val-path",
        type=Path,
        default=GEPA_VAL_PATH,
        help="Path to GEPA val set JSON (default: data/eval/gepa_val_set.json)",
    )
    parser.add_argument(
        "--bootstrap-path",
        type=Path,
        default=BOOTSTRAP_PROGRAM_PATH,
        help="Path to compiled bootstrap program .pkl (default: bsfs_optimization pkl)",
    )
    parser.add_argument(
        "--no-bootstrap",
        action="store_true",
        help="Do not load bootstrap program; build EnMiradGEPA from scratch",
    )
    parser.add_argument(
        "--final-eval-train",
        action="store_true",
        help="After compilation, evaluate on full trainset (slow ~1-2h). Default: eval only on valset (~1 min).",
    )
    parser.add_argument(
        "--eval-only",
        action="store_true",
        help="Skip optimization and evaluate an already-compiled program.",
    )
    parser.add_argument(
        "--eval-set",
        choices=["gepa-val", "val", "test", "train"],
        default="gepa-val",
        help="Dataset to evaluate in --eval-only mode (default: gepa-val).",
    )
    parser.add_argument(
        "--eval-max-samples",
        type=int,
        default=0,
        help="Max examples for --eval-only mode (0 = all available).",
    )
    parser.add_argument(
        "--compiled-program-path",
        type=Path,
        default=None,
        help="Path to compiled program .pkl for --eval-only mode. Defaults to <out-dir>/program.pkl.",
    )
    args = parser.parse_args()

    # Determine run mode
    if args.test_only:
        n_samples = TEST_SAMPLE_SIZE
    elif args.full:
        n_samples = FULL_TRAIN_SIZE
    else:
        n_samples = args.train_size

    # Output directory
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.out_dir:
        out_dir = Path(args.out_dir)
    else:
        suffix = "test" if n_samples == TEST_SAMPLE_SIZE else "full"
        out_dir = OUT_DIR_BASE / f"gepa_optimization_{ts}_{suffix}"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n[OUT] Output directory: {out_dir}")
    prior_summary = _load_prior_summary(out_dir)

    # GEPA log directory (inside out_dir)
    gepa_log_dir = str(out_dir / "gepa_logs")
    print(f"[LOG] GEPA log directory: {gepa_log_dir}")

    if args.eval_only:
        print("\n[EVAL-ONLY] Skipping optimization; loading compiled program...")
        eval_program_path = args.compiled_program_path or (out_dir / "program.pkl")
        compiled = load_bootstrap_program(eval_program_path)
        if compiled is None:
            raise FileNotFoundError(f"Could not load compiled program from {eval_program_path}")

        print("\n[LM] Configuring DeepInfra LM...")
        from dspy.utils.usage_tracker import UsageTracker
        tracker = UsageTracker()
        dspy.settings.usage_tracker = tracker
        configure_lm()
        print("[LM] Configured")
        print("[COST] Usage tracking enabled (DeepSeek V4 Flash pricing)")

        eval_path_map = {
            "gepa-val": GEPA_VAL_PATH,
            "val": PROJECT_ROOT / "data" / "eval" / "val.json",
            "test": PROJECT_ROOT / "data" / "eval" / "test.json",
            "train": DATA_PATH,
        }
        eval_path = eval_path_map[args.eval_set]
        if args.eval_set == "gepa-val":
            eval_target = load_gepa_val_data(eval_path)
        else:
            eval_target = load_eval_pairs(
                eval_path,
                min_english_words=0,
                max_samples=args.eval_max_samples,
                seed=42,
            )
        print(f"\n[EVAL-ONLY] Loaded {len(eval_target)} examples from {eval_path}")
        eval_results, eval_elapsed = evaluate(
            compiled,
            eval_target,
            parallel=args.threads,
            num_candidates=args.num_candidates,
            temperatures=DEFAULT_TEMPERATURES,
        )
        try:
            usage_by_model = tracker.get_total_tokens()
            cost_info = compute_cost_from_usage(usage_by_model)
        except Exception as e:
            cost_info = None
            print(f"\n[COST] Could not collect usage: {e}")

        summary = save_results(
            out_dir=out_dir,
            compiled=compiled,
            compile_time=0.0,
            eval_results=eval_results,
            eval_elapsed=eval_elapsed,
            config={
                "auto": "eval-only",
                "num_threads": args.threads,
                "num_candidates": args.num_candidates,
                "temperatures": DEFAULT_TEMPERATURES,
                "num_context_passages": 3,
                "track_stats": True,
                "seed": 42,
            },
            n_samples=len(eval_target),
            geoparam_log_dir=gepa_log_dir,
            cost_info=cost_info,
        )
        print(
            f"\n[EVAL-ONLY] Normalized match: {summary['metrics']['normalized_match']:.1%} "
            f"({summary['counts']['normalized_match_correct']}/{summary['counts']['total']})"
        )
        print(f"[EVAL-ONLY] Output: {out_dir}")
        return summary

    # ── 0b. Load GEPA val set (used for metric eval during optimization) ─────
    val_path = args.val_path
    if val_path and val_path.exists():
        valset = load_gepa_val_data(val_path)
        print(f"\n[VAL] Loaded {len(valset)} hand-picked val examples from {val_path}")
        for v in valset[:3]:
            print(f"  [{v.id}] {v.english_text[:50]} → {v.mirad_text[:50]}")
    else:
        valset = None
        print(f"\n[VAL] No val set found at {val_path} — using trainset (overfitting mode)")

    # ── 0c. Load compiled bootstrap program (warm start) ────────────────────
    if not args.no_bootstrap and args.bootstrap_path:
        bootstrap_prog = load_bootstrap_program(args.bootstrap_path)
    else:
        bootstrap_prog = None

    # ── 1. Load train data ────────────────────────────────────────────────────
    print(f"\n[DATA] Loading {n_samples} train samples (min 5 English words)...")
    trainset = load_train_data(min_english_words=5, max_samples=n_samples)
    print(f"[DATA] Loaded {len(trainset)} examples")
    if trainset:
        print(f"[DATA] Sample[0]: {trainset[0].english_text[:60]} → {trainset[0].mirad_text}")

    # ── 2. Configure LM ─────────────────────────────────────────────────────
    print("\n[LM] Configuring DeepInfra LM...")
    from dspy.utils.usage_tracker import UsageTracker
    tracker = UsageTracker()
    dspy.settings.usage_tracker = tracker
    configure_lm()
    print("[LM] Configured")
    print("[COST] Usage tracking enabled (DeepSeek V4 Flash pricing)")

    # ── 3. Build student module ─────────────────────────────────────────────
    # Use bootstrap-warmed program if available, otherwise build from scratch.
    # GEPA works with any dspy.Module that has .predictors(); MultiCandidateTranslator
    # (from BootstrapFewShot) and EnMiradGEPA both satisfy this.
    if bootstrap_prog is not None:
        student = bootstrap_prog
        print(f"\n[MODULE] Using bootstrap-warmed program (type={type(student).__name__})")
        print(f"[MODULE] Predictors: {[type(p).__name__ for p in student.predictors()]}")
    else:
        print(f"\n[MODULE] Building EnMiradGEPA (candidates={args.num_candidates})...")
        student = EnMiradGEPA(
            num_candidates=args.num_candidates,
            temperatures=DEFAULT_TEMPERATURES,
            num_context_passages=3,
        )
        print(f"[MODULE] Predictors: {[type(p).__name__ for p in student.predictors()]}")

    # ── 4. Quick baseline eval (unoptimized) ───────────────────────────────
    print("\n[BASELINE] Evaluating unoptimized module on train set...")
    baseline_results, baseline_eval_s = evaluate(
        student, trainset, parallel=1,
        num_candidates=args.num_candidates,
        temperatures=DEFAULT_TEMPERATURES,
    )
    baseline_nm = sum(1 for r in baseline_results if r["normalized_match"])
    baseline_nm_rate = baseline_nm / len(baseline_results)
    print(f"[BASELINE] Normalized match: {baseline_nm_rate:.1%} ({baseline_nm}/{len(baseline_results)})")
    print(f"[BASELINE] Eval time: {baseline_eval_s:.1f}s")

    # ── 5. GEPA compilation ─────────────────────────────────────────────────
    config = {
        "auto": args.auto,
        "num_threads": args.threads,
        "num_candidates": args.num_candidates,
        "temperatures": DEFAULT_TEMPERATURES,
        "num_context_passages": 3,
        "track_stats": True,
        "seed": 42,
        "valset_size": len(valset) if valset else "trainset",
        "bootstrap_program": str(args.bootstrap_path) if not args.no_bootstrap else None,
    }

    print(f"\n[GEPA] Starting compilation...")
    print(f"  auto={args.auto}, threads={args.threads}, candidates={args.num_candidates}")
    print(f"  trainset size: {len(trainset)}")
    print(f"  valset size:   {len(valset) if valset else 'trainset (overfitting mode)'}")

    try:
        compiled, compile_time = run_gepa(
            student=student,
            trainset=trainset,
            auto=args.auto,
            num_threads=args.threads,
            log_dir=gepa_log_dir,
            track_stats=True,
            seed=42,
            valset=valset,
        )
    except Exception as e:
        print(f"\n[ERROR] GEPA compilation failed: {e}")
        import traceback
        traceback.print_exc()
        # Save what we have before crashing
        save_results(
            out_dir=out_dir,
            compiled=student,  # unoptimized
            compile_time=0,
            eval_results=baseline_results,
            eval_elapsed=baseline_eval_s,
            config=config,
            n_samples=n_samples,
            geoparam_log_dir=gepa_log_dir,
            cost_info=None,
        )
        raise

    # ── 6. Save compiled program ────────────────────────────────────────────
    program_path = out_dir / "program.pkl"
    try:
        import cloudpickle
        with open(program_path, "wb") as f:
            cloudpickle.dump(compiled, f)
        print(f"[SAVE] Compiled program saved to {program_path}")
    except Exception as e:
        print(f"[SAVE] Program save failed: {e}")

    # ── 7. Evaluate compiled program ──────────────────────────────────────────
    # Default: fast eval on hand-picked valset (~1-2 min) to get quick feedback.
    # Use --final-eval-train to also evaluate on the full trainset (~1-2h).
    eval_target = valset if valset else trainset
    eval_label = "valset" if valset else "trainset"
    print(f"\n[EVAL] Evaluating compiled program on {eval_label} ({len(eval_target)} examples)...")
    eval_results, eval_elapsed = evaluate(
        compiled, eval_target, parallel=args.threads,
        num_candidates=args.num_candidates,
        temperatures=DEFAULT_TEMPERATURES,
    )
    nm_hits = sum(1 for r in eval_results if r["normalized_match"])
    nm_rate = nm_hits / len(eval_results)
    print(f"[EVAL] Normalized match: {nm_rate:.1%} ({nm_hits}/{len(eval_results)})")
    print(f"[EVAL] Eval time: {eval_elapsed:.1f}s")

    # Optional: evaluate on full trainset for full-run disclosure
    train_eval_results = None
    if args.final_eval_train and valset:
        print(f"\n[EVAL] Evaluating on full trainset ({len(trainset)} examples, ~1-2h)...")
        train_eval_results, train_eval_elapsed = evaluate(
            compiled, trainset, parallel=args.threads,
            num_candidates=args.num_candidates,
            temperatures=DEFAULT_TEMPERATURES,
        )
        train_nm_hits = sum(1 for r in train_eval_results if r["normalized_match"])
        train_nm_rate = train_nm_hits / len(train_eval_results)
        print(f"[EVAL] Trainset NM: {train_nm_rate:.1%} ({train_nm_hits}/{len(train_eval_results)})")
        print(f"[EVAL] Trainset time: {train_eval_elapsed:.0f}s ({train_eval_elapsed/60:.1f} min)")

    # ── 8. Collect cost info ─────────────────────────────────────────────────
    try:
        usage_by_model = tracker.get_total_tokens()
        cost_info = compute_cost_from_usage(usage_by_model)
        total_cost = cost_info["cost_usd"]["total"]
        calls = cost_info["total_llm_calls"]
        tokens_in = cost_info["tokens"]["prompt_tokens"] + cost_info["tokens"]["prompt_cache_hit_tokens"]
        tokens_out = cost_info["tokens"]["completion_tokens"]
        print(f"\n[COST] LLM calls: {calls:,}")
        print(f"[COST] Tokens: {tokens_in:,} in / {tokens_out:,} out")
        print(f"[COST] Input:  ${cost_info['cost_usd']['input']:.4f} | Cached: ${cost_info['cost_usd']['cached']:.4f} | Output: ${cost_info['cost_usd']['output']:.4f}")
        print(f"[COST] TOTAL: ${total_cost:.4f}")
    except Exception as e:
        cost_info = None
        print(f"\n[COST] Could not collect usage: {e}")

    # ── 9. Save all results ─────────────────────────────────────────────────
    summary = save_results(
        out_dir=out_dir,
        compiled=compiled,
        compile_time=compile_time,
        eval_results=eval_results,
        eval_elapsed=eval_elapsed,
        config=config,
        n_samples=n_samples,
        geoparam_log_dir=gepa_log_dir,
        cost_info=cost_info,
    )

    # ── 9b. Timing & cost estimate ─────────────────────────────────────────────
    val_n = len(valset) if valset else GEPA_VAL_SIZE
    if n_samples == TEST_SAMPLE_SIZE:
        estimate_compile_s = _resolve_estimate_compile_time(compile_time, prior_summary)
        estimate = estimate_full_run_time(
            test_n=TEST_SAMPLE_SIZE,
            test_compile_s=estimate_compile_s,
            test_eval_s=eval_elapsed,
            full_n=FULL_TRAIN_SIZE,
            num_threads=args.threads,
            auto=args.auto,
            full_val_n=val_n,
        )
        cost_estimate = estimate_run_cost(
            num_metric_calls=estimate["est_metric_calls_full"],
            num_candidates=config["num_candidates"],
        )
        eval_cost = estimate_run_cost(
            num_metric_calls=len(trainset) * config["num_candidates"],
            num_candidates=config["num_candidates"],
        )
        full_cost = {
            "estimate_total_usd": round(cost_estimate["cost_total_usd"] + eval_cost["cost_total_usd"], 4),
            "compile_cost_usd": cost_estimate["cost_total_usd"],
            "final_eval_cost_usd": eval_cost["cost_total_usd"],
            "compile_llm_calls": cost_estimate["total_llm_calls"],
            "eval_llm_calls": eval_cost["total_llm_calls"],
            "total_llm_calls": cost_estimate["total_llm_calls"] + eval_cost["total_llm_calls"],
            "compile_prompt_tokens": cost_estimate["total_prompt_tokens"],
            "compile_completion_tokens": cost_estimate["total_completion_tokens"],
            "eval_prompt_tokens": eval_cost["total_prompt_tokens"],
            "eval_completion_tokens": eval_cost["total_completion_tokens"],
            "total_prompt_tokens": cost_estimate["total_prompt_tokens"] + eval_cost["total_prompt_tokens"],
            "total_completion_tokens": cost_estimate["total_completion_tokens"] + eval_cost["total_completion_tokens"],
        }
        write_timing_estimate(out_dir, estimate, full_run_cost=full_cost)

        print(f"\n{'=' * 70}")
        print(f"TIMING & COST ESTIMATE (full run: {FULL_TRAIN_SIZE} train + {val_n} val examples)")
        print("  Model: DeepSeek V4 Flash | $0.10/$0.20 per 1M tokens")
        print(f"{'=' * 70}")
        print(f"  GEPA candidates:   {estimate['num_candidates']} (auto={estimate['auto']})")
        print(f"  Num trials:       {estimate['num_trials']}")
        print(f"  Est metric calls: ~{estimate['est_metric_calls_full']}")
        print(f"  Est LLM calls:    ~{estimate['est_llm_calls_full']:,}")
        print(f"  Est compile:      ~{estimate['est_full_compile_s']:.0f}s ({estimate['est_full_compile_s']/60:.1f} min)")
        print(f"  Est trainset eval: ~{estimate['est_full_eval_s']:.0f}s ({estimate['est_full_eval_s']/60:.1f} min)")
        print(f"  Est total time:    ~{estimate['est_full_total_s']:.0f}s (~{estimate['est_full_total_min']} min)")
        print("  --- Cost ---")
        print(f"  Compile cost:     ~${full_cost['compile_cost_usd']:.4f} ({full_cost['compile_llm_calls']:,} calls)")
        print(f"  Final eval cost:  ~${full_cost['final_eval_cost_usd']:.4f} ({full_cost['eval_llm_calls']:,} calls)")
        print(f"  Est total cost:   ~${full_cost['estimate_total_usd']:.4f} ({full_cost['total_llm_calls']:,} calls)")
        print(f"  Est tokens:        ~{(full_cost['total_prompt_tokens'] + full_cost['total_completion_tokens'])/1000:.1f}K total")
        print(f"{'=' * 70}")
        print(f"\nTo run the full optimization on {FULL_TRAIN_SIZE} train samples:")
        print("  python run_gepa_optimization.py --full")
        print(f"To also evaluate on full trainset after compilation (~{estimate['est_full_eval_s']/60:.0f} min extra, ~${full_cost['final_eval_cost_usd']:.4f}):")
        print("  python run_gepa_optimization.py --full --final-eval-train")
    else:
        print(f"\n[COMPLETE] Full run saved to: {out_dir}")
        print(f"  Normalized match: {nm_rate:.1%} ({nm_hits}/{len(eval_results)})")
        print(f"  Compile time:     {compile_time:.0f}s ({compile_time/60:.1f} min)")
        print(f"  Eval time:        {eval_elapsed:.0f}s ({eval_elapsed/60:.1f} min)")

    # ── 10. Final summary ───────────────────────────────────────────────────
    delta = nm_rate - baseline_nm_rate
    print(f"\n{'=' * 70}")
    print("FINAL RESULTS")
    print(f"{'=' * 70}")
    print(f"  Optimizer:         GEPA (auto={args.auto})")
    print(f"  Samples:           {n_samples}")
    print(f"  Baseline NM:       {baseline_nm_rate:.1%}")
    print(f"  Compiled NM:       {nm_rate:.1%} ({nm_hits}/{len(eval_results)})")
    print(f"  Delta:             {delta:+.1%}")
    print(f"  Compile:           {compile_time:.0f}s ({compile_time/60:.1f} min)")
    if cost_info:
        print(f"  Cost (API):        ${cost_info['cost_usd']['total']:.4f} USD")
        print(f"  LLM calls:         {cost_info['total_llm_calls']:,}")
        print(
            f"  Tokens in/out:     {cost_info['tokens']['prompt_tokens'] + cost_info['tokens']['prompt_cache_hit_tokens']:,} "
            f"/ {cost_info['tokens']['completion_tokens']:,}"
        )
    print(f"  Output:            {out_dir}")
    print(f"{'=' * 70}")

    return summary


if __name__ == "__main__":
    main()
