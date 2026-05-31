#!/usr/bin/env python3
"""
BootstrapFewShot optimization for MultiCandidateTranslator (full pipeline end-to-end).

Config: n_candidates=3, top_k_grammar_rules=3, top_k_relevant_words=0,
        normalized_match metric, max_bootstrapped_demos=28, max_rounds=1

Pipeline traced by BootstrapFewShot:
  MultiCandidateTranslator.forward()
    → TranslatorModule.forward()     [translator: n_context=3, top_k_per_word=0]
    → CandidateJudge.forward()       [judge scores 3 candidates, picks winner]
    → returns mirad_text (best candidate)

The optimizer traces all sub-modules and injects bootstrapped demos into
ChainOfThought signatures inside the translator + judge + grammar retriever.

Dataset: data/eval/train.json (330 pairs, seed-shuffled for reproducibility)
Validation: data/eval/val.json (330 pairs, no overlap with train)

Usage:
    # Preview only (no execution):
    python packages/translator/scripts/run_bsfs_optimization.py --dry-run

    # Full run (compile + eval):
    PYTHONPATH=packages/translator/src python packages/translator/scripts/run_bsfs_optimization.py
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
    "top_k_per_word": 0,          # top_k_relevant_words
    "max_bootstrapped_demos": 18,
    "max_labeled_demos": 0,
    "max_rounds": 1,
    "max_errors": 5,              # tolerate transient API failures during bootstrap
    "num_retries": 3,             # LM retry on failure (reduced — saves memory)
    "bootstrap_n": 100,           # number of examples to use for bootstrap
    "train_eval_n": 100,          # number of train examples to evaluate
    "parallel": 16,              # threads for Evaluate; 16 at 9 calls/ex = 144 in-flight
    "max_in_flight": 16,          # semaphore cap — keep ≤16 to stay within ~20 GB RAM at 144 calls
    "max_trace_size": 10000,       # Must be >0 to enable trace collection. 0 disables it entirely.
    "max_tokens": 4096,           # prevent LM response truncation (judge outputs long JSON)
}

# ── Pre-warm: embedding model ─────────────────────────────────────────────────
print("[warmup] Loading embedding model...")
t_warm = time.time()
from mirad_translator.semantic_lexicon import semantic_lookup_structured
_warm = semantic_lookup_structured("the quick brown fox", top_k_per_word=0, include_exact=True)
print(f"[warmup] Embedding model ready in {time.time()-t_warm:.1f}s")

# ── Load env + configure LM with retries ──────────────────────────────────────
from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

import dspy
from mirad_translator.multi_candidate import MultiCandidateTranslator
from mirad_translator.evaluate import (
    load_evaluation_set,
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
        max_tokens=CONFIG["max_tokens"],
    )

# Configure global LM at temperature 0 (prime the LM, temps overridden per-call via dspy.context)
lm = make_lm(0.0)
dspy.settings.configure(lm=lm, max_trace_size=CONFIG["max_trace_size"])
print(f"[setup] LM: openai/{os.environ.get('DEEPINFRA_TRANSLATION_MODEL', 'deepseek-ai/DeepSeek-V4-Flash')}, num_retries={CONFIG['num_retries']}, max_tokens={CONFIG['max_tokens']}, max_trace_size={CONFIG['max_trace_size']}")

# ── Build the program module ──────────────────────────────────────────────────
print(f"[setup] Building MultiCandidateTranslator (candidates={CONFIG['n_candidates']}, "
      f"temperatures={CONFIG['temperatures']}, num_context_passages={CONFIG['num_context_passages']}, "
      f"top_k_per_word={CONFIG['top_k_per_word']})")
program = MultiCandidateTranslator(
    num_candidates=CONFIG["n_candidates"],
    temperatures=CONFIG["temperatures"],
    num_context_passages=CONFIG["num_context_passages"],
    top_k_per_word=CONFIG["top_k_per_word"],
)
# Prime the translator module to avoid lazy-init inside the bootstrap loop
program._get_lm(0.0)
print("[setup] Program ready.")

# ── Load datasets ─────────────────────────────────────────────────────────────
def load_json_examples(path: str | Path) -> list[dspy.Example]:
    """Load pairs from a JSON eval file as dspy.Example(english_text, mirad_text)."""
    path = Path(path)
    with open(path) as f:
        raw = json.load(f)
    pairs = raw.get("pairs", raw) if isinstance(raw, dict) else raw
    examples = []
    for d in pairs:
        en = d.get("english", "") or d.get("source", "")
        mir = d.get("mirad", "") or d.get("target", "")
        if en and mir:
            examples.append(
                dspy.Example(english_text=en, mirad_text=mir).with_inputs("english_text")
            )
    return examples

print("[data] Loading train.json...")
all_train = load_json_examples("data/eval/train.json")
# Seed-shuffle for reproducible ordering
rng = random.Random(20260526)
rng.shuffle(all_train)
# Slice: first N for bootstrap, next N for train eval (disjoint)
bootstrap_examples = all_train[:CONFIG["bootstrap_n"]]
train_eval_examples = all_train[CONFIG["bootstrap_n"]:CONFIG["bootstrap_n"] + CONFIG["train_eval_n"]]
print(f"[data] {len(bootstrap_examples)} bootstrap + {len(train_eval_examples)} train-eval from train.json")

print("[data] Loading val.json...")
val_examples = load_json_examples("data/eval/val.json")
# Shuffle val too (consistent with the split intent), different seed
rng2 = random.Random(20260528)
rng2.shuffle(val_examples)
val_eval_examples = val_examples[:CONFIG["train_eval_n"]]
print(f"[data] {len(val_eval_examples)} val-eval from val.json")

# ── Output directory ──────────────────────────────────────────────────────────
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir = PROJECT_ROOT / f"data/eval_results/bsfs_optimization_{ts}"
out_dir.mkdir(parents=True, exist_ok=True)
print(f"[output] Output directory: {out_dir}")

# ── Parallel BootstrapFewShot (ThreadPoolExecutor, bounded concurrency) ───────
print(f"\n[bsfs] Starting parallel bootstrap — {len(bootstrap_examples)} examples, {CONFIG['parallel']} threads")
print(f"  max_bootstrapped_demos={CONFIG['max_bootstrapped_demos']}")
print(f"  max_errors={CONFIG['max_errors']} (aborts if exceeded)")
print(f"  num_retries={CONFIG['num_retries']} (LM-level retry per call)")
print(f"  max_in_flight={CONFIG['max_in_flight']} (semaphore cap prevents LiteLLM memory flood)")

from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import threading

# Thread-safety:
#   - dspy.context(lm=...) is thread-safe in DSPy 3.x (thread-local overrides).
#   - demos_collected is incremented under demos_lock; all other reads are atomic.
#   - LiteLLM's LM instances each open their own connection pool, so
#     max_in_flight caps in-flight API calls to prevent memory blowup.
#   - Early stopping: once demos_collected >= n_to_collect, remaining
#     futures are cancelled to avoid wasted API calls and memory.

t_bootstrap_start = time.time()

teacher = program.deepcopy()
assert len(program.predictors()) == len(teacher.predictors()), \
    "Student and teacher must have same number of predictors"

# Eagerly initialize the translator so all workers share a warm instance.
# Without this, each of the N threads could race to initialize the same module.
program._ensure_translator()
teacher._ensure_translator()

# Build predictor→name and name→predictor maps
name2predictor: dict = {}
predictor2name: dict = {}
for (s_name, s_pred), (t_name, t_pred) in zip(
    program.named_predictors(), teacher.named_predictors(), strict=False
):
    assert s_name == t_name, f"Name mismatch: {s_name} vs {t_name}"
    name2predictor[s_name] = None
    predictor2name[id(s_pred)] = s_name
    predictor2name[id(t_pred)] = t_name

# Shared state
name2traces: dict[str, list] = {name: [] for name in name2predictor}
error_count = 0
error_lock = threading.Lock()
error_examples = []
num_threads = CONFIG["parallel"]
max_errors = CONFIG["max_errors"]
demos_lock = threading.Lock()   # guards name2traces writes + demos_collected
demos_collected = 0             # total successful traces so far
n_to_collect = CONFIG["max_bootstrapped_demos"]

# Semaphore caps how many traces run concurrently.
# 32 workers × 9 LM calls/trace = 288 in-flight → LiteLLM buffer blowup.
# 16 in-flight × 9 calls = 144 in-flight, fits in ~16 GB RAM comfortably.
_in_flight_semaphore = threading.Semaphore(CONFIG["max_in_flight"])


def _trace_one(example: dspy.Example) -> bool | None:
    """Trace one example through the teacher module (thread-safe, semaphore-bounded).

    Returns True if the example passed (metric == 1.0), False otherwise.
    Raises RuntimeError if errors exceed max_errors.
    Returns None if early-stop signal (enough demos collected).
    """
    global error_count, demos_collected  # allow both read and augmented assign

    # Early stop: check before acquiring the semaphore to avoid unnecessary waiting.
    with demos_lock:
        if demos_collected >= n_to_collect:
            return None

    acquired = _in_flight_semaphore.acquire(timeout=5)
    if not acquired:
        return None  # No slot — early stop, discard future

    try:
        all_predictors = list(teacher.predictors())
        demos_backup: dict[int, list] = {id(p): list(p.demos) for p in all_predictors}

        # Remove this example from all demos so it doesn't self-fulfill
        for pred in all_predictors:
            pred.demos = [x for x in pred.demos if x != example]

        try:
            # NOTE: Read dspy.settings.trace INSIDE the context block — DSPy 3
            # populates it only while the context is active. Reading after exit
            # gives an empty list every time (root cause of total_demos=0).
            _trace = []
            with dspy.context(trace=[], lm=lm):
                prediction = teacher(**example.inputs())
                _trace = list(dspy.settings.trace)

            # Restore demos after context exit (predictors are stable objects)
            for pred in all_predictors:
                pred.demos = demos_backup[id(pred)]

            # Evaluate
            if normalized_match_metric is not None:
                score = normalized_match_metric(example, prediction, trace=None)
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
                    with demos_lock:
                        name2traces[pred_name].append(demo)
                        demos_collected += 1
                        # Check if we have enough; signal early stop
                        if demos_collected >= n_to_collect:
                            print(f"\n[bsfs] Collected {demos_collected} demo slots — cancelling remaining futures.")
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
    finally:
        _in_flight_semaphore.release()


print(f"[bsfs] Running parallel traces ({num_threads} threads, {CONFIG['max_in_flight']} in-flight cap)...")
t_trace_start = time.time()

results_passed = 0
with ThreadPoolExecutor(max_workers=num_threads) as exc:
    futures = {exc.submit(_trace_one, ex): i for i, ex in enumerate(bootstrap_examples)}
    for future in tqdm(as_completed(futures), total=len(bootstrap_examples),
                       desc="[bsfs] tracing", unit="ex"):
        try:
            result = future.result()
            if result is True:
                results_passed += 1
            elif result is None:
                # Early stop: enough demos collected, cancel remaining work
                exc.shutdown(wait=False, cancel_futures=True)
                break
        except RuntimeError:
            exc.shutdown(wait=False, cancel_futures=True)
            raise

t_trace = time.time() - t_trace_start

# Report bootstrap stats
total_demos = sum(len(v) for v in name2traces.values())
demo_counts = {name: len(demos) for name, demos in name2traces.items()}
print(f"[bsfs] Traced {len(bootstrap_examples)} examples in {t_trace:.0f}s "
      f"({len(bootstrap_examples)/t_trace:.1f} ex/s), "
      f"passed={results_passed}, total_demos={total_demos}, per_predictor={demo_counts}")
if error_count > 0:
    print(f"[bsfs] {error_count} examples failed (max_errors={max_errors})")
    for ex, err in error_examples[:5]:
        print(f"  FAILED: {ex} → {err}")

# Inject demos into the student module (mirrors BootstrapFewShot._train)
print(f"[bsfs] Injecting up to {CONFIG['max_bootstrapped_demos']} demos per predictor...")
rng = random.Random(0)
for name, predictor in program.named_predictors():
    demos = name2traces.get(name, [])[:CONFIG["max_bootstrapped_demos"]]

    sample_size = max(0, CONFIG["max_labeled_demos"] - len(demos))
    extra = rng.sample(list(bootstrap_examples), sample_size)
    predictor.demos = demos + extra

compiled_program = program
compiled_program._compiled = True

t_bootstrap = time.time() - t_bootstrap_start
print(f"[bsfs] Parallel bootstrap done in {t_bootstrap:.0f}s "
      f"(trace {t_trace:.0f}s, inject {t_bootstrap-t_trace:.1f}s)")

# ── Save compiled program ─────────────────────────────────────────────────────
compiled_path = out_dir / "compiled_program"
save_compiled_program(compiled_program, str(compiled_path))
print(f"[bsfs] Compiled program saved → {compiled_path}")

# ── Evaluate on train set (compiled) ──────────────────────────────────────────
print(f"\n[eval] Evaluating compiled program on train set ({len(train_eval_examples)} examples, {CONFIG['parallel']} threads)...")
t_eval_train_start = time.time()

from dspy import Evaluate
train_evaluator = Evaluate(
    devset=train_eval_examples,
    metric=normalized_match_metric,
    num_threads=CONFIG["parallel"],
    display_progress=True,
    display_table=0,
)
train_result = train_evaluator(compiled_program)
t_eval_train = time.time() - t_eval_train_start
train_score = train_result.score if hasattr(train_result, "score") else train_result
# Normalize: Evaluate may return raw sum (e.g. 149 for 330 examples) if metric
# returns integers. Convert to [0,1] fraction.
if train_score > 1:
    train_score = train_score / len(train_eval_examples)
print(f"[eval] Train set — Normalized Match: {train_score:.1%} ({int(train_score * len(train_eval_examples))}/{len(train_eval_examples)}) in {t_eval_train:.0f}s")

# ── Evaluate on val set (compiled) ─────────────────────────────────────────────
print(f"\n[eval] Evaluating compiled program on val set ({len(val_eval_examples)} examples, {CONFIG['parallel']} threads)...")
t_eval_val_start = time.time()

val_evaluator = Evaluate(
    devset=val_eval_examples,
    metric=normalized_match_metric,
    num_threads=CONFIG["parallel"],
    display_progress=True,
    display_table=0,
)
val_result = val_evaluator(compiled_program)
t_eval_val = time.time() - t_eval_val_start
val_score = val_result.score if hasattr(val_result, "score") else val_result
if val_score > 1:
    val_score = val_score / len(val_eval_examples)
print(f"[eval] Val set — Normalized Match: {val_score:.1%} ({int(val_score * len(val_eval_examples))}/{len(val_eval_examples)}) in {t_eval_val:.0f}s")

# ── Also compute exact match ──────────────────────────────────────────────────
print(f"\n[eval] Computing exact match metrics...")
t_em_train_start = time.time()
em_train_evaluator = Evaluate(
    devset=train_eval_examples,
    metric=exact_match_metric,
    num_threads=CONFIG["parallel"],
    display_progress=False,
    display_table=0,
)
em_train_result = em_train_evaluator(compiled_program)
em_train_score = em_train_result.score if hasattr(em_train_result, "score") else em_train_result
if em_train_score > 1:
    em_train_score = em_train_score / len(train_eval_examples)
t_em_train = time.time() - t_em_train_start

t_em_val_start = time.time()
em_val_evaluator = Evaluate(
    devset=val_eval_examples,
    metric=exact_match_metric,
    num_threads=CONFIG["parallel"],
    display_progress=False,
    display_table=0,
)
em_val_result = em_val_evaluator(compiled_program)
em_val_score = em_val_result.score if hasattr(em_val_result, "score") else em_val_result
if em_val_score > 1:
    em_val_score = em_val_score / len(val_eval_examples)
t_em_val = time.time() - t_em_val_start

# ── Save summary + config ─────────────────────────────────────────────────────
total_wall = time.time() - t_bootstrap_start

summary = {
    "config": {
        **CONFIG,
        "model": os.environ.get("DEEPINFRA_TRANSLATION_MODEL", "deepseek-ai/DeepSeek-V4-Flash"),
        "trainset_size": len(train_eval_examples),
        "valset_size": len(val_eval_examples),
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
            "correct_normalized": int(train_score * len(train_eval_examples)),
            "correct_exact": int(em_train_score * len(train_eval_examples)),
            "total": len(train_eval_examples),
        },
        "val": {
            "normalized_match": round(val_score, 4),
            "exact_match": round(em_val_score, 4),
            "correct_normalized": int(val_score * len(val_eval_examples)),
            "correct_exact": int(em_val_score * len(val_eval_examples)),
            "total": len(val_eval_examples),
        },
    },
    "compiled_program_path": str(compiled_path),
    "output_dir": str(out_dir),
    "timestamp": datetime.now().isoformat(),
}

(out_dir / "run_summary.json").write_text(json.dumps(summary, indent=2))

# ── Report ────────────────────────────────────────────────────────────────────
model_name = os.environ.get("DEEPINFRA_TRANSLATION_MODEL", "deepseek-ai/DeepSeek-V4-Flash")
report = f"""# BootstrapFewShot Optimization — MultiCandidateTranslator

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Model:** openai/{model_name}
**Trainset:** {len(train_eval_examples)} examples (data/eval/train.json, bootstrap + eval split)
**Valset:** {len(val_eval_examples)} examples (data/eval/val.json)

