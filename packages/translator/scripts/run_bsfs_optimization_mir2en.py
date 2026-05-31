#!/usr/bin/env python3
"""
BootstrapFewShot optimization for MiradToEnglishMultiCandidateTranslator
(full pipeline end-to-end, reverse direction).

Config: n_candidates=3, top_k_grammar_rules=3, top_k_relevant_words=0,
        mirad_to_english_normalized_match_metric, max_bootstrapped_demos=28,
        max_rounds=1

Pipeline traced by BootstrapFewShot:
  MiradToEnglishMultiCandidateTranslator.forward()
    → MiradToEnglishModule.forward()  [translator: mir_to_en, num_context=3, top_k_per_word=0]
    → MiradToEnglishCandidateJudge.forward()  [judge scores 3 candidates, picks winner]
    → returns english_text (best candidate)

Dataset: data/eval/train.json (330 pairs, seed-shuffled for reproducibility)
Validation: data/eval/val.json (330 pairs, no overlap with train)

Usage:
    # Dry-run (verify imports + data, no API calls):
    python packages/translator/scripts/run_bsfs_optimization_mir2en.py --dry-run

    # Full run:
    PYTHONPATH=packages/translator/src timeout 5400 python packages/translator/scripts/run_bsfs_optimization_mir2en.py
"""

import json, random, time, re, sys, os
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "translator" / "src"))

# ── Config ────────────────────────────────────────────────────────────────────
CONFIG = {
    "n_candidates": 3,
    "temperatures": [0.1, 0.3, 0.7],
    "num_context_passages": 3,   # top_k_grammar_rules
    "top_k_per_word": 0,          # top_k_relevant_words (disabled for en→mir; same for mir→en)
    "max_bootstrapped_demos": 28,
    "max_labeled_demos": 0,
    "max_rounds": 1,
    "max_errors": 5,              # tolerate transient API failures during bootstrap
    "num_retries": 5,             # LM retry on failure
    "parallel": 32,               # threads for Evaluate
}

# ── Pre-warm: embedding model ─────────────────────────────────────────────────
print("[warmup] Loading embedding model...")
t_warm = time.time()
from mirad_translator.semantic_lexicon import semantic_lookup_structured
_warm = semantic_lookup_structured("the quick brown fox jumps", top_k_per_word=0, include_exact=True)
print(f"[warmup] Embedding model ready in {time.time()-t_warm:.1f}s")

# ── Load env + configure LM with retries ──────────────────────────────────────
from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

import dspy
from mirad_translator.multi_candidate import MiradToEnglishMultiCandidateTranslator
from mirad_translator.evaluate import (
    load_evaluation_set,
    mirad_to_english_normalized_match_metric,
    mirad_to_english_exact_match_metric,
    normalized_match_metric,
    exact_match_metric,
    save_compiled_program,
)

# Suppress LiteLLM redaction noise
import logging
logging.getLogger("LiteLLM").setLevel(logging.ERROR)
logging.getLogger("litellm").setLevel(logging.ERROR)

def make_lm(temperature: float = 0.0) -> dspy.LM:
    api_key = os.environ.get("DEEPINFRA_API_KEY", "")
    if not api_key:
        raise ValueError("DEEPINFRA_API_KEY not set in .env or environment.")
    api_base = os.environ.get("DEEPINFRA_BASE_URL", "https://api.deepinfra.com/v1/openai")
    model = os.environ.get("DEEPINFRA_TRANSLATION_MODEL", "deepseek-ai/DeepSeek-V4-Flash")
    return dspy.LM(
        model=f"openai/{model}",
        temperature=temperature,
        cache=False,
        api_key=api_key,
        api_base=api_base,
        num_retries=CONFIG["num_retries"],
    )

# Configure global LM at temperature 0
lm = make_lm(0.0)
dspy.settings.configure(lm=lm)
print(f"[setup] LM: openai/{os.environ.get('DEEPINFRA_TRANSLATION_MODEL', 'deepseek-ai/DeepSeek-V4-Flash')}, num_retries={CONFIG['num_retries']}")

