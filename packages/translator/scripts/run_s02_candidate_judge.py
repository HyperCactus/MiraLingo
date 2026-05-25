#!/usr/bin/env python3
"""Run bounded S02 candidate-generation and judge evaluation with inspectable artifacts.

Artifacts are written beneath ``data/eval_results/m006_s02_candidate_judge/``:

- ``run_summary.json`` — run-level metadata, preflight state, counts, timing, cost
- ``examples.json`` — per-example selected/rejected candidate and judge diagnostic rows
- ``latest.md`` — human-readable inspection report derived from the JSON artifacts

The module intentionally exposes pure helpers so tests can inject fake candidate
and judge implementations without network access.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TRANSLATOR_SRC = PROJECT_ROOT / "packages" / "translator" / "src"
if str(TRANSLATOR_SRC) not in sys.path:
    sys.path.insert(0, str(TRANSLATOR_SRC))

from mirad_translator.candidate_judge import (  # noqa: E402
    DEFAULT_MAX_CANDIDATES,
    CandidateJudgeContractError,
    evaluate_example_candidates,
    generate_dry_run_candidates,
    load_devset,
)

DEFAULT_DEVSET_PATH = PROJECT_ROOT / "data" / "eval" / "devset_s01_bidirectional.json"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "eval_results" / "m006_s02_candidate_judge"
DEFAULT_MODEL = "deepseek-ai/DeepSeek-V4-Flash"
DEFAULT_MAX_EXAMPLES = 15
DEFAULT_ESTIMATED_COST_PER_CALL_USD = 0.0
DEFAULT_CANDIDATES_PER_EXAMPLE = DEFAULT_MAX_CANDIDATES
MAX_SAFE_EXAMPLES = DEFAULT_MAX_EXAMPLES
MAX_SAFE_CANDIDATES_PER_EXAMPLE = DEFAULT_MAX_CANDIDATES
DIRECTION_LABELS = {
    "en_to_mir": "English → Mirad",
    "mir_to_en": "Mirad → English",
}
REQUIRED_REPORT_EXAMPLE_KEYS = {
    "id",
    "status",
    "phase",
    "direction",
    "input",
    "expected",
    "candidate_count",
    "selected_candidate",
    "rejected_candidates",
    "judge_summary",
    "raw_judge_output",
    "elapsed_ms",
    "model",
    "estimated_calls",
    "estimated_cost_usd",
    "error",
}
REQUIRED_REPORT_SUMMARY_KEYS = {
    "started_at",
    "completed_at",
    "dry_run",
    "model",
    "api_preflight",
    "devset_size",
    "direction_counts",
    "estimated_total_calls",
    "estimated_cost_usd",
    "total_calls",
    "elapsed_ms",
    "failed_example_count",
    "failed_example_ids",
    "preflight",
    "successful_example_count",
    "passed_example_count",
}


@dataclass(frozen=True)
class ExampleEstimate:
    estimated_calls: int
    estimated_cost_usd: float


class RunnerConfigError(ValueError):
    """Raised when invocation configuration is invalid."""


class PreflightError(RuntimeError):
    """Raised when live execution should not start."""


class CandidateGeneratorError(RuntimeError):
    """Wrap candidate generator failures so they surface cleanly."""


class JudgeExecutionError(RuntimeError):
    """Wrap judge failures so they surface cleanly."""


class CandidateJudgeSignature:
    """DSPy signature for selecting the best candidate with calibrated confidence."""



def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()



def safe_error_summary(error: BaseException) -> str:
    message = str(error).strip() or error.__class__.__name__
    return f"{error.__class__.__name__}: {message}"



def round_cost(value: float) -> float:
    return round(float(value), 8)



def _coerce_string(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)



def _direction_label(value: Any) -> str:
    return DIRECTION_LABELS.get(_coerce_string(value), _coerce_string(value) or "unknown")



def estimate_calls_for_example(*, candidates_per_example: int) -> ExampleEstimate:
    bounded_candidates = max(1, int(candidates_per_example))
    # One LM call per candidate generation attempt, plus one judge call.
    calls = bounded_candidates + 1
    return ExampleEstimate(estimated_calls=calls, estimated_cost_usd=0.0)



def preflight_devset(
    devset: list[dict[str, Any]],
    *,
    max_examples: int = DEFAULT_MAX_EXAMPLES,
    explicit_override: bool = False,
    dry_run: bool = False,
    candidates_per_example: int = DEFAULT_CANDIDATES_PER_EXAMPLE,
    estimated_cost_per_call_usd: float = DEFAULT_ESTIMATED_COST_PER_CALL_USD,
    model: str = DEFAULT_MODEL,
) -> dict[str, Any]:
    if max_examples < 1:
        raise RunnerConfigError("max_examples must be >= 1")
    if candidates_per_example < 1:
        raise RunnerConfigError("candidates_per_example must be >= 1")
    if len(devset) > max_examples and not explicit_override:
        raise PreflightError(
            f"dev-set has {len(devset)} examples, exceeding bounded limit {max_examples}; "
            f"pass --max-examples {len(devset)} to override"
        )
    if candidates_per_example > MAX_SAFE_CANDIDATES_PER_EXAMPLE and not explicit_override:
        raise PreflightError(
            f"candidates_per_example {candidates_per_example} exceeds bounded safe limit {MAX_SAFE_CANDIDATES_PER_EXAMPLE}; "
            f"override with --max-examples {len(devset)} to acknowledge larger runs"
        )

    estimated_calls = 0
    estimated_cost = 0.0
    directions: dict[str, int] = {"en_to_mir": 0, "mir_to_en": 0}
    for example in devset:
        directions[example["direction"]] += 1
        estimate = estimate_calls_for_example(candidates_per_example=candidates_per_example)
        estimated_calls += estimate.estimated_calls
        estimated_cost += estimate.estimated_calls * float(estimated_cost_per_call_usd)

    return {
        "ok": True,
        "dry_run": dry_run,
        "model": model,
        "devset_size": len(devset),
        "max_examples": max_examples,
        "explicit_override": explicit_override,
        "candidates_per_example": int(candidates_per_example),
        "estimated_total_calls": estimated_calls,
        "estimated_cost_usd": round_cost(estimated_cost),
        "direction_counts": directions,
    }



def require_live_api_key(*, dry_run: bool) -> dict[str, Any]:
    api_key_present = bool(os.environ.get("DEEPINFRA_API_KEY"))
    if dry_run:
        return {"api_key_required": False, "api_key_present": api_key_present, "status": "not-required"}
    if not api_key_present:
        raise PreflightError("DEEPINFRA_API_KEY is required for live candidate-judge runs")
    return {"api_key_required": True, "api_key_present": True, "status": "ok"}


class DryRunCandidateGenerator:
    def __call__(self, *, example: Mapping[str, Any], max_candidates: int) -> list[dict[str, Any]]:
        return generate_dry_run_candidates(
            example=dict(example),
            base_prediction="",
            expected_text=_coerce_string(example.get("expected_text")),
            max_candidates=max_candidates,
        )


class DryRunJudgeRunner:
    def __call__(self, *, example: Mapping[str, Any], candidates: list[dict[str, Any]]) -> dict[str, Any]:
        selected = candidates[0]
        rejected = candidates[1:]
        direction = _coerce_string(example.get("direction"))
        criteria_scores = {
            "semantic_fidelity": 0.98,
            "grammar": 0.95,
            "fluency" if direction == "en_to_mir" else "literalness": 0.94,
        }
        return {
            "selected_candidate_id": selected["candidate_id"],
            "confidence": 0.91,
            "confidence_bucket": "high",
            "passes_threshold": True,
            "rationale": "Dry run selected the first deterministic candidate for auditable offline inspection.",
            "criteria_scores": criteria_scores,
            "rejected_candidates": [
                {
                    "candidate_id": candidate["candidate_id"],
                    "reason": "Dry run retained only the first deterministic candidate.",
                }
                for candidate in rejected
            ],
            "raw_judge_output": {
                "mode": "dry-run",
                "selected_candidate_id": selected["candidate_id"],
                "candidate_ids": [candidate["candidate_id"] for candidate in candidates],
            },
        }


class DefaultCandidateGeneratorAdapter:
    def __init__(self, *, model: str):
        import dspy
        from mirad_translator.evaluate import _make_deepinfra_lm
        from mirad_translator.translate import DefaultTranslator

        lm = _make_deepinfra_lm(model=model)
        dspy.settings.configure(lm=lm)
        self._forward = DefaultTranslator(direction="en_to_mir", num_context_passages=5)
        self._reverse = DefaultTranslator(direction="mir_to_en", num_context_passages=5)

    def _run_translator(self, source_text: str, direction: str) -> Any:
        translator = self._forward if direction == "en_to_mir" else self._reverse
        if hasattr(translator, "forward"):
            if direction == "en_to_mir":
                return translator.forward(english_text=source_text)
            return translator.forward(mirad_text=source_text)
        return translator(source_text)

    def __call__(self, *, example: Mapping[str, Any], max_candidates: int) -> list[dict[str, Any]]:
        source_text = _coerce_string(example.get("source_text"))
        direction = _coerce_string(example.get("direction"))
        candidates: list[dict[str, Any]] = []
        seen_predictions: set[str] = set()
        for index in range(1, max_candidates + 1):
            raw_prediction = self._run_translator(source_text, direction)
            payload = _normalize_prediction_shape(raw_prediction)
            prediction = _extract_prediction_text(payload, direction)
            if prediction in seen_predictions:
                continue
            seen_predictions.add(prediction)
            candidates.append(
                {
                    "candidate_id": f"{_coerce_string(example.get('id'))}-cand-{index:02d}",
                    "prediction": prediction,
                    "source": "default-translator",
                    "prompt_variant": f"sample-{index:02d}",
                    "retrieval_rule_ids": _coerce_string_list(payload.get("used_rule_ids")),
                    "retrieval_context": _coerce_string_list(payload.get("context")),
                    "raw_candidate_output": payload,
                }
            )
        if not candidates:
            raise CandidateJudgeContractError("no candidates generated")
        return candidates


class DefaultJudgeRunnerAdapter:
    def __init__(self, *, model: str):
        import dspy
        from mirad_translator.evaluate import _make_deepinfra_lm

        class Signature(dspy.Signature):
            """Choose the best translation candidate and calibrate confidence.

            Return JSON-compatible fields: selected_candidate_id, confidence
            (0..1), rationale, criteria_scores, rejected_candidates.
            Use semantic_fidelity, grammar, and fluency for en_to_mir; use
            semantic_fidelity, grammar, and literalness for mir_to_en.
            """

            example_id = dspy.InputField(desc="Evaluation example id")
            direction = dspy.InputField(desc="Translation direction")
            source_text = dspy.InputField(desc="Original source text")
            expected_text = dspy.InputField(desc="Reference translation")
            candidates_json = dspy.InputField(desc="JSON array of candidate rows")
            selected_candidate_id = dspy.OutputField(desc="Winning candidate id")
            confidence = dspy.OutputField(desc="Float from 0 to 1")
            rationale = dspy.OutputField(desc="Short reason for the selection")
            criteria_scores = dspy.OutputField(desc="JSON object of criteria scores")
            rejected_candidates = dspy.OutputField(desc="JSON array of rejected candidate ids with reasons")

        self._signature = Signature
        lm = _make_deepinfra_lm(model=model)
        dspy.settings.configure(lm=lm)
        self._predict = dspy.ChainOfThought(self._signature)

    def __call__(self, *, example: Mapping[str, Any], candidates: list[dict[str, Any]]) -> dict[str, Any]:
        prediction = self._predict(
            example_id=_coerce_string(example.get("id")),
            direction=_coerce_string(example.get("direction")),
            source_text=_coerce_string(example.get("source_text")),
            expected_text=_coerce_string(example.get("expected_text")),
            candidates_json=json.dumps(candidates, ensure_ascii=False),
        )
        raw_criteria = _maybe_parse_jsonish(getattr(prediction, "criteria_scores", {}))
        raw_rejected = _maybe_parse_jsonish(getattr(prediction, "rejected_candidates", []))
        return {
            "selected_candidate_id": _coerce_string(getattr(prediction, "selected_candidate_id", "")),
            "confidence": _coerce_floatish(getattr(prediction, "confidence", 0.0)),
            "rationale": _coerce_string(getattr(prediction, "rationale", "")),
            "criteria_scores": raw_criteria,
            "rejected_candidates": raw_rejected,
            "raw_judge_output": {
                "selected_candidate_id": _coerce_string(getattr(prediction, "selected_candidate_id", "")),
                "confidence": _coerce_string(getattr(prediction, "confidence", "")),
                "rationale": _coerce_string(getattr(prediction, "rationale", "")),
                "criteria_scores": raw_criteria,
                "rejected_candidates": raw_rejected,
            },
        }



def default_candidate_generator_factory(*, dry_run: bool, model: str) -> Callable[..., list[dict[str, Any]]]:
    if dry_run:
        return DryRunCandidateGenerator()
    return DefaultCandidateGeneratorAdapter(model=model)



def default_judge_runner_factory(*, dry_run: bool, model: str) -> Callable[..., dict[str, Any]]:
    if dry_run:
        return DryRunJudgeRunner()
    return DefaultJudgeRunnerAdapter(model=model)



def _coerce_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        return [part.strip() for part in stripped.split(",") if part.strip()]
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)]



def _normalize_prediction_shape(prediction: Any) -> dict[str, Any]:
    if isinstance(prediction, str):
        return {"text": prediction}
    if isinstance(prediction, Mapping):
        return dict(prediction)
    data: dict[str, Any] = {}
    for key in (
        "mirad_text",
        "english_text",
        "text",
        "prediction",
        "context",
        "used_rule_ids",
        "raw_output",
        "raw_prediction",
    ):
        if hasattr(prediction, key):
            data[key] = getattr(prediction, key)
    return data



def _extract_prediction_text(prediction: Mapping[str, Any], direction: str) -> str:
    if direction == "en_to_mir":
        candidates = [prediction.get("mirad_text"), prediction.get("text"), prediction.get("prediction")]
    else:
        candidates = [prediction.get("english_text"), prediction.get("text"), prediction.get("prediction")]
    for candidate in candidates:
        if candidate is not None:
            if not isinstance(candidate, str):
                raise TypeError(f"translator returned non-string prediction type {type(candidate).__name__}")
            return candidate
    raise TypeError("translator returned no prediction text field")



def _maybe_parse_jsonish(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return {} if value is not None else None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return value
    return value



def _coerce_floatish(value: Any) -> float:
    if isinstance(value, bool):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        head = value.strip().split()[0] if value.strip() else "0"
        return float(head)
    return float(value)



def build_example_row(
    example: Mapping[str, Any],
    *,
    model: str,
    estimated_calls: int,
    estimated_cost_usd: float,
) -> dict[str, Any]:
    return {
        "id": _coerce_string(example.get("id")),
        "status": "pending",
        "phase": "pending",
        "direction": _coerce_string(example.get("direction")),
        "input": _coerce_string(example.get("source_text")),
        "expected": _coerce_string(example.get("expected_text")),
        "candidate_count": 0,
        "selected_candidate": None,
        "rejected_candidates": [],
        "judge_summary": None,
        "raw_judge_output": None,
        "elapsed_ms": 0,
        "model": model,
        "estimated_calls": int(estimated_calls),
        "estimated_cost_usd": round_cost(estimated_cost_usd),
        "error": None,
    }



def _generate_candidates(
    *,
    example: Mapping[str, Any],
    candidate_generator: Callable[..., list[dict[str, Any]]],
    max_candidates: int,
) -> list[dict[str, Any]]:
    try:
        raw = candidate_generator(example=example, max_candidates=max_candidates)
    except Exception as error:  # noqa: BLE001
        raise CandidateGeneratorError(str(error) or error.__class__.__name__) from error
    if not isinstance(raw, list):
        raise CandidateGeneratorError("candidate generator must return a list")
    return raw



def _run_judge(
    *,
    example: Mapping[str, Any],
    candidates: list[dict[str, Any]],
    judge_runner: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    try:
        raw = judge_runner(example=example, candidates=candidates)
    except Exception as error:  # noqa: BLE001
        raise JudgeExecutionError(str(error) or error.__class__.__name__) from error
    if not isinstance(raw, dict):
        raise JudgeExecutionError("judge runner must return an object")
    return raw



def run_examples(
    devset: list[dict[str, Any]],
    *,
    candidate_generator: Callable[..., list[dict[str, Any]]],
    judge_runner: Callable[..., dict[str, Any]],
    model: str,
    dry_run: bool,
    candidates_per_example: int,
    estimated_cost_per_call_usd: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for example in devset:
        estimate = estimate_calls_for_example(candidates_per_example=candidates_per_example)
        row = build_example_row(
            example,
            model=model,
            estimated_calls=estimate.estimated_calls,
            estimated_cost_usd=estimate.estimated_calls * float(estimated_cost_per_call_usd),
        )
        start = time.perf_counter()
        try:
            candidates = _generate_candidates(
                example=example,
                candidate_generator=candidate_generator,
                max_candidates=candidates_per_example,
            )
            judge_payload = _run_judge(example=example, candidates=candidates, judge_runner=judge_runner)
            result = evaluate_example_candidates(
                example=example,
                candidates=candidates,
                judge_payload=judge_payload,
                max_candidates=candidates_per_example,
            )
            row.update(
                {
                    "status": "dry-run" if dry_run and result["status"] == "ok" else result["status"],
                    "phase": "dry_run" if dry_run and result["status"] == "ok" else result["phase"],
                    "candidate_count": result.get("candidate_count", len(candidates)),
                    "selected_candidate": result.get("selected_candidate"),
                    "rejected_candidates": result.get("rejected_candidates") or [],
                    "judge_summary": result.get("judge_summary"),
                    "raw_judge_output": result.get("raw_judge_output"),
                    "error": result.get("error"),
                }
            )
        except CandidateGeneratorError as error:
            row.update(
                {
                    "status": "error",
                    "phase": "candidate_generation",
                    "error": safe_error_summary(error),
                }
            )
        except JudgeExecutionError as error:
            row.update(
                {
                    "status": "error",
                    "phase": "judge_execution",
                    "error": safe_error_summary(error),
                }
            )
        finally:
            row["elapsed_ms"] = max(0, round((time.perf_counter() - start) * 1000))
        rows.append(row)
    return rows



def build_run_summary(
    *,
    model: str,
    dry_run: bool,
    preflight: dict[str, Any],
    rows: list[dict[str, Any]],
    started_at: str,
    completed_at: str,
    api_preflight: dict[str, Any],
) -> dict[str, Any]:
    total_elapsed_ms = sum(int(row.get("elapsed_ms") or 0) for row in rows)
    failed_examples = [row["id"] for row in rows if row["status"] == "error"]
    successful_rows = [row for row in rows if row["status"] != "error"]
    passed_examples = [
        row["id"]
        for row in successful_rows
        if bool(((row.get("judge_summary") or {}).get("passes_threshold")))
    ]
    return {
        "started_at": started_at,
        "completed_at": completed_at,
        "dry_run": dry_run,
        "model": model,
        "api_preflight": api_preflight,
        "devset_size": preflight["devset_size"],
        "direction_counts": preflight["direction_counts"],
        "estimated_total_calls": preflight["estimated_total_calls"],
        "estimated_cost_usd": preflight["estimated_cost_usd"],
        "total_calls": sum(int(row.get("estimated_calls") or 0) for row in rows),
        "elapsed_ms": total_elapsed_ms,
        "failed_example_count": len(failed_examples),
        "failed_example_ids": failed_examples,
        "successful_example_count": len(successful_rows),
        "passed_example_count": len(passed_examples),
        "passed_example_ids": passed_examples,
        "preflight": preflight,
    }



def _format_usd(value: Any) -> str:
    try:
        return f"${float(value):.6f}"
    except (TypeError, ValueError):
        return "$0.000000"



def _format_duration_ms(value: Any) -> str:
    try:
        milliseconds = int(value)
    except (TypeError, ValueError):
        milliseconds = 0
    seconds = milliseconds / 1000
    return f"{milliseconds} ms ({seconds:.2f} s)"



def _format_confidence(summary: Mapping[str, Any] | None) -> str:
    if not summary:
        return "n/a"
    try:
        return f"{float(summary.get('confidence', 0.0)):.2f}"
    except (TypeError, ValueError):
        return "n/a"



def _validate_report_example(example: Any, index: int) -> dict[str, Any]:
    if not isinstance(example, dict):
        raise RunnerConfigError(f"report example {index} must be an object")
    missing = sorted(REQUIRED_REPORT_EXAMPLE_KEYS.difference(example))
    if missing:
        raise RunnerConfigError(f"report example {index} missing keys: {', '.join(missing)}")
    return example



def _validate_report_inputs(summary: Any, rows: Any) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if not isinstance(summary, dict):
        raise RunnerConfigError("report summary must be an object")
    if not isinstance(rows, list):
        raise RunnerConfigError("report examples must be a list")
    if "error" in summary and "started_at" not in summary:
        return summary, []
    missing_summary = sorted(REQUIRED_REPORT_SUMMARY_KEYS.difference(summary))
    if missing_summary:
        raise RunnerConfigError(f"report summary missing keys: {', '.join(missing_summary)}")
    validated_rows = [_validate_report_example(example, index) for index, example in enumerate(rows, start=1)]
    return summary, validated_rows



def render_markdown_report(summary: Mapping[str, Any], rows: list[dict[str, Any]]) -> str:
    summary, rows = _validate_report_inputs(dict(summary), list(rows))
    if "error" in summary and "started_at" not in summary:
        error_summary = _coerce_string(summary.get("error")) or "unknown error"
        phase = _coerce_string(summary.get("phase")) or "preflight"
        return "\n".join(
            [
                "# M006 S02 Candidate Judge Inspection Report",
                "",
                "## Run Metadata",
                "",
                "- status: preflight-failed",
                f"- phase: {phase}",
                f"- error: {error_summary}",
                "- examples_rendered: 0",
                "",
                "## Preflight Call and Cost Estimate",
                "",
                "Preflight failed before candidate generation or judging started.",
                "",
                "## Per-Example Summary",
                "",
                "No examples available.",
            ]
        ) + "\n"

    lines: list[str] = [
        "# M006 S02 Candidate Judge Inspection Report",
        "",
        "## Run Metadata",
        "",
        f"- started_at: {summary['started_at']}",
        f"- completed_at: {summary['completed_at']}",
        f"- mode: {'dry-run' if summary['dry_run'] else 'live'}",
        f"- model: {summary['model']}",
        f"- api_preflight: {summary['api_preflight'].get('status', 'unknown')}",
        f"- devset_size: {summary['devset_size']}",
        f"- elapsed: {_format_duration_ms(summary['elapsed_ms'])}",
        f"- failed_example_count: {summary['failed_example_count']}",
        f"- passed_example_count: {summary['passed_example_count']}",
        "",
        "## Preflight Call and Cost Estimate",
        "",
        f"- estimated_total_calls: {summary['estimated_total_calls']}",
        f"- estimated_cost_usd: {_format_usd(summary['estimated_cost_usd'])}",
        f"- total_calls_recorded: {summary['total_calls']}",
        f"- candidates_per_example: {summary['preflight']['candidates_per_example']}",
        f"- english_to_mirad_examples: {summary['direction_counts'].get('en_to_mir', 0)}",
        f"- mirad_to_english_examples: {summary['direction_counts'].get('mir_to_en', 0)}",
        "",
        "## Per-Example Summary",
        "",
        "| ID | Direction | Status | Phase | Candidates | Confidence | Bucket | Passes | Elapsed |",
        "|----|-----------|--------|-------|------------|------------|--------|--------|---------|",
    ]
    for row in rows:
        judge_summary = row.get("judge_summary") or {}
        lines.append(
            f"| {row['id']} | {_direction_label(row['direction'])} | {row['status']} | {row['phase']} | "
            f"{row['candidate_count']} | {_format_confidence(judge_summary)} | "
            f"{judge_summary.get('confidence_bucket', 'n/a')} | "
            f"{judge_summary.get('passes_threshold', 'n/a')} | {int(row.get('elapsed_ms') or 0)} ms |"
        )

    lines.extend(["", "## Detailed Examples", ""])
    for row in rows:
        judge_summary = row.get("judge_summary") or {}
        selected = row.get("selected_candidate") or {}
        rejected = row.get("rejected_candidates") or []
        lines.extend(
            [
                f"### {row['id']}",
                "",
                f"- direction: {_direction_label(row['direction'])}",
                f"- status: {row['status']}",
                f"- phase: {row['phase']}",
                f"- candidate_count: {row['candidate_count']}",
                f"- confidence: {_format_confidence(judge_summary)}",
                f"- confidence_bucket: {judge_summary.get('confidence_bucket', 'n/a')}",
                f"- passes_threshold: {judge_summary.get('passes_threshold', 'n/a')}",
                f"- selected_candidate_id: {selected.get('candidate_id', 'none')}",
                f"- selected_prediction: {_coerce_string(selected.get('prediction')) or 'none'}",
                f"- aggregate_score: {judge_summary.get('aggregate_score', 'n/a')}",
                f"- criteria_scores: {json.dumps(judge_summary.get('criteria_scores') or {}, ensure_ascii=False)}",
                f"- judge_rationale: {_coerce_string(judge_summary.get('rationale')) or 'none'}",
                f"- error_summary: {_coerce_string(row.get('error')) or 'none'}",
                "",
                "#### Rejected Candidates",
                "",
            ]
        )
        if rejected:
            for candidate in rejected:
                lines.append(
                    f"- {candidate.get('candidate_id', 'unknown')}: {_coerce_string(candidate.get('rejection_reason')) or 'no reason'}"
                )
        else:
            lines.append("None.")
        lines.extend([
            "",
            "#### Raw Judge Output",
            "",
            "```json",
            json.dumps(row.get("raw_judge_output"), indent=2, ensure_ascii=False),
            "```",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"



def write_markdown_report(*, output_dir: Path, summary: Mapping[str, Any], rows: list[dict[str, Any]]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "latest.md"
    report_text = render_markdown_report(summary, rows)
    report_path.write_text(report_text, encoding="utf-8")
    return report_path



def persist_artifacts(*, output_dir: Path, summary: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "run_summary.json"
    examples_path = output_dir / "examples.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    examples_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    report_path = write_markdown_report(output_dir=output_dir, summary=summary, rows=rows)
    return {"summary_path": summary_path, "examples_path": examples_path, "report_path": report_path}



def run_candidate_judge(
    *,
    devset_path: Path = DEFAULT_DEVSET_PATH,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    model: str = DEFAULT_MODEL,
    dry_run: bool = False,
    max_examples: int = DEFAULT_MAX_EXAMPLES,
    candidates_per_example: int = DEFAULT_CANDIDATES_PER_EXAMPLE,
    estimated_cost_per_call_usd: float = DEFAULT_ESTIMATED_COST_PER_CALL_USD,
    candidate_generator_factory: Callable[..., Callable[..., list[dict[str, Any]]]] | None = None,
    judge_runner_factory: Callable[..., Callable[..., dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    devset = load_devset(devset_path)
    explicit_override = max_examples != DEFAULT_MAX_EXAMPLES
    preflight = preflight_devset(
        devset,
        max_examples=max_examples,
        explicit_override=explicit_override,
        dry_run=dry_run,
        candidates_per_example=candidates_per_example,
        estimated_cost_per_call_usd=estimated_cost_per_call_usd,
        model=model,
    )
    api_preflight = require_live_api_key(dry_run=dry_run)
    build_candidate_generator = candidate_generator_factory or default_candidate_generator_factory
    build_judge_runner = judge_runner_factory or default_judge_runner_factory
    candidate_generator = build_candidate_generator(dry_run=dry_run, model=model)
    judge_runner = build_judge_runner(dry_run=dry_run, model=model)
    started_at = utc_now_iso()
    rows = run_examples(
        devset,
        candidate_generator=candidate_generator,
        judge_runner=judge_runner,
        model=model,
        dry_run=dry_run,
        candidates_per_example=candidates_per_example,
        estimated_cost_per_call_usd=estimated_cost_per_call_usd,
    )
    completed_at = utc_now_iso()
    summary = build_run_summary(
        model=model,
        dry_run=dry_run,
        preflight=preflight,
        rows=rows,
        started_at=started_at,
        completed_at=completed_at,
        api_preflight=api_preflight,
    )
    artifact_paths = persist_artifacts(output_dir=output_dir, summary=summary, rows=rows)
    return {"summary": summary, "rows": rows, **artifact_paths}



def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run bounded S02 candidate judge evaluation")
    parser.add_argument("--devset", type=Path, default=DEFAULT_DEVSET_PATH, help="Path to the S01 bidirectional dev-set JSON")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Artifact output directory")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="DeepInfra model identifier")
    parser.add_argument("--dry-run", action="store_true", help="Skip live LM calls and emit deterministic diagnostic rows")
    parser.add_argument("--max-examples", type=int, default=DEFAULT_MAX_EXAMPLES, help="Bounded example limit; must explicitly override to exceed 15")
    parser.add_argument("--candidates-per-example", type=int, default=DEFAULT_CANDIDATES_PER_EXAMPLE, help="Bounded candidate count per example")
    parser.add_argument("--estimated-cost-per-call-usd", type=float, default=DEFAULT_ESTIMATED_COST_PER_CALL_USD, help="Optional per-call cost estimate used in artifacts")
    return parser



def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    try:
        result = run_candidate_judge(
            devset_path=args.devset,
            output_dir=args.output_dir,
            model=args.model,
            dry_run=args.dry_run,
            max_examples=args.max_examples,
            candidates_per_example=args.candidates_per_example,
            estimated_cost_per_call_usd=args.estimated_cost_per_call_usd,
        )
    except (RunnerConfigError, PreflightError, CandidateJudgeContractError) as error:
        payload = {
            "error": safe_error_summary(error),
            "phase": "preflight",
        }
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "run_summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(payload, indent=2))
        return 2

    print(
        json.dumps(
            {
                "summary_path": str(result["summary_path"]),
                "examples_path": str(result["examples_path"]),
                "report_path": str(result["report_path"]),
                "failed_example_count": result["summary"]["failed_example_count"],
                "estimated_total_calls": result["summary"]["estimated_total_calls"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