## Config
| Parameter | Value |
|-----------|-------|
| n_candidates | {CONFIG['n_candidates']} |
| temperatures | {CONFIG['temperatures']} |
| num_context_passages (k_grammar) | {CONFIG['num_context_passages']} |
| top_k_per_word (k_vocab) | {CONFIG['top_k_per_word']} |
| max_bootstrapped_demos | {CONFIG['max_bootstrapped_demos']} |
| max_labeled_demos | {CONFIG['max_labeled_demos']} |
| max_errors (bootstrap) | {CONFIG['max_errors']} |
| num_retries (LM) | {CONFIG['num_retries']} |
| max_tokens | {CONFIG['max_tokens']} |
| parallel threads | {CONFIG['parallel']} |
| max_in_flight | {CONFIG['max_in_flight']} |
| max_trace_size | {CONFIG['max_trace_size']} |
| bootstrap_n | {CONFIG['bootstrap_n']} |
| train_eval_n | {CONFIG['train_eval_n']} |

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
| Normalized Match | {train_score:.1%} ({int(train_score * len(train_eval_examples))}/{len(train_eval_examples)}) |
| Exact Match | {em_train_score:.1%} ({int(em_train_score * len(train_eval_examples))}/{len(train_eval_examples)}) |

### Val set
| Metric | Value |
|--------|-------|
| Normalized Match | {val_score:.1%} ({int(val_score * len(val_eval_examples))}/{len(val_eval_examples)}) |
| Exact Match | {em_val_score:.1%} ({int(em_val_score * len(val_eval_examples))}/{len(val_eval_examples)}) |

## Output
- Compiled program: `{compiled_path}`
- Summary JSON: `{out_dir / "run_summary.json"}`
- Run timestamp: {ts}
"""
(out_dir / "report.md").write_text(report)

# ── Final print ───────────────────────────────────────────────────────────────
print(f"\n{'='*65}")
print(f"BSFS OPTIMIZATION COMPLETE")
print(f"{'='*65}")
print(f"  Bootstrap time:       {t_bootstrap:.0f}s")
print(f"  Train normalized:     {train_score:.1%} ({int(train_score*len(train_eval_examples))}/{len(train_eval_examples)})")
print(f"  Train exact match:    {em_train_score:.1%}")
print(f"  Val normalized:       {val_score:.1%} ({int(val_score*len(val_eval_examples))}/{len(val_eval_examples)})")
print(f"  Val exact match:      {em_val_score:.1%}")
print(f"  Total wall time:      {total_wall:.0f}s")
print(f"  Output:               {out_dir}")
print(f"  Compiled program:     {compiled_path}")
print(f"{'='*65}")