# ── Build the Mir→En program module ──────────────────────────────────────────
print(f"[setup] Building MiradToEnglishMultiCandidateTranslator (candidates={CONFIG['n_candidates']}, "
      f"temperatures={CONFIG['temperatures']}, num_context_passages={CONFIG['num_context_passages']}, "
      f"top_k_per_word={CONFIG['top_k_per_word']})")
program = MiradToEnglishMultiCandidateTranslator(
    num_candidates=CONFIG["n_candidates"],
    temperatures=CONFIG["temperatures"],
    num_context_passages=CONFIG["num_context_passages"],
    top_k_per_word=CONFIG["top_k_per_word"],
)
program._get_lm(0.0)  # prime (method exists on the Mir→En translator)
print("[setup] Program ready.")

# ── Load datasets ─────────────────────────────────────────────────────────────
def load_mir2en_examples(path: str | Path) -> list[dspy.Example]:
    """Load pairs from a JSON eval file as Mir→En dspy.Example(english_text, mirad_text)."""
    path = Path(path)
    with open(path) as f:
        raw = json.load(f)
    pairs = raw.get("pairs", raw) if isinstance(raw, dict) else raw
    examples = []
    for d in pairs:
        en = d.get("english", "") or d.get("source", "")
        mir = d.get("mirad", "") or d.get("target", "")
        if en and mir:
            # The module takes mirad_text as input; gold english_text is in the example
            examples.append(
                dspy.Example(english_text=en, mirad_text=mir).with_inputs("mirad_text")
            )
    return examples

print("[data] Loading train.json...")
train_examples = load_mir2en_examples("data/eval/train.json")
rng = random.Random(20260526)
rng.shuffle(train_examples)
print(f"[data] {len(train_examples)} training examples")

print("[data] Loading val.json...")
val_examples = load_mir2en_examples("data/eval/val.json")
rng2 = random.Random(20260528)
rng2.shuffle(val_examples)
print(f"[data] {len(val_examples)} validation examples")

# ── Output directory ──────────────────────────────────────────────────────────
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir = PROJECT_ROOT / f"data/eval_results/bsfs_optimization_mir2en_{ts}"
out_dir.mkdir(parents=True, exist_ok=True)
print(f"[output] Output directory: {out_dir}")

# ── Parallel BootstrapFewShot (ThreadPoolExecutor, ~20x faster than sequential) ─
print(f"\n[bsfs] Starting parallel bootstrap — Mirad→English, {len(train_examples)} examples, {CONFIG['parallel']} threads")
print(f"  metric: mirad_to_english_normalized_match_metric")
print(f"  max_bootstrapped_demos={CONFIG['max_bootstrapped_demos']}")
print(f"  max_errors={CONFIG['max_errors']} (aborts if exceeded)")
print(f"  num_retries={CONFIG['num_retries']} (LM-level retry per call)")

from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import threading

# Same parallel bootstrap as run_bsfs_optimization.py:
#   1. deepcopy program → teacher
#   2. ensure all sub-modules initialized so named_predictors() is complete
#   3. build predictor name↔instance map
#   4. run traces (parallel), collect demos per predictor
#   5. inject demos into student predictors
#
# Thread-safety: dspy.context(lm=...) is thread-safe in DSPy 3.x.
# The LM's num_retries handles transient failures; Python-level max_errors
# aborts if too many examples hard-fail after all retries.

t_bootstrap_start = time.time()

teacher = program.deepcopy()
program._ensure_translator()   # init _translator so named_predictors() includes all predictors
teacher._ensure_translator()

# Build predictor→name and name→predictor maps
name2predictor: dict = {}
predictor2name: dict = {}
for (s_name, s_pred), (t_name, t_pred) in zip(
    program.named_predictors(), teacher.named_predictors(), strict=False
):
    assert s_name == t_name, f"Name mismatch: {s_name} vs {t_name}"
    name2predictor[s_name] = None
    predictor2name[id(s_pred)] = s_name   # student predictor
    predictor2name[id(t_pred)] = t_name   # teacher predictor

