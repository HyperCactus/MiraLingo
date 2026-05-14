"""DSPy-native evaluation, metrics, and optimization for English→Mirad translation.

Evaluation dataset: data/phrases/english-mirad-sentence-pairs.csv (44 sentence pairs)
Metrics: exact_match, normalized_match (punctuation/whitespace-tolerant),
         semantic_similarity (all-MiniLM-L6-v2 cosine similarity on English text)
Optimizers: BootstrapFewShot (starter), MIPROv2 (advanced)

Post-processing:
    TranslatorModule (returned by DefaultTranslator) pipes raw LM output through
    ``postprocess_mirad`` by default, applying:
      - be→bi possessive correction
      - ge→vyel comparative correction
      - Meta-commentary stripping
      - Whitespace/punctuation normalization
    Use ``use_postprocessor=False`` on DefaultTranslator() to get raw output only.

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

from mirad_translator.translate import TranslatorModule, DefaultTranslator, _format_word_equivalents, _format_context_passages

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
EVAL_CSV_PATH = os.environ.get(
    "MIRAD_EVAL_CSV",
    str(_PROJECT_ROOT / "data" / "phrases" / "english-mirad-sentence-pairs.csv"),
)


def save_compiled_program(compiled: dspy.Module, path: str) -> None:
    """Save a compiled DSPy program to a JSON file for later reuse.

    The saved program can be reloaded with ``load_compiled_program``.

    Args:
        compiled: A compiled dspy.Module (e.g. from compile_with_bootstrap).
        path: File path to save to (convention: data/eval_results/compiled_<method>_<config>.json).
    """
    from pathlib import Path
    import datetime

    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    save_data = dspy.export(program=compiled)
    meta = {
        "saved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "module_type": type(compiled).__name__,
        "dspy_version": getattr(dspy, "__version__", "unknown"),
        "note": "Reload with mirad_translator.evaluate.load_compiled_program(path)",
    }

    payload = {**save_data, "_meta": meta}

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"[save_compiled_program] Saved compiled program → {out_path}")


def load_compiled_program(path: str) -> dspy.Module:
    """Reload a compiled DSPy program from a JSON file.

    Args:
        path: Path to the saved JSON file.

    Returns:
        The reloaded compiled dspy.Module.
    """
    with open(path, encoding="utf-8") as f:
        payload = json.load(f)
    # Strip meta before loading
    payload.pop("_meta", None)
    return dspy.load(program=payload)


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
    num_threads: int = 10,
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
    save_path: Optional[str] = None,
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
        save_path: If provided, save the compiled program to this path as JSON.

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

    if save_path:
        save_compiled_program(compiled, save_path)

    return compiled


# ---------------------------------------------------------------------------
# CLI entry points
# ---------------------------------------------------------------------------

def _make_ollama_lm(model: str = "qwen3.5:4b") -> "OllamaLM":
    """Create and configure an OllamaLM for DSPy use, suppressing API key redaction noise."""
    from mirad_translator.ollama_lm import OllamaLM
    lm = OllamaLM(model=model)
    return lm


def _make_deepinfra_lm(model: str | None = None) -> dspy.LM:
    """Create a DSPy LM backed by DeepInfra's OpenAI-compatible API.

    Reads DEEPINFRA_API_KEY, DEEPINFRA_BASE_URL, and DEEPINFRA_TEACHER_MODEL
    from environment variables (or .env file).
    """
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[4] / ".env")

    api_key = os.environ.get("DEEPINFRA_API_KEY")
    api_base = os.environ.get("DEEPINFRA_BASE_URL", "https://api.deepinfra.com/v1/openai")
    teacher_model = model or os.environ.get("DEEPINFRA_TEACHER_MODEL", "deepseek-ai/DeepSeek-V4-Flash")

    if not api_key:
        raise ValueError("DEEPINFRA_API_KEY not set. Add it to .env or environment.")

    lm = dspy.LM(
        model=f"openai/{teacher_model}",
        api_key=api_key,
        api_base=api_base,
    )
    return lm


def run_baseline_eval(
    model: str = "qwen3.5:4b",
    metric_name: str = "normalized_match",
    num_threads: int = 10,
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


# ---------------------------------------------------------------------------
# Enrich examples with pre-computed intermediates for LabeledFewShot
# ---------------------------------------------------------------------------

def _enrich_examples(
    examples: list[dspy.Example],
    db_path=None,
    num_context_passages: int = 0,
) -> list[dspy.Example]:
    """Enrich evaluation examples with pre-computed word_equivalents and context_passages.

    LabeledFewShot requires demos that have all of the signature's input/output fields
    populated. This helper runs lexicon lookup and retrieval for each example to fill
    in ``word_equivalents`` and ``context_passages`` from runtime computation.

    Args:
        examples: Raw examples with english_text + mirad_text only.
        db_path: Path to the lexicon DB.
        num_context_passages: Number of RAG passages (0 disables retrieval).

    Returns:
        List of enriched dspy.Example with all signature fields, configured with
        ``.with_inputs("english_text", "word_equivalents", "context_passages")``.
    """
    module = TranslatorModule(db_path=db_path, num_context_passages=num_context_passages)
    enriched = []
    for ex in examples:
        word_eq_pred = module.lexicon_lookup(english_text=ex.english_text)
        word_equivalents = word_eq_pred.word_equivalents

        ctx_pred = module.context_retrieve(query=ex.english_text)
        context_passages = ctx_pred.passages

        we_str = _format_word_equivalents(word_equivalents)
        ctx_str = _format_context_passages(context_passages)

        enriched.append(
            dspy.Example(
                english_text=ex.english_text,
                word_equivalents=we_str,
                context_passages=ctx_str,
                mirad_text=ex.mirad_text,
            ).with_inputs("english_text", "word_equivalents", "context_passages")
        )
    return enriched


# ---------------------------------------------------------------------------
# LabeledFewShot baseline evaluation
# ---------------------------------------------------------------------------

def run_labeled_fewshot_eval(
    model: str | None = None,
    num_fewshot: int = 5,
    num_threads: int = 1,
    output_path: Optional[str] = None,
    lm_type: str = "ollama",
    save_compiled: Optional[str] = None,
) -> dict:
    """Run LabeledFewShot baseline evaluation with timed execution.

    Splits the 44-pair evaluation set: first ``num_fewshot`` examples become
    labeled demos, the remainder are the eval set. Enriches the few-shot demos
    with pre-computed word equivalents and context passages so LabeledFewShot
    can include them in the prompt. Uses k=0 (no RAG retrieval) to isolate
    the effect of dictionary lookups + few-shot prompting.

    Args:
        model: Model name (default: qwen3.5:4b for Ollama, or DeepInfra teacher model).
        num_fewshot: Number of labeled few-shot examples (default: 5).
        num_threads: Parallel threads for evaluation (default: 1 for timing accuracy).
        output_path: Override output path for results JSON.
        lm_type: "ollama" for local Ollama, "deepinfra" for DeepInfra cloud API.
        save_compiled: If provided, save the compiled program to this path as JSON.

    Returns:
        Dict with normalized_score, exact_score, timing, and per-example results.
    """
    import time

    _PROJECT_ROOT = Path(__file__).resolve().parents[4]
    out_dir = _PROJECT_ROOT / "data" / "eval_results"
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── Configure LM ─────────────────────────────────────────────────────────
    if lm_type == "deepinfra":
        lm = _make_deepinfra_lm(model=model)
    else:
        lm = _make_ollama_lm(model=model)
    dspy.settings.configure(lm=lm)

    # ── Load and split dataset ────────────────────────────────────────────────
    all_examples = load_evaluation_set()
    fewshot_examples = all_examples[:num_fewshot]
    eval_examples = all_examples[num_fewshot:]

    print(f"[run_labeled_fewshot_eval] {num_fewshot} few-shot demos, {len(eval_examples)} eval examples")

    # ── Enrich few-shot examples with pre-computed intermediates ──────────────
    enriched_fewshot = _enrich_examples(fewshot_examples, db_path=None, num_context_passages=0)

    # Print few-shot demo summary
    for i, demo in enumerate(enriched_fewshot):
        we_count = len(demo.word_equivalents.split("\n")) if demo.word_equivalents else 0
        print(f"  Demo {i}: EN={demo.english_text[:50]!r}... WE={we_count} items")

    # ── Build module with k=0 (no RAG retrieval) ──────────────────────────────
    module = DefaultTranslator(num_context_passages=0)

    # ── Compile with LabeledFewShot ───────────────────────────────────────────
    from dspy import LabeledFewShot

    compile_start = time.time()
    optimizer = LabeledFewShot(k=num_fewshot)
    compiled = optimizer.compile(student=module, trainset=enriched_fewshot)
    compile_time = time.time() - compile_start
    print(f"[run_labeled_fewshot_eval] Compile time: {compile_time:.1f}s")

    if save_compiled:
        save_compiled_program(compiled, save_compiled)

    # ── Evaluate on remaining examples ────────────────────────────────────────
    eval_start = time.time()

    # Eval examples only need english_text as input — the module computes intermediates
    norm_evaluator = Evaluate(
        devset=eval_examples,
        metric=normalized_match_metric,
        num_threads=num_threads,
        display_progress=True,
        display_table=0,
    )
    norm_result = norm_evaluator(compiled)

    exact_evaluator = Evaluate(
        devset=eval_examples,
        metric=exact_match_metric,
        num_threads=num_threads,
        display_progress=True,
        display_table=0,
    )
    exact_result = exact_evaluator(compiled)

    eval_time = time.time() - eval_start
    total_time = time.time() - compile_start

    summary = {
        "method": "LabeledFewShot",
        "lm_type": lm_type,
        "model": model,
        "num_fewshot": num_fewshot,
        "k_context_passages": 0,
        "eval_set_size": len(eval_examples),
        "normalized_score": norm_result.score if hasattr(norm_result, "score") else norm_result,
        "exact_score": exact_result.score if hasattr(exact_result, "score") else exact_result,
        "compile_time_s": round(compile_time, 2),
        "eval_time_s": round(eval_time, 2),
        "total_time_s": round(total_time, 2),
    }

    # ── Save results ──────────────────────────────────────────────────────────
    results_path = output_path or str(out_dir / "labeled_fewshot_baseline.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # ── Per-example predictions ────────────────────────────────────────────────
    per_example = []
    for ex in eval_examples:
        pred = compiled(ex.english_text)
        norm_score = normalized_match_metric(ex, pred)
        exact_score = exact_match_metric(ex, pred)
        per_example.append({
            "english_text": ex.english_text,
            "gold_mirad": ex.mirad_text,
            "predicted_mirad": pred.mirad_text,
            "word_equivalents": pred.word_equivalents if hasattr(pred, "word_equivalents") else {},
            "context": pred.context if hasattr(pred, "context") else [],
            "normalized_match": norm_score,
            "exact_match": exact_score,
        })

    per_example_path = str(out_dir / "labeled_fewshot_per_example.json")
    with open(per_example_path, "w", encoding="utf-8") as f:
        json.dump(per_example, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"LabeledFewShot Baseline Results (lm={lm_type}, k=0, {num_fewshot} demos)")
    print(f"{'='*60}")
    print(f"  Model:           {model}")
    print(f"  LM type:          {lm_type}")
    print(f"  Few-shot demos:  {num_fewshot}")
    print(f"  Eval examples:   {len(eval_examples)}")
    print(f"  RAG passages:    0 (disabled)")
    print(f"  Normalized match: {summary['normalized_score']:.1f}%")
    print(f"  Exact match:       {summary['exact_score']:.1f}%")
    print(f"  Compile time:      {compile_time:.1f}s")
    print(f"  Eval time:          {eval_time:.1f}s")
    print(f"  Total time:         {total_time:.1f}s")
    print(f"{'='*60}")
    print(f"Summary saved to {results_path}")
    print(f"Per-example results saved to {per_example_path}")

    return summary


# ---------------------------------------------------------------------------
# Mirad→English reverse evaluation
# ---------------------------------------------------------------------------

def load_reverse_evaluation_set(csv_path: Optional[str] = None) -> list[dspy.Example]:
    """Load the English-Mirad sentence pairs as Mirad→English examples.

    Each Example has:
        - mirad_text: input (the Mirad sentence)
        - english_text: gold label (the English sentence)
    Word equivalents and context are NOT included as input fields — the
    MiradToEnglishModule computes those internally.

    Returns:
        List of dspy.Example with .with_inputs('mirad_text').
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
                        mirad_text=mirad,
                        english_text=english,
                    ).with_inputs("mirad_text")
                )
    return examples


