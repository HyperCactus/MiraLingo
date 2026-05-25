#!/usr/bin/env python3
"""Run a bounded S01 baseline evaluation and persist inspectable artifacts.

This runner is designed to support both live DeepInfra-backed evaluation and
fully offline test execution through injected translators or ``--dry-run``.

Artifacts are written beneath ``data/eval_results/m006_s01_baseline/``:

- ``run_summary.json`` — run-level metadata, preflight state, counts, timing, cost
- ``examples.json`` — per-example diagnostic rows

The module also exposes pure helpers so tests can verify schema, preflight, and
error-row behavior without network access.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TRANSLATOR_SRC = PROJECT_ROOT / "packages" / "translator" / "src"
if str(TRANSLATOR_SRC) not in sys.path:
    sys.path.insert(0, str(TRANSLATOR_SRC))

DEFAULT_DEVSET_PATH = PROJECT_ROOT / "data" / "eval" / "devset_s01_bidirectional.json"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "eval_results" / "m006_s01_baseline"
DEFAULT_MODEL = "deepseek-ai/DeepSeek-V4-Flash"
DEFAULT_MAX_EXAMPLES = 15
DEFAULT_ESTIMATED_CALLS_PER_EXAMPLE = 1
DEFAULT_ESTIMATED_COST_PER_CALL_USD = 0.0
ALLOWED_DIRECTIONS = {"en_to_mir", "mir_to_en"}


@dataclass(frozen=True)
class ExampleEstimate:
    estimated_calls: int
    estimated_cost_usd: float


class BaselineConfigError(ValueError):
    """Raised when the dataset or invocation configuration is invalid."""


class PreflightError(RuntimeError):
    """Raised when live execution should not start."""


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


def normalize_for_match(text: str) -> str:
    normalized = _coerce_string(text).strip().lower()
    collapsed = " ".join(normalized.split())
    return "".join(ch for ch in collapsed if ch.isalnum() or ch.isspace()).strip()


def normalize_prediction_shape(prediction: Any) -> dict[str, Any]:
    """Coerce translator output to a dict-like structure.

    Accepts dicts, DSPy predictions/objects with attributes, or bare strings.
    """
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
        "word_equivalents",
        "warnings",
        "warning",
        "raw_output",
        "raw_prediction",
    ):
        if hasattr(prediction, key):
            data[key] = getattr(prediction, key)
    return data


def extract_prediction_text(prediction: Any, direction: str) -> str:
    payload = normalize_prediction_shape(prediction)
    candidates: list[Any] = []
    if direction == "en_to_mir":
        candidates.extend([payload.get("mirad_text"), payload.get("text"), payload.get("prediction")])
    else:
        candidates.extend([payload.get("english_text"), payload.get("text"), payload.get("prediction")])
    for candidate in candidates:
        if candidate is not None:
            if not isinstance(candidate, str):
                raise TypeError(f"translator returned non-string prediction type {type(candidate).__name__}")
            return candidate
    raise TypeError("translator returned no prediction text field")


def coerce_rule_ids(value: Any) -> tuple[list[str], bool]:
    if value is None:
        return [], False
    malformed = False
    if isinstance(value, str):
        text = value.strip()
        if not text or text.lower() in {"none", "n/a", "na"}:
            return [], False
        items = [part.strip() for part in text.split(",")]
    elif isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray, dict)):
        items = [str(item).strip() for item in value]
    else:
        return [str(value)], True
    result = [item for item in items if item]
    return result, malformed


def coerce_retrieval_context(value: Any) -> tuple[list[str], bool]:
    if value is None:
        return [], False
    if isinstance(value, str):
        text = value.strip()
        return ([text] if text else []), False
    if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray, dict)):
        result = []
        malformed = False
        for item in value:
            if item is None:
                continue
            if isinstance(item, str):
                text = item.strip()
                if text:
                    result.append(text)
                continue
            malformed = True
            result.append(str(item))
        return result, malformed
    return [str(value)], True


def load_devset(path: Path = DEFAULT_DEVSET_PATH) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    validate_devset(payload)
    return payload


def validate_devset(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, list):
        raise BaselineConfigError("dev-set must be a list")
    if not payload:
        raise BaselineConfigError("dev-set must not be empty")

    validated: list[dict[str, Any]] = []
    for index, example in enumerate(payload, start=1):
        if not isinstance(example, dict):
            raise BaselineConfigError(f"example {index} must be an object")
        example_id = _coerce_string(example.get("id") or f"index-{index}")
        direction = example.get("direction")
        if direction not in ALLOWED_DIRECTIONS:
            raise BaselineConfigError(f"{example_id}: unknown direction '{direction}'")
        expected_text = _coerce_string(example.get("expected_text"))
        if not expected_text.strip():
            raise BaselineConfigError(f"{example_id}: expected_text must be a non-empty string")
        source_text = _coerce_string(example.get("source_text"))
        if not source_text.strip():
            raise BaselineConfigError(f"{example_id}: source_text must be a non-empty string")
        taxonomy_focus = example.get("taxonomy_focus")
        if taxonomy_focus is None:
            taxonomy_focus = []
        if not isinstance(taxonomy_focus, list) or any(not _coerce_string(item).strip() for item in taxonomy_focus):
            raise BaselineConfigError(f"{example_id}: taxonomy_focus must be a list of non-empty strings")
        validated.append(dict(example))
    return validated


def estimate_calls_for_example(example: Mapping[str, Any], estimated_calls_per_example: int = DEFAULT_ESTIMATED_CALLS_PER_EXAMPLE) -> ExampleEstimate:
    calls = max(1, int(estimated_calls_per_example))
    return ExampleEstimate(estimated_calls=calls, estimated_cost_usd=0.0)


def preflight_devset(
    devset: list[dict[str, Any]],
    *,
    max_examples: int = DEFAULT_MAX_EXAMPLES,
    explicit_override: bool = False,
    dry_run: bool = False,
    estimated_calls_per_example: int = DEFAULT_ESTIMATED_CALLS_PER_EXAMPLE,
    estimated_cost_per_call_usd: float = DEFAULT_ESTIMATED_COST_PER_CALL_USD,
    model: str = DEFAULT_MODEL,
) -> dict[str, Any]:
    validated = validate_devset(devset)
    if len(validated) > max_examples and not explicit_override:
        raise PreflightError(
            f"dev-set has {len(validated)} examples, exceeding bounded limit {max_examples}; pass --max-examples {len(validated)} to override"
        )
    estimated_calls = 0
    estimated_cost = 0.0
    directions: dict[str, int] = {"en_to_mir": 0, "mir_to_en": 0}
    for example in validated:
        directions[example["direction"]] += 1
        estimate = estimate_calls_for_example(example, estimated_calls_per_example=estimated_calls_per_example)
        estimated_calls += estimate.estimated_calls
        estimated_cost += estimate.estimated_calls * float(estimated_cost_per_call_usd)
    return {
        "ok": True,
        "dry_run": dry_run,
        "model": model,
        "devset_size": len(validated),
        "max_examples": max_examples,
        "explicit_override": explicit_override,
        "estimated_calls_per_example": int(estimated_calls_per_example),
        "estimated_total_calls": estimated_calls,
        "estimated_cost_usd": round_cost(estimated_cost),
        "direction_counts": directions,
    }


def require_live_api_key(*, dry_run: bool) -> dict[str, Any]:
    api_key_present = bool(os.environ.get("DEEPINFRA_API_KEY"))
    if dry_run:
        return {"api_key_required": False, "api_key_present": api_key_present, "status": "not-required"}
    if not api_key_present:
        raise PreflightError("DEEPINFRA_API_KEY is required for live baseline runs")
    return {"api_key_required": True, "api_key_present": True, "status": "ok"}


class DryRunTranslator:
    def __call__(self, source_text: str, direction: str, example: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "text": "",
            "context": [],
            "used_rule_ids": [],
            "warning": "dry_run_no_translation",
        }


class DefaultTranslatorAdapter:
    """Thin compatibility layer over ``mirad_translator.translate.DefaultTranslator``."""

    def __init__(self, *, model: str, num_context_passages: int = 5):
        import dspy
        from mirad_translator.evaluate import _make_deepinfra_lm
        from mirad_translator.translate import DefaultTranslator

        lm = _make_deepinfra_lm(model=model)
        dspy.settings.configure(lm=lm)
        self._forward = DefaultTranslator(direction="en_to_mir", num_context_passages=num_context_passages)
        self._reverse = DefaultTranslator(direction="mir_to_en", num_context_passages=num_context_passages)

    def __call__(self, source_text: str, direction: str, example: Mapping[str, Any]) -> Any:
        translator = self._forward if direction == "en_to_mir" else self._reverse
        if hasattr(translator, "forward"):
            if direction == "en_to_mir":
                return translator.forward(english_text=source_text)
            return translator.forward(mirad_text=source_text)
        return translator(source_text)


def default_translator_factory(*, dry_run: bool, model: str) -> Callable[[str, str, Mapping[str, Any]], Any]:
    if dry_run:
        return DryRunTranslator()
    return DefaultTranslatorAdapter(model=model)


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
        "prediction": "",
        "normalized_match": False,
        "exact_match": False,
        "retrieval_context": [],
        "retrieval_rule_ids": [],
        "retrieval_warning": None,
        "elapsed_ms": 0,
        "model": model,
        "estimated_calls": int(estimated_calls),
        "estimated_cost_usd": round_cost(estimated_cost_usd),
        "failure_labels": list(example.get("taxonomy_focus") or []),
        "error": None,
    }


def run_examples(
    devset: list[dict[str, Any]],
    *,
    translator: Callable[[str, str, Mapping[str, Any]], Any],
    model: str,
    dry_run: bool,
    fail_fast: bool,
    estimated_calls_per_example: int,
    estimated_cost_per_call_usd: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for example in devset:
        estimate = estimate_calls_for_example(example, estimated_calls_per_example=estimated_calls_per_example)
        row = build_example_row(
            example,
            model=model,
            estimated_calls=estimate.estimated_calls,
            estimated_cost_usd=estimate.estimated_calls * float(estimated_cost_per_call_usd),
        )
        start = time.perf_counter()
        try:
            raw_prediction = translator(example["source_text"], example["direction"], example)
            payload = normalize_prediction_shape(raw_prediction)
            prediction_text = extract_prediction_text(payload, example["direction"])
            retrieval_context, retrieval_context_malformed = coerce_retrieval_context(payload.get("context"))
            rule_ids, rule_ids_malformed = coerce_rule_ids(payload.get("used_rule_ids"))
            warning_candidates = []
            if payload.get("warning"):
                warning_candidates.append(_coerce_string(payload.get("warning")))
            if payload.get("warnings"):
                warning_candidates.append(_coerce_string(payload.get("warnings")))
            if retrieval_context_malformed or rule_ids_malformed:
                warning_candidates.append("retrieval_context_malformed")

            row.update(
                {
                    "status": "ok" if not dry_run else "dry-run",
                    "phase": "complete" if not dry_run else "dry_run",
                    "prediction": prediction_text,
                    "exact_match": prediction_text == example["expected_text"],
                    "normalized_match": normalize_for_match(prediction_text) == normalize_for_match(example["expected_text"]),
                    "retrieval_context": retrieval_context,
                    "retrieval_rule_ids": rule_ids,
                    "retrieval_warning": "; ".join(part for part in warning_candidates if part) or None,
                }
            )
        except TypeError as error:
            row.update(
                {
                    "status": "error",
                    "phase": "parse_prediction",
                    "error": safe_error_summary(error),
                }
            )
            if fail_fast:
                row["elapsed_ms"] = max(0, round((time.perf_counter() - start) * 1000))
                rows.append(row)
                raise
        except Exception as error:  # noqa: BLE001 - persisted as stacktrace-free diagnostics
            row.update(
                {
                    "status": "error",
                    "phase": "model_call",
                    "error": safe_error_summary(error),
                }
            )
            if fail_fast:
                row["elapsed_ms"] = max(0, round((time.perf_counter() - start) * 1000))
                rows.append(row)
                raise
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
        "preflight": preflight,
    }


def persist_artifacts(*, output_dir: Path, summary: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "run_summary.json"
    examples_path = output_dir / "examples.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    examples_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"summary_path": summary_path, "examples_path": examples_path}


def run_baseline(
    *,
    devset_path: Path = DEFAULT_DEVSET_PATH,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    model: str = DEFAULT_MODEL,
    dry_run: bool = False,
    max_examples: int = DEFAULT_MAX_EXAMPLES,
    fail_fast: bool = False,
    estimated_calls_per_example: int = DEFAULT_ESTIMATED_CALLS_PER_EXAMPLE,
    estimated_cost_per_call_usd: float = DEFAULT_ESTIMATED_COST_PER_CALL_USD,
    translator_factory: Callable[..., Callable[[str, str, Mapping[str, Any]], Any]] | None = None,
) -> dict[str, Any]:
    devset = load_devset(devset_path)
    explicit_override = max_examples != DEFAULT_MAX_EXAMPLES
    preflight = preflight_devset(
        devset,
        max_examples=max_examples,
        explicit_override=explicit_override,
        dry_run=dry_run,
        estimated_calls_per_example=estimated_calls_per_example,
        estimated_cost_per_call_usd=estimated_cost_per_call_usd,
        model=model,
    )
    api_preflight = require_live_api_key(dry_run=dry_run)
    build_translator = translator_factory or default_translator_factory
    translator = build_translator(dry_run=dry_run, model=model)
    started_at = utc_now_iso()
    rows = run_examples(
        devset,
        translator=translator,
        model=model,
        dry_run=dry_run,
        fail_fast=fail_fast,
        estimated_calls_per_example=estimated_calls_per_example,
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
    return {
        "summary": summary,
        "rows": rows,
        **artifact_paths,
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run bounded S01 baseline evaluation")
    parser.add_argument("--devset", type=Path, default=DEFAULT_DEVSET_PATH, help="Path to the S01 bidirectional dev-set JSON")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Artifact output directory")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="DeepInfra model identifier")
    parser.add_argument("--dry-run", action="store_true", help="Skip live LM calls and emit diagnostic dry-run rows")
    parser.add_argument("--max-examples", type=int, default=DEFAULT_MAX_EXAMPLES, help="Bounded example limit; must explicitly override to exceed 15")
    parser.add_argument("--fail-fast", action="store_true", help="Abort after the first per-example error")
    parser.add_argument("--estimated-calls-per-example", type=int, default=DEFAULT_ESTIMATED_CALLS_PER_EXAMPLE, help="Preflight estimate for LM calls per example")
    parser.add_argument("--estimated-cost-per-call-usd", type=float, default=DEFAULT_ESTIMATED_COST_PER_CALL_USD, help="Optional per-call cost estimate used in artifacts")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    try:
        result = run_baseline(
            devset_path=args.devset,
            output_dir=args.output_dir,
            model=args.model,
            dry_run=args.dry_run,
            max_examples=args.max_examples,
            fail_fast=args.fail_fast,
            estimated_calls_per_example=args.estimated_calls_per_example,
            estimated_cost_per_call_usd=args.estimated_cost_per_call_usd,
        )
    except (BaselineConfigError, PreflightError) as error:
        payload = {
            "error": safe_error_summary(error),
            "phase": "preflight",
        }
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "run_summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(payload, indent=2))
        return 2

    print(json.dumps({
        "summary_path": str(result["summary_path"]),
        "examples_path": str(result["examples_path"]),
        "failed_example_count": result["summary"]["failed_example_count"],
        "estimated_total_calls": result["summary"]["estimated_total_calls"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