# Shared state for parallel traces
name2traces: dict[str, list] = {name: [] for name in name2predictor}
error_count = 0
error_lock = threading.Lock()
error_examples = []
num_threads = CONFIG["parallel"]
max_errors = CONFIG["max_errors"]


def _trace_one(example: dspy.Example) -> bool:
    """Trace one Mir→En example through the teacher (thread-safe)."""
    global error_count

    # Snapshot ALL current teacher predictor demos before the forward pass.
    # The forward call may lazily initialize new sub-modules.  Saving/restoring
    # by name via named_predictors() can produce KeyErrors when new predictors
    # appear between the save-loop and restore-loop.  Fix: save/restore by id.
    all_predictors = list(teacher.predictors())
    demos_backup: dict[int, list] = {id(p): list(p.demos) for p in all_predictors}

    # Remove this example from all demos so it doesn't self-fulfill
    for pred in all_predictors:
        pred.demos = [x for x in pred.demos if x != example]

    try:
        with dspy.context(trace=[], lm=lm):
            prediction = teacher(mirad_text=example.mirad_text)

            # Capture trace INSIDE the context block — same reason as En→Mir.
            _trace = dspy.settings.trace

        # Restore demos
        for pred in all_predictors:
            pred.demos = demos_backup[id(pred)]

        if mirad_to_english_normalized_match_metric is not None:
            score = mirad_to_english_normalized_match_metric(example, prediction, trace=None)
            success = bool(score)
        else:
            success = True

        if success:
            for step in _trace:
                predictor, inputs, outputs = step
                try:
                    pred_name = predictor2name[id(predictor)]
                except KeyError:
                    continue
                demo = dspy.Example(augmented=True, **inputs, **outputs)
                name2traces[pred_name].append(demo)
            return True
        return False

    except Exception as exc:
        with error_lock:
            error_count += 1
            current = error_count
            error_examples.append((example, repr(exc)))
        if max_errors is not None and current > max_errors:
            raise RuntimeError(
                f"Bootstrap exceeded max_errors={max_errors} "
                f"(failed on: {error_examples[-1]!r})"
            )
        return False


print(f"[bsfs] Running parallel traces ({num_threads} threads)...")
t_trace_start = time.time()

results_passed = 0
n_to_collect = CONFIG["max_bootstrapped_demos"]

with ThreadPoolExecutor(max_workers=num_threads) as exc:
    futures = {exc.submit(_trace_one, ex): i for i, ex in enumerate(train_examples)}
    for future in tqdm(as_completed(futures), total=len(train_examples),
                       desc="[bsfs] tracing", unit="ex"):
        try:
            if future.result():
                results_passed += 1
        except RuntimeError:
            exc.shutdown(wait=False, cancel_futures=True)
            raise

t_trace = time.time() - t_trace_start

total_demos = sum(len(v) for v in name2traces.values())
demo_counts = {name: len(demos) for name, demos in name2traces.items()}
print(f"[bsfs] Traced {len(train_examples)} examples in {t_trace:.0f}s "
      f"({len(train_examples)/t_trace:.1f} ex/s), "
      f"passed={results_passed}, total_demos={total_demos}, per_predictor={demo_counts}")
if error_count > 0:
    print(f"[bsfs] {error_count} examples failed (max_errors={max_errors})")
    for ex, err in error_examples[:5]:
        print(f"  FAILED: {ex} → {err}")

# Inject demos into the student (mirrors BootstrapFewShot._train)
print(f"[bsfs] Injecting up to {CONFIG['max_bootstrapped_demos']} demos per predictor...")
rng = random.Random(0)
for name, predictor in program.named_predictors():
    demos = name2traces.get(name, [])[:CONFIG["max_bootstrapped_demos"]]
    sample_size = max(0, CONFIG["max_labeled_demos"] - len(demos))
    extra = rng.sample(list(train_examples), sample_size)
    predictor.demos = demos + extra

compiled_program = program
compiled_program._compiled = True