def exact_match_reverse_metric(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    """Exact string match between predicted English and gold English translation.

    Returns 1.0 for exact match, 0.0 otherwise.
    Both sides are stripped and collapsed before comparison.
    """
    gold = _normalize(example.english_text)
    pred = _normalize(prediction.english_text)
    return 1.0 if gold == pred else 0.0


def normalized_match_reverse_metric(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    """Punctuation- and whitespace-tolerant match for Mir→En direction.

    Strips all punctuation and normalizes whitespace, then compares.
    """
    gold = _normalize(example.english_text)
    pred = _normalize(prediction.english_text)

    def strip_punct(s: str) -> str:
        s = re.sub(r'[.,!?;:()"\'][\[\]{}]', "", s)
        return re.sub(r"\s+", " ", s).strip()

    return 1.0 if strip_punct(gold) == strip_punct(pred) else 0.0


# ---------------------------------------------------------------------------
# Semantic similarity metrics (all-MiniLM-L6-v2 cosine similarity)
# ---------------------------------------------------------------------------

_semantic_model = None


def _get_semantic_model():
    """Lazy-load the all-MiniLM-L6-v2 model (same as ChromaDB retrieval)."""
    global _semantic_model
    if _semantic_model is None:
        from sentence_transformers import SentenceTransformer
        _semantic_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _semantic_model


def _cosine_similarity(a, b):
    """Compute cosine similarity between two numpy vectors."""
    import numpy as np
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, norm_b) / (norm_a * norm_b))


