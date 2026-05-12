"""DSPy-native evaluation, metrics, and optimization for English→Mirad translation.

Evaluation dataset: data/phrases/english-mirad-sentence-pairs.csv (44 sentence pairs)
Metrics: exact_match, normalized_match (punctuation/whitespace-tolerant)
Optimizers: BootstrapFewShot (starter), MIPROv2 (advanced)

Usage:
    from mirad_translator.evaluate import (
        load_evaluation_set,
        exact_match_metric,
        normalized_match_metric,
        evaluate_module,
        compile_with_bootstrap,
        compile_with_mipro,
    )

CLI entry points:
    from mirad_translator.evaluate import run_baseline_eval, inspect_traces
"""
import csv
import re
import os
import json
from pathlib import Path
from typing import Callable, Optional

import dspy
from dspy import BootstrapFewShot, MIPROv2, Evaluate

from mirad_translator.translate import TranslatorModule, DefaultTranslator

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
EVAL_CSV_PATH = os.environ.get(
    "MIRAD_EVAL_CSV",
    str(_PROJECT_ROOT / "data" / "phrases" / "english-mirad-sentence-pairs.csv"),
)


# ---------------------------------------------------------------------------
# Dataset loading
# ---------------------------------------------------------------------------

def load_evaluation_set(csv_path: Optional[str] = None) -> list[dspy.Example]:
    """Load the English-Mirad sentence pairs from CSV as DSPy Examples.

    Each Example has:
        - english_text: input
        - mirad_text: gold label
    Word equivalents and context are NOT included as input fields — the
    TranslatorModule computes those internally via MiradLexiconLookup and
    MiradContextRetrieve.  This is the DSPy-native pattern: the optimizer
    traces the full pipeline and bootstraps demos with runtime-realistic
    retrieval values.

    Returns:
        List of dspy.Example with .with_inputs('english_text').
    """
    path = Path(csv_path or EVAL_CSV_PATH)
    if not path.exists():
        raise FileNotFoundError(f"Evaluation CSV not found: {path}")

    examples = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            english = row["English"].strip()
            mirad = row["Mirad"].strip()
            if english and mirad:
                examples.append(
                    dspy.Example(
                        english_text=english,
                        mirad_text=mirad,
                    ).with_inputs("english_text")
                )
    return examples


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    """Normalize Mirad text for comparison: strip, collapse whitespace, unify quotes."""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    # Normalize quotation marks: unify smart quotes → straight quotes
    text = text.replace('\u201c', '"').replace('\u201d', '"')  # " " → "
    text = text.replace('\u2018', "'").replace('\u2019', "'")  # ' ' → '
    return text