t_bootstrap = time.time() - t_bootstrap_start
print(f"[bsfs] Parallel bootstrap done in {t_bootstrap:.0f}s "
      f"(trace {t_trace:.0f}s, inject {t_bootstrap-t_trace:.1f}s)")

# ── Save compiled program ─────────────────────────────────────────────────────
compiled_path = out_dir / "compiled_program.json"
save_compiled_program(compiled_program, str(compiled_path))
print(f"[bsfs] Compiled program saved → {compiled_path}")

# ── Evaluate on train set ────────────────────────────────────────────────────
print(f"\n[eval] Evaluating compiled program on train set ({len(train_examples)} examples, {CONFIG['parallel']} threads)...")
t_eval_train_start = time.time()

from dspy import Evaluate
train_evaluator = Evaluate(
    devset=train_examples,
    metric=mirad_to_english_normalized_match_metric,
    num_threads=CONFIG["parallel"],
    display_progress=True,
    display_table=0,
)
train_result = train_evaluator(compiled_program)
t_eval_train = time.time() - t_eval_train_start
train_score = train_result.score if hasattr(train_result, "score") else train_result
print(f"[eval] Train — Mir→En Normalized Match: {train_score:.1%} ({int(train_score * len(train_examples))}/{len(train_examples)}) in {t_eval_train:.0f}s")

# ── Evaluate on val set ───────────────────────────────────────────────────────
print(f"\n[eval] Evaluating compiled program on val set ({len(val_examples)} examples, {CONFIG['parallel']} threads)...")
t_eval_val_start = time.time()

val_evaluator = Evaluate(
    devset=val_examples,
    metric=mirad_to_english_normalized_match_metric,
    num_threads=CONFIG["parallel"],
    display_progress=True,
    display_table=0,
)
val_result = val_evaluator(compiled_program)
t_eval_val = time.time() - t_eval_val_start
val_score = val_result.score if hasattr(val_result, "score") else val_result
print(f"[eval] Val — Mir→En Normalized Match: {val_score:.1%} ({int(val_score * len(val_examples))}/{len(val_examples)}) in {t_eval_val:.0f}s")

# ── Exact match ───────────────────────────────────────────────────────────────
print(f"\n[eval] Computing exact match metrics...")
t_em_train_start = time.time()
em_train_evaluator = Evaluate(
    devset=train_examples,
    metric=mirad_to_english_exact_match_metric,
    num_threads=CONFIG["parallel"],
    display_progress=False,
    display_table=0,
)
em_train_result = em_train_evaluator(compiled_program)
em_train_score = em_train_result.score if hasattr(em_train_result, "score") else em_train_result
t_em_train = time.time() - t_em_train_start

t_em_val_start = time.time()
em_val_evaluator = Evaluate(
    devset=val_examples,
    metric=mirad_to_english_exact_match_metric,
    num_threads=CONFIG["parallel"],
    display_progress=False,
    display_table=0,
)
em_val_result = em_val_evaluator(compiled_program)
em_val_score = em_val_result.score if hasattr(em_val_result, "score") else em_val_result
t_em_val = time.time() - t_em_val_start

# ── Save summary ─────────────────────────────────────────────────────────────
total_wall = time.time() - t_bootstrap_start

summary = {
    "config": {
        **CONFIG,
        "model": os.environ.get("DEEPINFRA_TRANSLATION_MODEL", "deepseek-ai/DeepSeek-V4-Flash"),
        "trainset_size": len(train_examples),
        "valset_size": len(val_examples),
        "direction": "mir_to_en",
    },
    "timing": {
        "bootstrap_s": round(t_bootstrap, 1),
        "eval_train_s": round(t_eval_train, 1),
        "eval_val_s": round(t_eval_val, 1),
        "exact_match_train_s": round(t_em_train, 1),
        "exact_match_val_s": round(t_em_val, 1),
        "total_wall_s": round(total_wall, 1),
    },
    "metrics": {
        "train": {
            "normalized_match": round(train_score, 4),
            "exact_match": round(em_train_score, 4),
            "correct_normalized": int(train_score * len(train_examples)),
            "correct_exact": int(em_train_score * len(train_examples)),
            "total": len(train_examples),
        },
        "val": {
            "normalized_match": round(val_score, 4),
            "exact_match": round(em_val_score, 4),
            "correct_normalized": int(val_score * len(val_examples)),
            "correct_exact": int(em_val_score * len(val_examples)),
            "total": len(val_examples),
        },
    },
    "compiled_program_path": str(compiled_path),
    "output_dir": str(out_dir),
    "timestamp": datetime.now().isoformat(),
}