def semantic_similarity_metric(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    """Semantic cosine similarity between predicted and gold *English* text.

    Uses all-MiniLM-L6-v2 (the same model used for ChromaDB retrieval) to
    embed both texts and compute cosine similarity. Returns a float in [0, 1].

    Suitable for both En→Mir (comparing predicted translation correctness
    semantically) and Mir→En directions, since English text is compared in
    both cases.
    """
    model = _get_semantic_model()
    gold = _normalize(example.english_text)
    pred = _normalize(prediction.english_text)
    embeddings = model.encode([gold, pred], normalize_embeddings=True)
    import numpy as np
    return float(np.dot(embeddings[0], embeddings[1]))


def semantic_similarity_reverse_metric(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> float:
    """Semantic cosine similarity for Mir→En direction — same as semantic_similarity_metric.

    Included for naming consistency with the reverse metric family.
    Compares predicted English text against gold English text using
    all-MiniLM-L6-v2 embeddings.
    """
    return semantic_similarity_metric(example, prediction, trace=trace)


def run_mir_to_en_baseline_eval(
    model: str | None = None,
    num_fewshot: int = 5,
    num_context_passages: int = 5,
    num_threads: int = 1,
    output_path: Optional[str] = None,
    lm_type: str = "deepinfra",
    save_compiled: Optional[str] = None,
) -> dict:
    """Run baseline Mirad→English evaluation with LabeledFewShot k=5.

    Mirrors run_labeled_fewshot_eval but for the Mir→En direction.
    Uses the same 44-pair eval set with directions reversed: input is
    mirad_text, gold label is english_text.

    Args:
        model: Model name (default: DeepSeek-V4-Flash).
        num_fewshot: Number of labeled few-shot examples (default: 5).
        num_context_passages: Number of RAG context passages (default: 5).
        num_threads: Parallel threads for evaluation (default: 1).
        output_path: Override output path for results JSON.
        lm_type: "deepinfra" for cloud API, "ollama" for local Ollama.
        save_compiled: If provided, save the compiled program to this path as JSON.

    Returns:
        Dict with normalized_score, exact_score, timing, and per-example results.
    """
    import time

    _PROJECT_ROOT = Path(__file__).resolve().parents[4]
    out_dir = _PROJECT_ROOT / "data" / "eval_results"
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── Configure LM ─────────────────────────────────────────────────────────
    if lm_type == "deepinfra":
        lm = _make_deepinfra_lm(model=model)
    else:
        lm = _make_ollama_lm(model=model or "qwen3.5:4b")
    dspy.settings.configure(lm=lm)

    # ── Load and split dataset ────────────────────────────────────────────────
    all_examples = load_reverse_evaluation_set()
    fewshot_examples = all_examples[:num_fewshot]
    eval_examples = all_examples[num_fewshot:]

    print(f"[run_mir_to_en_baseline_eval] {num_fewshot} few-shot demos, {len(eval_examples)} eval examples, k={num_context_passages}")

    # ── Enrich few-shot examples with pre-computed Mir→En intermediates ──────
    from mirad_translator.translate import MiradToEnglishModule
    module = MiradToEnglishModule(num_context_passages=num_context_passages)

    enriched_fewshot = []
    for ex in fewshot_examples:
        we_pred = module.lexicon_lookup(mirad_text=ex.mirad_text)
        word_equivalents = we_pred.word_equivalents
        # Format as Mirad→English
        we_str = "\n".join(f"{mi} → {en}" for mi, en in sorted(word_equivalents.items()))

        ctx_pred = module.context_retrieve(query=ex.mirad_text)
        context_passages = list(ctx_pred.passages)
        ctx_str = _format_context_passages(context_passages)

        enriched_fewshot.append(
            dspy.Example(
                mirad_text=ex.mirad_text,
                word_equivalents=we_str,
                context_passages=ctx_str,
                english_text=ex.english_text,
            ).with_inputs("mirad_text", "word_equivalents", "context_passages")
        )

    # Print few-shot demo summary
    for i, demo in enumerate(enriched_fewshot):
        we_count = len(demo.word_equivalents.split("\n")) if demo.word_equivalents else 0
        print(f"  Demo {i}: MI={demo.mirad_text[:50]!r}... WE={we_count} items")

    # ── Compile with LabeledFewShot ───────────────────────────────────────────
    from dspy import LabeledFewShot

    compile_start = time.time()
    optimizer = LabeledFewShot(k=num_fewshot)
    compiled = optimizer.compile(student=module, trainset=enriched_fewshot)
    compile_time = time.time() - compile_start
    print(f"[run_mir_to_en_baseline_eval] Compile time: {compile_time:.1f}s")

    if save_compiled:
        save_compiled_program(compiled, save_compiled)

    # ── Evaluate on remaining examples ────────────────────────────────────────
    eval_start = time.time()

    # Eval examples only need mirad_text as input — the module computes intermediates
    norm_evaluator = Evaluate(
        devset=eval_examples,
        metric=normalized_match_reverse_metric,
        num_threads=num_threads,
        display_progress=True,
        display_table=0,
    )
    norm_result = norm_evaluator(compiled)

    exact_evaluator = Evaluate(
        devset=eval_examples,
        metric=exact_match_reverse_metric,
        num_threads=num_threads,
        display_progress=True,
        display_table=0,
    )
    exact_result = exact_evaluator(compiled)

    eval_time = time.time() - eval_start
    total_time = time.time() - compile_start

    norm_score = norm_result.score if hasattr(norm_result, "score") else norm_result
    exact_score = exact_result.score if hasattr(exact_result, "score") else exact_result

    summary = {
        "method": "LabeledFewShot",
        "direction": "mir_to_en",
        "lm_type": lm_type,
        "model": model or ("deepseek-ai/DeepSeek-V4-Flash" if lm_type == "deepinfra" else "qwen3.5:4b"),
        "num_fewshot": num_fewshot,
        "k_context_passages": num_context_passages,
        "eval_set_size": len(eval_examples),
        "normalized_score": norm_score,
        "exact_score": exact_score,
        "compile_time_s": round(compile_time, 2),
        "eval_time_s": round(eval_time, 2),
        "total_time_s": round(total_time, 2),
    }

    # ── Save summary ──────────────────────────────────────────────────────────
    results_path = output_path or str(out_dir / "mir_to_en_labeled_fewshot_k5.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # ── Per-example predictions ────────────────────────────────────────────────
    per_example = []
    for ex in eval_examples:
        pred = compiled(ex.mirad_text)
        norm_score_ex = normalized_match_reverse_metric(ex, pred)
        exact_score_ex = exact_match_reverse_metric(ex, pred)
        per_example.append({
            "mirad_text": ex.mirad_text,
            "gold_english": ex.english_text,
            "predicted_english": pred.english_text,
            "word_equivalents": pred.word_equivalents if hasattr(pred, "word_equivalents") else {},
            "context": pred.context if hasattr(pred, "context") else [],
            "normalized_match": norm_score_ex,
            "exact_match": exact_score_ex,
        })

    per_example_path = str(out_dir / "mir_to_en_labeled_fewshot_k5_per_example.json")
    with open(per_example_path, "w", encoding="utf-8") as f:
        json.dump(per_example, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"Mir→En LabeledFewShot Baseline (lm={lm_type}, k={num_context_passages}, {num_fewshot} demos)")
    print(f"{'='*60}")
    print(f"  Model:              {summary['model']}")
    print(f"  LM type:            {lm_type}")
    print(f"  Few-shot demos:     {num_fewshot}")
    print(f"  Eval examples:      {len(eval_examples)}")
    print(f"  RAG passages:      {num_context_passages}")
    print(f"  Normalized match:  {norm_score:.1f}%")
    print(f"  Exact match:        {exact_score:.1f}%")
    print(f"  Compile time:       {compile_time:.1f}s")
    print(f"  Eval time:           {eval_time:.1f}s")
    print(f"  Total time:          {total_time:.1f}s")
    print(f"{'='*60}")
    print(f"Summary saved to {results_path}")
    print(f"Per-example results saved to {per_example_path}")

    return summary