def exact_match_metric(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    """Exact string match between prediction and gold Mirad translation.

    Returns 1.0 for exact match, 0.0 otherwise.
    Both sides are stripped and collapsed before comparison.
    """
    gold = _normalize(example.mirad_text)
    pred = _normalize(prediction.mirad_text)
    return 1.0 if gold == pred else 0.0


def normalized_match_metric(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    """Punctuation- and whitespace-tolerant match metric.

    Strips all punctuation and normalizes whitespace, then compares.
    Catches cases like trailing periods, comma spacing, etc.
    """
    gold = _normalize(example.mirad_text)
    pred = _normalize(prediction.mirad_text)

    def strip_punct(s: str) -> str:
        # Remove all punctuation except Mirad-specific chars (hyphens in compounds)
        s = re.sub(r'[.,!?;:()"\'\[\]{}]', "", s)
        return re.sub(r"\s+", " ", s).strip()

    return 1.0 if strip_punct(gold) == strip_punct(pred) else 0.0


# ---------------------------------------------------------------------------
# Evaluation runner
# ---------------------------------------------------------------------------

def evaluate_module(
    module: Optional[dspy.Module] = None,
    metric: Optional[Callable] = None,
    devset: Optional[list[dspy.Example]] = None,
    num_threads: int = 1,
    display_progress: bool = True,
    display_table: int = 0,
    save_json: Optional[str] = None,
) -> dict:
    """Run DSPy Evaluate on a TranslatorModule.

    Args:
        module: TranslatorModule to evaluate. Creates DefaultTranslator if None.
        metric: Metric function. Defaults to normalized_match_metric.
        devset: Evaluation dataset. Loads from CSV if None.
        num_threads: Parallel threads for evaluation.
        display_progress: Show progress bar.
        display_table: Number of examples to display in table (0 = none).
        save_json: Path to save evaluation results as JSON.

    Returns:
        Dict with keys: score, results (list of per-example dicts), module_name.
    """
    if module is None:
        module = DefaultTranslator()
    if metric is None:
        metric = normalized_match_metric
    if devset is None:
        devset = load_evaluation_set()

    evaluator = Evaluate(
        devset=devset,
        metric=metric,
        num_threads=num_threads,
        display_progress=display_progress,
        display_table=display_table,
    )
    result = evaluator(module)

    output = {
        "score": result.score if hasattr(result, "score") else result,
        "module_name": type(module).__name__,
        "devset_size": len(devset),
        "metric_name": metric.__name__,
    }

    if save_json:
        import json
        with open(save_json, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

    return output


# ---------------------------------------------------------------------------
# Optimization: BootstrapFewShot
# ---------------------------------------------------------------------------

def compile_with_bootstrap(
    student: Optional[dspy.Module] = None,
    metric: Optional[Callable] = None,
    trainset: Optional[list[dspy.Example]] = None,
    max_bootstrapped_demos: int = 4,
    max_labeled_demos: int = 16,
    max_rounds: int = 1,
) -> dspy.Module:
    """Compile a TranslatorModule with BootstrapFewShot.

    BootstrapFewShot traces the full module execution (including retrieval)
    and generates few-shot demos from successful runs. The resulting compiled
    module includes those demos as context for ChainOfThought.

    Args:
        student: Module to optimize. Creates DefaultTranslator if None.
        metric: Metric for bootstrapping. Defaults to normalized_match_metric.
        trainset: Training examples. Loads from CSV if None.
        max_bootstrapped_demos: Max bootstrapped (traced) demos per predictor.
        max_labeled_demos: Max labeled (direct) demos per predictor.
        max_rounds: Number of bootstrap rounds.

    Returns:
        Compiled dspy.Module with bootstrapped demos.
    """
    if student is None:
        student = TranslatorModule()
    if metric is None:
        metric = normalized_match_metric
    if trainset is None:
        trainset = load_evaluation_set()

    optimizer = BootstrapFewShot(
        metric=metric,
        max_bootstrapped_demos=max_bootstrapped_demos,
        max_labeled_demos=max_labeled_demos,
        max_rounds=max_rounds,
    )
    compiled = optimizer.compile(student, trainset=trainset)
    return compiled


# ---------------------------------------------------------------------------
# CLI entry points
# ---------------------------------------------------------------------------

def _make_ollama_lm(model: str = "qwen3.5:4b") -> "OllamaLM":
    """Create and configure an OllamaLM for DSPy use, suppressing API key redaction noise."""
    from mirad_translator.ollama_lm import OllamaLM
    lm = OllamaLM(model=model)
    return lm


def run_baseline_eval(
    model: str = "qwen3.5:4b",
    metric_name: str = "normalized_match",
    num_threads: int = 4,
    output_path: Optional[str] = None,
) -> dict:
    """Run baseline evaluation with Ollama qwen3.5:4b and save per-example predictions.

    Uses DSPy's native Evaluate with ``save_as_json`` to persist results.
    Runs both ``normalized_match_metric`` and ``exact_match_metric`` so callers
    can compare.  Returns a flat summary dict with score and metric name.

    Args:
        model: Ollama model name (default: qwen3.5:4b).
        metric_name: Which metric to return in the summary. Pass 'exact' or 'exact_match'
                     for exact_match_metric, anything else uses normalized_match_metric.
        num_threads: Parallel threads passed to Evaluate (default 4).
        output_path: Override output path for normalized_match results.
                     Defaults to ``data/eval_results/ollama_baseline.json``.

    Returns:
        Dict with keys: score (float %), metric_name (str), devset_size (int),
        normalized_score (float), exact_score (float).
    """
    _PROJECT_ROOT = Path(__file__).resolve().parents[4]
    out_dir = _PROJECT_ROOT / "data" / "eval_results"
    out_dir.mkdir(parents=True, exist_ok=True)

    norm_path = output_path or str(out_dir / "ollama_baseline.json")
    exact_path = str(out_dir / "ollama_baseline_exact.json")

    # Configure LM — DSPy uses dspy.settings.lm for all Generate tasks
    lm = _make_ollama_lm(model=model)
    dspy.settings.configure(lm=lm)

    devset = load_evaluation_set()
    module = DefaultTranslator()

    # ── normalized_match_metric ──────────────────────────────────────────────
    norm_evaluator = Evaluate(
        devset=devset,
        metric=normalized_match_metric,
        num_threads=num_threads,
        display_progress=True,
        display_table=0,
        save_as_json=norm_path,
    )
    norm_result = norm_evaluator(module)

    # ── exact_match_metric ────────────────────────────────────────────────────
    exact_evaluator = Evaluate(
        devset=devset,
        metric=exact_match_metric,
        num_threads=num_threads,
        display_progress=True,
        display_table=0,
        save_as_json=exact_path,
    )
    exact_result = exact_evaluator(module)

    chosen_metric = "exact_match_metric" if metric_name in ("exact", "exact_match") else "normalized_match_metric"
    chosen_score = exact_result.score if chosen_metric == "exact_match_metric" else norm_result.score

    summary = {
        "score": chosen_score,
        "metric_name": chosen_metric,
        "devset_size": len(devset),
        "normalized_score": norm_result.score,
        "exact_score": exact_result.score,
        "model": model,
        "output_normalized": norm_path,
        "output_exact": exact_path,
    }

    # Also save a summary alongside the per-example results
    summary_path = str(out_dir / "ollama_baseline_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"[run_baseline_eval] normalized={norm_result.score}%  exact={exact_result.score}%")
    print(f"[run_baseline_eval] Results saved to {norm_path}")

    return summary


def inspect_traces(
    model: str = "qwen3.5:4b",
    num_examples: int = 5,
    output_path: Optional[str] = None,
) -> dict:
    """Run the first N examples and log retrieval context + generated output.

    Uses DSPy's native evaluation pipeline so the module receives the same
    retrieval context (word equivalents + ChromaDB chunks) as in full evaluation.
    Writes ``trace_inspection.json`` with per-example: english_text, word_equivalents,
    context_passages, mirad_text, confidence, normalized_score.

    Args:
        model: Ollama model name.
        num_examples: How many first examples to trace (default 5).
        output_path: Override trace output path.
                     Defaults to ``data/eval_results/trace_inspection.json``.

    Returns:
        Dict with keys: traces (list of per-example dicts), lm_history (list of
        the raw messages+responses stored by OllamaLM for each call).
    """
    _PROJECT_ROOT = Path(__file__).resolve().parents[4]
    out_dir = _PROJECT_ROOT / "data" / "eval_results"
    out_dir.mkdir(parents=True, exist_ok=True)
    trace_path = output_path or str(out_dir / "trace_inspection.json")

    lm = _make_ollama_lm(model=model)
    dspy.settings.configure(lm=lm)

    devset = load_evaluation_set()
    examples_to_trace = devset[:num_examples]
    module = DefaultTranslator()

    traces = []
    for example in examples_to_trace:
        prediction = module(example.english_text)
        score = normalized_match_metric(example, prediction)
        traces.append({
            "english_text": example.english_text,
            "gold_mirad": example.mirad_text,
            "predicted_mirad": prediction.mirad_text,
            "confidence": prediction.confidence if hasattr(prediction, "confidence") else None,
            "word_equivalents": prediction.word_equivalents if hasattr(prediction, "word_equivalents") else {},
            "context_passages": prediction.context if hasattr(prediction, "context") else [],
            "normalized_score": score,
        })

    with open(trace_path, "w", encoding="utf-8") as f:
        json.dump({
            "traces": traces,
            "lm_history_count": len(lm.history),
        }, f, indent=2, ensure_ascii=False)

    print(f"[inspect_traces] Traced {len(traces)} examples → {trace_path}")
    for i, t in enumerate(traces):
        print(f"  [{i}] EN: {t['english_text'][:60]!r}")
        print(f"      WE: {t['word_equivalents']}")
        print(f"      CTX: {t['context_passages'][:2] if t['context_passages'] else '[]'}")
        print(f"      PR: {t['predicted_mirad'][:60]!r}  GOLD: {t['gold_mirad'][:60]!r}  score={t['normalized_score']}")

    return {"traces": traces, "lm_history_count": len(lm.history)}