(out_dir / "run_summary.json").write_text(json.dumps(summary, indent=2))

# ── Report ─────────────────────────────────────────────────────────────────────
model_name = os.environ.get("DEEPINFRA_TRANSLATION_MODEL", "deepseek-ai/DeepSeek-V4-Flash")
report = f"""# BootstrapFewShot Optimization — Mirad→English MultiCandidateTranslator

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Model:** openai/{model_name}
**Direction:** Mirad → English
**Trainset:** {len(train_examples)} examples (data/eval/train.json)
**Valset:** {len(val_examples)} examples (data/eval/val.json)

## Config
| Parameter | Value |
|-----------|-------|
| n_candidates | {CONFIG['n_candidates']} |
| temperatures | {CONFIG['temperatures']} |
| num_context_passages (k_grammar) | {CONFIG['num_context_passages']} |
| top_k_per_word (k_vocab) | {CONFIG['top_k_per_word']} |
| max_bootstrapped_demos | {CONFIG['max_bootstrapped_demos']} |
| max_labeled_demos | {CONFIG['max_labeled_demos']} |
| max_rounds | {CONFIG['max_rounds']} |
| max_errors (bootstrap) | {CONFIG['max_errors']} |
| num_retries (LM) | {CONFIG['num_retries']} |
| parallel threads | {CONFIG['parallel']} |

## Timing
| Phase | Duration |
|-------|----------|
| BootstrapFewShot.compile() | {t_bootstrap:.0f}s |
| Eval train (normalized) | {t_eval_train:.0f}s |
| Eval val (normalized) | {t_eval_val:.0f}s |
| Exact match train | {t_em_train:.0f}s |
| Exact match val | {t_em_val:.0f}s |
| **Total wall time** | **{total_wall:.0f}s** |

## Results

### Train set
| Metric | Value |
|--------|-------|
| Normalized Match | {train_score:.1%} ({int(train_score * len(train_examples))}/{len(train_examples)}) |
| Exact Match | {em_train_score:.1%} ({int(em_train_score * len(train_examples))}/{len(train_examples)}) |

### Val set
| Metric | Value |
|--------|-------|
| Normalized Match | {val_score:.1%} ({int(val_score * len(val_examples))}/{len(val_examples)}) |
| Exact Match | {em_val_score:.1%} ({int(em_val_score * len(val_examples))}/{len(val_examples)}) |

## Output
- Compiled program: `{compiled_path}`
- Summary JSON: `{out_dir / "run_summary.json"}`
- Run timestamp: {ts}
"""
(out_dir / "report.md").write_text(report)

# ── Final print ───────────────────────────────────────────────────────────────
print(f"\n{'='*65}")
print(f"MIR→EN BSFS OPTIMIZATION COMPLETE")
print(f"{'='*65}")
print(f"  Bootstrap time:       {t_bootstrap:.0f}s")
print(f"  Train normalized:     {train_score:.1%} ({int(train_score*len(train_examples))}/{len(train_examples)})")
print(f"  Train exact match:    {em_train_score:.1%}")
print(f"  Val normalized:       {val_score:.1%} ({int(val_score*len(val_examples))}/{len(val_examples)})")
print(f"  Val exact match:      {em_val_score:.1%}")
print(f"  Total wall time:      {total_wall:.0f}s")
print(f"  Output:               {out_dir}")
print(f"  Compiled program:     {compiled_path}")
print(f"{'='*65}")