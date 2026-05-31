#!/usr/bin/env python3
"""
Run 3-candidate LLM-as-judge evaluation (T=0.1, 0.5, 0.9) on 100 samples.

Key architecture (thread-safe DSPy usage):
  - TranslatorModule and CandidateJudge are created ONCE in the main thread
    before the ThreadPoolExecutor is spawned. This avoids dspy.settings
    thread-affinity violations: dspy.settings.configure() can only be called
    from the thread that first configured it.
  - Worker threads receive the pre-built translator + judge as arguments.
  - Per-call temperature override uses dspy.context(lm=...) which IS thread-safe
    and does NOT touch the global dspy.settings singleton.
  - Each thread-local LM is created once via thread_local storage and reused
    for all samples in that thread.

Expected wall time (~100 samples, 3 candidates, parallel=32):
  ~100-300s total (vs ~5000s naive parallel=4 scaling)

Usage:
  python scripts/run_3c_eval.py
  python scripts/run_3c_eval.py --parallel 24
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT / "packages" / "translator" / "src"))


# ── Config ───────────────────────────────────────────────────────────────────

CANDIDATE_TEMPERATURES = [0.1, 0.5, 0.9]
NUM_CANDIDATES = 3
NUM_CONTEXT_PASSAGES = 3
TOP_K_PER_WORD = 0
RANDOM_SEED = 20260526
DEFAULT_PARALLEL = 32
DEFAULT_N_SAMPLES = 100


# ── Thread-local LM cache ───────────────────────────────────────────────────
#
# Each worker thread gets one LM instance (created lazily). Reused across all
# samples assigned to that thread. Avoids repeated dspy.LM() instantiation.

_thread_lm_cache: dict[int, object] = {}  # thread_id -> LM
_cache_lock = threading.Lock()


def _load_env():
    from dotenv import load_dotenv

    dotenv_path = _PROJECT_ROOT / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path, override=False)


def _get_api_key() -> str:
    _load_env()
    key = os.environ.get("DEEPINFRA_API_KEY", "")
    if not key:
        raise ValueError(
            "DEEPINFRA_API_KEY not set. Add it to .env or export it."
        )
    return key


def _get_api_base() -> str:
    _load_env()
    return os.environ.get(
        "DEEPINFRA_BASE_URL", "https://api.deepinfra.com/v1/openai"
    )


def _get_model() -> str:
    _load_env()
    return os.environ.get(
        "DEEPINFRA_TRANSLATION_MODEL", "deepseek-ai/DeepSeek-V4-Flash"
    )


def _make_lm(temperature: float, max_tokens: int | None = None):
    """Create a fresh dspy.LM at the given temperature."""
    import dspy

    kwargs = dict(
        model=_get_model(),
        temperature=temperature,
        cache=True,
        api_key=_get_api_key(),
        api_base=_get_api_base(),
    )
    if max_tokens:
        kwargs["max_tokens"] = max_tokens
    return dspy.LM(**kwargs)


def _get_thread_lm(temperature: float, max_tokens: int | None = None):
    """Get or create a cached LM for the current thread at the given temperature.

    This avoids the overhead of creating a new dspy.LM for every single call.
    Thread-safe via a lock.
    """
    tid = threading.current_thread().ident
    cache_key = (tid, temperature, max_tokens)
    with _cache_lock:
        if cache_key not in _thread_lm_cache:
            _thread_lm_cache[cache_key] = _make_lm(temperature, max_tokens=max_tokens)
        return _thread_lm_cache[cache_key]


# ── Load data ────────────────────────────────────────────────────────────────

def load_samples(n_samples: int = 100, seed: int = RANDOM_SEED) -> list[dict]:
    """Load and sample from data/eval/train.json."""
    with open(_PROJECT_ROOT / "data" / "eval" / "train.json") as f:
        raw = json.load(f)

    pairs = raw.get("pairs", raw) if isinstance(raw, dict) else raw

    def normalize(d):
        return {
            "english": d.get("english", "") or d.get("source", ""),
            "mirad": d.get("mirad", "") or d.get("target", ""),
            "id": d.get("id", ""),
        }

    samples = [normalize(d) for d in pairs]
    rng = random.Random(seed)
    rng.shuffle(samples)
    return samples[:n_samples] if n_samples > 0 else samples


# ── Core eval: per-sample ────────────────────────────────────────────────────
#
# translator and judge are pre-built objects (created in the main thread).
# Temperature override uses dspy.context() — thread-safe, does NOT touch
# dspy.settings.configure().

def eval_one(
    sample: dict,
    translator,  # Pre-built DefaultTranslator (thread-safe DSPy module)
    judge,       # Pre-built CandidateJudge (thread-safe DSPy module)
) -> dict:
    """Evaluate one English sentence: translate at 3 temps, judge, pick best."""
    import dspy

    english = sample["english"]
    gold = sample["mirad"]
    sample_id = sample.get("id", "")

    # Phase 1: generate all 3 candidates (thread-local LM via context)
    # Context and vocabulary are retrieved once on the first call; all temps share them.
    candidates = []
    # Track retrieval metadata from the first call for the example record.
    retrieval_context: list[str] = []
    word_equivalents: dict[str, str] = {}
    relevant_words: dict[str, str] = {}
    back_translation: dict[str, str] = {}
    used_rule_ids: list[str] = []

    for i, temp in enumerate(CANDIDATE_TEMPERATURES):
        lm = _get_thread_lm(temp, max_tokens=2048)
        with dspy.context(lm=lm):
            pred = translator(english_text=english)
        mirad = str(getattr(pred, "mirad_text", ""))

        # Capture retrieval data from the first (T=0.1) call — subsequent calls
        # reuse the same context so deduplication is safe.
        if i == 0:
            retrieval_context = list(getattr(pred, "context", []) or [])
            used_rule_ids = list(getattr(pred, "used_rule_ids", []) or [])
            # Word equivalents uses a 3-section schema:
            #   word_equivalents  = exact English→Mirad matches
            #   relevant_words     = semantic English→Mirad neighbors
            #   back_translation   = Mirad→English reverse lookups
            word_equivalents = dict(getattr(pred, "word_equivalents", {}) or {})
            relevant_words = dict(getattr(pred, "relevant_words", {}) or {})
            back_translation = dict(getattr(pred, "back_translation", {}) or {})

        candidates.append({
            "index": i,
            "temperature": temp,
            "mirad_text": mirad,
            "retrieval_context": retrieval_context,
        })

    # Phase 2: judge all 3 candidates (thread-local LM at T=0)
    judge_lm = _get_thread_lm(0.0, max_tokens=1024)
    winner_index = 0
    winner_score = -1.0
    winner_rationale = ""

    for i, cand in enumerate(candidates):
        with dspy.context(lm=judge_lm):
            pred = judge(original_english=english, candidate_mirad=cand["mirad_text"])
        scores = {
            "grammar_score": _parse_float(pred.grammar_score),
            "morphology_score": _parse_float(pred.morphology_score),
            "vocabulary_score": _parse_float(pred.vocabulary_score),
            "english_bleed_score": _parse_float(pred.english_bleed_score),
            "completeness_score": _parse_float(pred.completeness_score),
            "total_score": _parse_float(pred.total_score),
            "rationale": str(pred.rationale),
        }
        cand["judge"] = scores
        total = scores["total_score"]
        if total > winner_score:
            winner_score = total
            winner_index = i
            winner_rationale = scores["rationale"]

    best = candidates[winner_index]
    mirad_pred = best["mirad_text"]

    # Normalized match
    def nmatch(a, b):
        a_n = re.sub(r"[^a-z0-9]", " ", a.lower())
        b_n = re.sub(r"[^a-z0-9]", " ", b.lower())
        return " ".join(a_n.split()) == " ".join(b_n.split())

    nm = nmatch(mirad_pred, gold)
    em = mirad_pred.strip() == gold.strip()

    cand_summaries = [{
        "temp": c["temperature"],
        "mirad": c["mirad_text"],
        "total_score": c.get("judge", {}).get("total_score", 0),
        "grammar": c.get("judge", {}).get("grammar_score", 0),
        "morphology": c.get("judge", {}).get("morphology_score", 0),
        "vocab": c.get("judge", {}).get("vocabulary_score", 0),
        "bleed": c.get("judge", {}).get("english_bleed_score", 0),
        "complete": c.get("judge", {}).get("completeness_score", 0),
        "retrieval_context": c.get("retrieval_context", []),
    } for c in candidates]

    return {
        "id": sample_id,
        "idx": sample.get("idx", 0),
        "english_text": english,
        "gold": gold,
        "pred": mirad_pred,
        "exact_match": em,
        "normalized_match": nm,
        "winner_index": winner_index,
        "total_score": winner_score,
        "rationale": winner_rationale,
        "candidates": cand_summaries,
        "context": retrieval_context,
        "used_rule_ids": used_rule_ids,
        # 3-section word equivalents schema mirrors _format_word_equivalents():
        #   exact            = exact English→Mirad lookups from the lexicon
        #   relevant_words   = semantic English→Mirad neighbors from embeddings
        #   back_translation = Mirad→English reverse lookups for context
        "word_equivalents": {
            "exact": word_equivalents,
            "relevant_words": relevant_words,
            "back_translation": back_translation,
        },
    }


def _parse_float(value, default: float = 0.0) -> float:
    try:
        s = str(value).strip()
        m = re.search(r"-?\d+(?:\.\d+)?", s)
        if m:
            return float(m.group())
        return default
    except Exception:
        return default


# ── Main ─────────────────────────────────────────────────────────────────────

def run(
    n_samples: int = DEFAULT_N_SAMPLES,
    parallel: int = DEFAULT_PARALLEL,
    seed: int = RANDOM_SEED,
    out_dir: Optional[Path] = None,
) -> dict:
    import dspy
    from mirad_translator.multi_candidate import CandidateJudge
    from mirad_translator.translate import DefaultTranslator

    print(f"[3c_eval] Loading {n_samples} samples (seed={seed})...")
    samples = load_samples(n_samples, seed)
    for i, s in enumerate(samples):
        s["idx"] = i

    # ── MAIN THREAD: build translator + judge before spawning workers ─────────
    #
    # dspy.settings.configure() can ONLY be called from the main thread (the
    # thread that first configured it). Subsequent calls from worker threads
    # raise: "dspy.settings can only be changed by the thread that initially
    # configured it."
    #
    # The fix: configure once here, then use dspy.context(lm=...) in workers.

    print(f"[3c_eval] Building translator + judge in main thread...")
    seed_lm = _make_lm(0.0)
    dspy.settings.configure(lm=seed_lm)  # Main thread only

    translator = DefaultTranslator(
        direction="en_to_mir",
        num_context_passages=NUM_CONTEXT_PASSAGES,
        top_k_per_word=TOP_K_PER_WORD,
        use_compiled=False,
        semantic_lexicon=False,
    )

    judge = CandidateJudge()  # Uses seed_lm via dspy.settings at init time

    print(f"[3c_eval] Running 3-candidate eval ({parallel} workers, "
          f"T={CANDIDATE_TEMPERATURES}) on {len(samples)} samples...")

    t0 = time.time()
    examples: list[dict | None] = [None] * len(samples)

    with ThreadPoolExecutor(max_workers=parallel) as ex:
        # Pass pre-built translator + judge to each worker
        futures = {
            ex.submit(eval_one, s, translator, judge): i
            for i, s in enumerate(samples)
        }
        done = 0
        for future in as_completed(futures):
            i = futures[future]
            try:
                examples[i] = future.result()
            except Exception as exc:
                examples[i] = {
                    "idx": samples[i].get("idx", i),
                    "id": samples[i].get("id", f"err-{i}"),
                    "english_text": samples[i]["english"],
                    "gold": samples[i]["mirad"],
                    "pred": "",
                    "exact_match": False,
                    "normalized_match": False,
                    "winner_index": -1,
                    "total_score": 0,
                    "rationale": "",
                    "candidates": [],
                    "error": str(exc),
                }
            done += 1
            nm = examples[i].get("normalized_match", False)
            score = examples[i].get("total_score", 0)
            en = examples[i].get('english_text', '')[:55]
            print(f"  [{done:3d}/{len(samples)}] "
                  f"{'✓' if nm else '✗'} score={score:5.1f}  {en}")

    wall_s = time.time() - t0

    # Metrics
    n = len(examples)
    nm_count = sum(1 for e in examples if e.get("normalized_match"))
    em_count = sum(1 for e in examples if e.get("exact_match"))
    nm_rate = nm_count / n
    em_rate = em_count / n
    avg_score = sum(e.get("total_score", 0) for e in examples) / n
    error_count = sum(1 for e in examples if e.get("error"))

    summary = {
        "config": {
            "num_candidates": NUM_CANDIDATES,
            "temperatures": CANDIDATE_TEMPERATURES,
            "num_context_passages": NUM_CONTEXT_PASSAGES,
            "top_k_per_word": TOP_K_PER_WORD,
            "parallel": parallel,
            "random_seed": seed,
            "n_samples": n,
        },
        "metrics": {
            "normalized_match": nm_rate,
            "exact_match": em_rate,
            "avg_judge_score": avg_score,
        },
        "counts": {
            "total": n,
            "normalized_match_correct": nm_count,
            "exact_match_correct": em_count,
            "errors": error_count,
        },
        "timing": {
            "total_wall_s": round(wall_s, 1),
            "avg_per_sample_s": round(wall_s / n, 2) if n else 0,
        },
    }

    # Output
    if out_dir is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = _PROJECT_ROOT / "data" / "eval_results" / f"mc_eval_3c_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "run_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    (out_dir / "examples.json").write_text(
        json.dumps(examples, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Report
    rows = []
    for e in examples:
        nm = "✓" if e.get("normalized_match") else "✗"
        score = e.get("total_score", 0)
        winner_temp = "?"
        if e.get("candidates") and e.get("winner_index", -1) >= 0:
            winner_temp = e["candidates"][e["winner_index"]].get("temp", "?")
        rows.append(
            f"| {e.get('idx', 0):3d} | {nm} | {score:5.1f} | "
            f"T={winner_temp} | "
            f"{e.get('english_text', '')[:55]} → {e.get('pred', '')[:40]} |"
        )

    report = f"""# 3-Candidate Translation Eval

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Model:** {_get_model()}
**Samples:** {n} (seed={seed})
**Candidates:** {NUM_CANDIDATES} @ {CANDIDATE_TEMPERATURES}
**Config:** num_context_passages={NUM_CONTEXT_PASSAGES}, top_k_per_word={TOP_K_PER_WORD}
**Parallelism:** {parallel} workers
**Errors:** {error_count}/{n}

## Metrics

| Metric | Value |
|--------|-------|
| Normalized Match | {nm_rate:.1%} ({nm_count}/{n}) |
| Exact Match | {em_rate:.1%} ({em_count}/{n}) |
| Avg Judge Score | {avg_score:.1f}/100 |

## Timing

| | |
|--|--|
| Total wall time | {wall_s:.0f}s |
| Avg per sample | {wall_s/n:.1f}s |
| Samples/sec | {n/wall_s:.1f} |

## Results

| # | NM | Judge | Winner Temp | Sample |
|---|----|-------|-------------|--------|
{chr(10).join(rows)}
"""
    (out_dir / "report.md").write_text(report, encoding="utf-8")

    print(f"\n[3c_eval] Done in {wall_s:.0f}s ({n/wall_s:.1f} samples/sec)")
    print(f"[3c_eval] NM: {nm_rate:.1%}  EM: {em_rate:.1%}  avg judge: {avg_score:.1f}")
    print(f"[3c_eval] Errors: {error_count}/{n}")
    print(f"[3c_eval] Output: {out_dir}")
    print(f"  run_summary.json — config, metrics, timing")
    print(f"  examples.json   — per-example data")
    print(f"  report.md       — human-readable")

    return summary


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Run 3-candidate LLM-as-judge translation eval "
                    "(T=0.1, 0.5, 0.9) on 100 samples."
    )
    p.add_argument("--n", type=int, default=DEFAULT_N_SAMPLES,
                   help="Number of samples (0=all)")
    p.add_argument("--parallel", "-p", type=int, default=DEFAULT_PARALLEL,
                   help="Number of parallel workers (default: 32)")
    p.add_argument("--seed", type=int, default=RANDOM_SEED)
    p.add_argument("--out-dir", type=Path, default=None)

    args = p.parse_args()
    run(
        n_samples=args.n,
        parallel=args.parallel,
        seed=args.seed,
        out_dir=args.out_dir,
    )