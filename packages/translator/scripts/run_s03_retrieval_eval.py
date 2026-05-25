#!/usr/bin/env python3
"""Run bounded S03 retrieval comparison evaluation with inspectable artifacts.

This runner compares the default translator retrieval path against an S03
retrieval-strategy-enhanced path on the shared S01 bidirectional dev-set.

Artifacts are written beneath ``data/eval_results/m006_s03_retrieval/``:

- ``run_summary.json`` — run-level metadata, preflight state, delta counts, timing
- ``examples.json`` — per-example before/after rows with retrieval payloads
- ``latest.md`` — human-readable inspection report derived from the JSON artifacts

The module intentionally exposes pure helpers so tests can verify dry-run,
preflight, classification, and safe failure behavior without network access.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = Path(__file__).resolve().parent
TRANSLATOR_SRC = PROJECT_ROOT / "packages" / "translator" / "src"
if str(TRANSLATOR_SRC) not in sys.path:
    sys.path.insert(0, str(TRANSLATOR_SRC))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from mirad_translator.retrieval_strategy import RetrievalStrategyConfig, build_retrieval_payload  # noqa: E402
from mirad_translator.translate import _format_context_passages  # noqa: E402

from run_s01_baseline import (  # noqa: E402
    DEFAULT_DEVSET_PATH,
    DEFAULT_MODEL,
    DEFAULT_MAX_EXAMPLES,
    BaselineConfigError,
    PreflightError,
    extract_prediction_text,
    load_devset,
    normalize_for_match,
    normalize_prediction_shape,
    round_cost,
    safe_error_summary,
)

DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "eval_results" / "m006_s03_retrieval"
DEFAULT_ESTIMATED_CALLS_PER_EXAMPLE = 2
DEFAULT_ESTIMATED_COST_PER_CALL_USD = 0.0
DEFAULT_NUM_CONTEXT_PASSAGES = 5

REQUIRED_REPORT_EXAMPLE_KEYS = {
    "id",
    "status",
    "phase",
    "direction",
    "taxonomy_focus",
    "input",
    "expected",
    "baseline_prediction",
    "improved_prediction",
    "baseline_exact_match",
    "baseline_normalized_match",
    "improved_exact_match",
    "improved_normalized_match",
    "delta_classification",
    "baseline_retrieval",
    "improved_retrieval",
    "selected_examples",
    "retrieval_rule_ids",
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
    "delta_counts",
    "preflight",
    "strategy_config",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_string(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def _coerce_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        return [part.strip() for part in text.split(",") if part.strip()]
    if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray, dict)):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)]


def _match_flags(prediction: str, expected: str) -> tuple[bool, bool]:
    exact = prediction == expected
    normalized = normalize_for_match(prediction) == normalize_for_match(expected)
    return exact, normalized


def classify_delta(*, baseline_normalized_match: bool, improved_normalized_match: bool) -> str:
    if baseline_normalized_match and improved_normalized_match:
        return "pass"
    if not baseline_normalized_match and improved_normalized_match:
        return "improved"
    if baseline_normalized_match and not improved_normalized_match:
        return "regressed"
    return "fail" if not baseline_normalized_match and not improved_normalized_match else "held"


# Retain explicit held classification for callers/tests using exact-match paths.
def classify_delta_from_bools(*, baseline_exact_match: bool, baseline_normalized_match: bool, improved_exact_match: bool, improved_normalized_match: bool) -> str:
    if baseline_normalized_match and improved_normalized_match:
        return "pass"
    if not baseline_normalized_match and improved_normalized_match:
        return "improved"
    if baseline_normalized_match and not improved_normalized_match:
        return "regressed"
    if baseline_exact_match == improved_exact_match and baseline_normalized_match == improved_normalized_match:
        return "fail"
    return "held"


def require_live_api_key(*, dry_run: bool) -> dict[str, Any]:
    api_key_present = bool(os.environ.get("DEEPINFRA_API_KEY"))
    if dry_run:
        return {"api_key_required": False, "api_key_present": api_key_present, "status": "not-required"}
    if not api_key_present:
        raise PreflightError("DEEPINFRA_API_KEY is required for live S03 retrieval comparison runs")
    return {"api_key_required": True, "api_key_present": True, "status": "ok"}


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
    if max_examples < 1:
        raise BaselineConfigError("max_examples must be >= 1")
    if len(devset) > max_examples and not explicit_override:
        raise PreflightError(
            f"dev-set has {len(devset)} examples, exceeding bounded limit {max_examples}; pass --max-examples {len(devset)} to override"
        )
    directions = {"en_to_mir": 0, "mir_to_en": 0}
    for example in devset:
        directions[example["direction"]] += 1
    estimated_calls = len(devset) * max(1, int(estimated_calls_per_example))
    estimated_cost = estimated_calls * float(estimated_cost_per_call_usd)
    return {
        "ok": True,
        "dry_run": dry_run,
        "model": model,
        "devset_size": len(devset),
        "max_examples": max_examples,
        "explicit_override": explicit_override,
        "estimated_calls_per_example": int(estimated_calls_per_example),
        "estimated_total_calls": estimated_calls,
        "estimated_cost_usd": round_cost(estimated_cost),
        "direction_counts": directions,
    }


def _retrieval_payload_to_inputs(payload: Mapping[str, Any], *, direction: str) -> tuple[str, str, list[str], list[str]]:
    if direction == "en_to_mir":
        word_equivalents = "\n".join(
            f"{pair['source']} → {pair['target']}" for pair in (payload.get("lexicon_pairs") or [])
        )
    else:
        word_equivalents = "\n".join(
            f"{pair['source']} → {pair['target']}" for pair in (payload.get("lexicon_pairs") or [])
        )
    context_passages_list = [rule.get("passage", "") for rule in (payload.get("grammar_rules") or []) if rule.get("passage")]
    context_passages = _format_context_passages(context_passages_list)
    rule_ids = [str(rule.get("rule_id") or "") for rule in (payload.get("grammar_rules") or []) if str(rule.get("rule_id") or "").strip()]
    selected_examples = [str(item.get("id") or "") for item in (payload.get("few_shot_examples") or []) if str(item.get("id") or "").strip()]
    return word_equivalents, context_passages, rule_ids, selected_examples


def _dry_run_baseline_prediction(example: Mapping[str, Any], index: int) -> str:
    expected = _coerce_string(example.get("expected_text"))
    direction = _coerce_string(example.get("direction"))
    if index % 4 == 0:
        return expected
    if index % 4 == 1:
        return f"baseline-wrong::{example['id']}"
    if index % 4 == 2:
        return expected.upper() if direction == "mir_to_en" else expected.lower()
    return f"held-baseline::{direction}::{index}"


def _dry_run_improved_prediction(example: Mapping[str, Any], index: int) -> str:
    expected = _coerce_string(example.get("expected_text"))
    if index % 4 in {0, 1}:
        return expected
    if index % 4 == 2:
        return f"improved-wrong::{example['id']}"
    return f"held-improved::{example['direction']}::{index}"


def _dry_run_retrieval_payload(
    example: Mapping[str, Any],
    *,
    devset: list[dict[str, Any]],
    improved: bool,
    config: RetrievalStrategyConfig,
) -> dict[str, Any]:
    prefix = "s03" if improved else "baseline"
    payload = build_retrieval_payload(
        dict(example),
        config=config,
        comparison_examples=devset,
        semantic_lookup_multi_fn=lambda text, **_: {
            token.lower(): f"{prefix}.{idx:02d}.{token.lower()}" for idx, token in enumerate(text.split()[:3], start=1)
        } if example["direction"] == "en_to_mir" else {},
        exact_lookup_fn=lambda *, english_word: f"{prefix}.exact.{english_word}",
        reverse_lookup_fn=lambda *, mirad_word: f"{prefix}.reverse.{mirad_word.lower()}",
        retrieve_all_fn=lambda query, top_k: {
            "grammar": [
                {
                    "text": f"{prefix} retrieval for {query}",
                    "metadata": {"source_section": "dry-run", "rule_id": f"{prefix}.rule.{n:02d}"},
                    "rule": {"id": f"{prefix}.rule.{n:02d}", "description": f"{prefix} rule {n} for {example['id']}"},
                }
                for n in range(1, min(top_k, 2 if improved else 1) + 1)
            ]
        },
    )
    return payload


class DryRunTranslator:
    def __init__(self, *, variant: str, devset: list[dict[str, Any]], config: RetrievalStrategyConfig):
        self._variant = variant
        self._devset = devset
        self._config = config

    def __call__(self, source_text: str, direction: str, example: Mapping[str, Any], index: int) -> dict[str, Any]:
        improved = self._variant == "improved"
        payload = _dry_run_retrieval_payload(example, devset=self._devset, improved=improved, config=self._config)
        prediction_text = _dry_run_improved_prediction(example, index) if improved else _dry_run_baseline_prediction(example, index)
        key = "mirad_text" if direction == "en_to_mir" else "english_text"
        return {
            key: prediction_text,
            "context": [rule.get("passage", "") for rule in payload.get("grammar_rules", [])],
            "used_rule_ids": [rule.get("rule_id", "") for rule in payload.get("grammar_rules", [])],
            "retrieval_payload": payload,
        }


class LiveTranslatorAdapter:
    def __init__(
        self,
        *,
        model: str,
        variant: str,
        devset: list[dict[str, Any]],
        strategy_config: RetrievalStrategyConfig,
        num_context_passages: int = DEFAULT_NUM_CONTEXT_PASSAGES,
    ):
        import dspy
        from mirad_translator.evaluate import _make_deepinfra_lm
        from mirad_translator.translate import DefaultTranslator

        self._variant = variant
        self._devset = devset
        self._strategy_config = strategy_config
        lm = _make_deepinfra_lm(model=model)
        dspy.settings.configure(lm=lm)
        self._forward = DefaultTranslator(direction="en_to_mir", num_context_passages=num_context_passages)
        self._reverse = DefaultTranslator(direction="mir_to_en", num_context_passages=num_context_passages)

    def __call__(self, source_text: str, direction: str, example: Mapping[str, Any], index: int) -> Any:
        translator = self._forward if direction == "en_to_mir" else self._reverse
        if self._variant == "baseline":
            if direction == "en_to_mir":
                return translator.forward(english_text=source_text)
            return translator.forward(mirad_text=source_text)

        retrieval_payload = build_retrieval_payload(
            dict(example),
            config=self._strategy_config,
            comparison_examples=self._devset,
        )
        word_equivalents, context_passages, _rule_ids, _selected_examples = _retrieval_payload_to_inputs(
            retrieval_payload,
            direction=direction,
        )
        if direction == "en_to_mir":
            prediction = translator.forward(
                english_text=source_text,
                word_equivalents=word_equivalents,
                context_passages=context_passages,
            )
        else:
            prediction = translator.forward(
                mirad_text=source_text,
                word_equivalents=word_equivalents,
                context_passages=context_passages,
            )
        payload = normalize_prediction_shape(prediction)
        payload["retrieval_payload"] = retrieval_payload
        return payload


def default_translator_factory(
    *,
    dry_run: bool,
    model: str,
    variant: str,
    devset: list[dict[str, Any]],
    strategy_config: RetrievalStrategyConfig,
) -> Callable[[str, str, Mapping[str, Any], int], Any]:
    if dry_run:
        return DryRunTranslator(variant=variant, devset=devset, config=strategy_config)
    return LiveTranslatorAdapter(model=model, variant=variant, devset=devset, strategy_config=strategy_config)


def build_example_row(example: Mapping[str, Any], *, model: str, estimated_calls: int, estimated_cost_usd: float) -> dict[str, Any]:
    return {
        "id": _coerce_string(example.get("id")),
        "status": "pending",
        "phase": "pending",
        "direction": _coerce_string(example.get("direction")),
        "taxonomy_focus": list(example.get("taxonomy_focus") or []),
        "input": _coerce_string(example.get("source_text")),
        "expected": _coerce_string(example.get("expected_text")),
        "baseline_prediction": "",
        "improved_prediction": "",
        "baseline_exact_match": False,
        "baseline_normalized_match": False,
        "improved_exact_match": False,
        "improved_normalized_match": False,
        "delta_classification": "pending",
        "baseline_retrieval": {},
        "improved_retrieval": {},
        "selected_examples": [],
        "retrieval_rule_ids": [],
        "elapsed_ms": 0,
        "model": model,
        "estimated_calls": int(estimated_calls),
        "estimated_cost_usd": round_cost(estimated_cost_usd),
        "error": None,
    }


def _normalize_retrieval_payload(payload: Mapping[str, Any] | None) -> dict[str, Any]:
    if not payload:
        return {
            "normalized_search_terms": [],
            "lexicon_pairs": [],
            "grammar_rules": [],
            "few_shot_examples": [],
            "warnings": [],
        }
    return {
        "normalized_search_terms": list(payload.get("normalized_search_terms") or []),
        "lexicon_pairs": list(payload.get("lexicon_pairs") or []),
        "grammar_rules": list(payload.get("grammar_rules") or []),
        "few_shot_examples": list(payload.get("few_shot_examples") or []),
        "warnings": list(payload.get("warnings") or []),
    }


def run_examples(
    devset: list[dict[str, Any]],
    *,
    baseline_translator: Callable[[str, str, Mapping[str, Any], int], Any],
    improved_translator: Callable[[str, str, Mapping[str, Any], int], Any],
    model: str,
    dry_run: bool,
    estimated_calls_per_example: int,
    estimated_cost_per_call_usd: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, example in enumerate(devset):
        estimated_calls = max(1, int(estimated_calls_per_example))
        row = build_example_row(
            example,
            model=model,
            estimated_calls=estimated_calls,
            estimated_cost_usd=estimated_calls * float(estimated_cost_per_call_usd),
        )
        start = time.perf_counter()
        try:
            baseline_raw = baseline_translator(example["source_text"], example["direction"], example, index)
            improved_raw = improved_translator(example["source_text"], example["direction"], example, index)
            baseline_payload = normalize_prediction_shape(baseline_raw)
            improved_payload = normalize_prediction_shape(improved_raw)
            baseline_prediction = extract_prediction_text(baseline_payload, example["direction"])
            improved_prediction = extract_prediction_text(improved_payload, example["direction"])
            baseline_exact, baseline_normalized = _match_flags(baseline_prediction, example["expected_text"])
            improved_exact, improved_normalized = _match_flags(improved_prediction, example["expected_text"])
            baseline_retrieval = _normalize_retrieval_payload(baseline_payload.get("retrieval_payload"))
            improved_retrieval = _normalize_retrieval_payload(improved_payload.get("retrieval_payload"))
            selected_examples = [
                str(item.get("id") or "")
                for item in improved_retrieval.get("few_shot_examples", [])
                if str(item.get("id") or "").strip()
            ]
            retrieval_rule_ids = [
                str(item.get("rule_id") or "")
                for item in improved_retrieval.get("grammar_rules", [])
                if str(item.get("rule_id") or "").strip()
            ]
            row.update(
                {
                    "status": "dry-run" if dry_run else "ok",
                    "phase": "dry_run" if dry_run else "comparison_complete",
                    "baseline_prediction": baseline_prediction,
                    "improved_prediction": improved_prediction,
                    "baseline_exact_match": baseline_exact,
                    "baseline_normalized_match": baseline_normalized,
                    "improved_exact_match": improved_exact,
                    "improved_normalized_match": improved_normalized,
                    "delta_classification": classify_delta_from_bools(
                        baseline_exact_match=baseline_exact,
                        baseline_normalized_match=baseline_normalized,
                        improved_exact_match=improved_exact,
                        improved_normalized_match=improved_normalized,
                    ),
                    "baseline_retrieval": baseline_retrieval,
                    "improved_retrieval": improved_retrieval,
                    "selected_examples": selected_examples,
                    "retrieval_rule_ids": retrieval_rule_ids,
                }
            )
        except Exception as error:  # noqa: BLE001
            row.update(
                {
                    "status": "error",
                    "phase": "comparison_execution",
                    "error": safe_error_summary(error),
                    "delta_classification": "error",
                }
            )
        finally:
            row["elapsed_ms"] = max(0, round((time.perf_counter() - start) * 1000))
        rows.append(row)
    return rows


def _delta_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"improved": 0, "regressed": 0, "pass": 0, "fail": 0, "held": 0, "error": 0}
    for row in rows:
        key = str(row.get("delta_classification") or "").strip() or "error"
        counts[key] = counts.get(key, 0) + 1
    return counts


def build_run_summary(
    *,
    model: str,
    dry_run: bool,
    preflight: dict[str, Any],
    rows: list[dict[str, Any]],
    started_at: str,
    completed_at: str,
    api_preflight: dict[str, Any],
    strategy_config: RetrievalStrategyConfig,
) -> dict[str, Any]:
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
        "elapsed_ms": sum(int(row.get("elapsed_ms") or 0) for row in rows),
        "failed_example_count": len(failed_examples),
        "failed_example_ids": failed_examples,
        "delta_counts": _delta_counts(rows),
        "preflight": preflight,
        "strategy_config": strategy_config.__dict__,
    }


def _validate_report_example(example: Any, index: int) -> dict[str, Any]:
    if not isinstance(example, dict):
        raise BaselineConfigError(f"report example {index} must be an object")
    missing = sorted(REQUIRED_REPORT_EXAMPLE_KEYS.difference(example))
    if missing:
        raise BaselineConfigError(f"report example {index} missing keys: {', '.join(missing)}")
    return example


def _validate_report_inputs(summary: Any, rows: Any) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if not isinstance(summary, dict):
        raise BaselineConfigError("report summary must be an object")
    if not isinstance(rows, list):
        raise BaselineConfigError("report examples must be a list")
    if "error" in summary and "started_at" not in summary:
        return summary, []
    missing = sorted(REQUIRED_REPORT_SUMMARY_KEYS.difference(summary))
    if missing:
        raise BaselineConfigError(f"report summary missing keys: {', '.join(missing)}")
    return summary, [_validate_report_example(example, index) for index, example in enumerate(rows, start=1)]


def render_markdown_report(summary: Mapping[str, Any], rows: list[dict[str, Any]]) -> str:
    summary, rows = _validate_report_inputs(dict(summary), list(rows))
    if "error" in summary and "started_at" not in summary:
        return "\n".join(
            [
                "# M006 S03 Retrieval Comparison Report",
                "",
                "## Run Metadata",
                "",
                "- status: preflight-failed",
                f"- phase: {_coerce_string(summary.get('phase')) or 'preflight'}",
                f"- error: {_coerce_string(summary.get('error')) or 'unknown error'}",
                "- examples_rendered: 0",
                "",
                "## Preflight Call Estimate",
                "",
                "Preflight failed before baseline/improved comparisons started.",
                "",
                "## Delta Summary",
                "",
                "No comparisons were generated.",
            ]
        ) + "\n"

    lines = [
        "# M006 S03 Retrieval Comparison Report",
        "",
        "## Run Metadata",
        "",
        f"- started_at: {summary['started_at']}",
        f"- completed_at: {summary['completed_at']}",
        f"- mode: {'dry-run' if summary['dry_run'] else 'live'}",
        f"- model: {summary['model']}",
        f"- api_preflight: {summary['api_preflight'].get('status', 'unknown')}",
        f"- devset_size: {summary['devset_size']}",
        f"- elapsed_ms: {summary['elapsed_ms']}",
        f"- failed_example_count: {summary['failed_example_count']}",
        f"- failed_example_ids: {', '.join(summary['failed_example_ids']) if summary['failed_example_ids'] else 'none'}",
        "",
        "## Preflight Call Estimate",
        "",
        f"- estimated_total_calls: {summary['estimated_total_calls']}",
        f"- estimated_cost_usd: {summary['estimated_cost_usd']}",
        f"- total_calls_recorded: {summary['total_calls']}",
        f"- english_to_mirad_examples: {summary['direction_counts'].get('en_to_mir', 0)}",
        f"- mirad_to_english_examples: {summary['direction_counts'].get('mir_to_en', 0)}",
        "",
        "## Strategy Config",
        "",
        "```json",
        json.dumps(summary["strategy_config"], indent=2, ensure_ascii=False),
        "```",
        "",
        "## Delta Summary",
        "",
        "| Classification | Count |",
        "|----------------|-------|",
    ]
    for key in ["improved", "regressed", "pass", "fail", "held", "error"]:
        lines.append(f"| {key} | {summary['delta_counts'].get(key, 0)} |")

    lines.extend([
        "",
        "## Per-Example Table",
        "",
        "| ID | Direction | Delta | Baseline Norm | Improved Norm | Rule IDs | Selected Examples | Elapsed |",
        "|----|-----------|-------|---------------|---------------|----------|-------------------|---------|",
    ])
    for row in rows:
        lines.append(
            f"| {row['id']} | {row['direction']} | {row['delta_classification']} | {row['baseline_normalized_match']} | "
            f"{row['improved_normalized_match']} | {', '.join(row['retrieval_rule_ids']) or 'none'} | "
            f"{', '.join(row['selected_examples']) or 'none'} | {int(row['elapsed_ms'] or 0)} ms |"
        )

    lines.extend(["", "## Detailed Examples", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row['id']}",
                "",
                f"- direction: {row['direction']}",
                f"- taxonomy_focus: {', '.join(row['taxonomy_focus']) if row['taxonomy_focus'] else 'none'}",
                f"- delta_classification: {row['delta_classification']}",
                f"- baseline_exact_match: {row['baseline_exact_match']}",
                f"- baseline_normalized_match: {row['baseline_normalized_match']}",
                f"- improved_exact_match: {row['improved_exact_match']}",
                f"- improved_normalized_match: {row['improved_normalized_match']}",
                f"- retrieval_rule_ids: {', '.join(row['retrieval_rule_ids']) if row['retrieval_rule_ids'] else 'none'}",
                f"- selected_examples: {', '.join(row['selected_examples']) if row['selected_examples'] else 'none'}",
                f"- error_summary: {_coerce_string(row.get('error')) or 'none'}",
                "",
                "#### Baseline Prediction",
                "",
                row['baseline_prediction'] or "(empty)",
                "",
                "#### Improved Prediction",
                "",
                row['improved_prediction'] or "(empty)",
                "",
                "#### Improved Retrieval",
                "",
                "```json",
                json.dumps(row['improved_retrieval'], indent=2, ensure_ascii=False),
                "```",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def write_markdown_report(*, output_dir: Path, summary: Mapping[str, Any], rows: list[dict[str, Any]]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "latest.md"
    report_path.write_text(render_markdown_report(summary, rows), encoding="utf-8")
    return report_path


def persist_artifacts(*, output_dir: Path, summary: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "run_summary.json"
    examples_path = output_dir / "examples.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    examples_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    report_path = write_markdown_report(output_dir=output_dir, summary=summary, rows=rows)
    return {"summary_path": summary_path, "examples_path": examples_path, "report_path": report_path}


def run_retrieval_eval(
    *,
    devset_path: Path = DEFAULT_DEVSET_PATH,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    model: str = DEFAULT_MODEL,
    dry_run: bool = False,
    max_examples: int = DEFAULT_MAX_EXAMPLES,
    estimated_calls_per_example: int = DEFAULT_ESTIMATED_CALLS_PER_EXAMPLE,
    estimated_cost_per_call_usd: float = DEFAULT_ESTIMATED_COST_PER_CALL_USD,
    translator_factory: Callable[..., Callable[[str, str, Mapping[str, Any], int], Any]] | None = None,
    strategy_config: RetrievalStrategyConfig | None = None,
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
    strategy_config = strategy_config or RetrievalStrategyConfig()
    build_translator = translator_factory or default_translator_factory
    baseline_translator = build_translator(
        dry_run=dry_run,
        model=model,
        variant="baseline",
        devset=devset,
        strategy_config=strategy_config,
    )
    improved_translator = build_translator(
        dry_run=dry_run,
        model=model,
        variant="improved",
        devset=devset,
        strategy_config=strategy_config,
    )
    started_at = utc_now_iso()
    rows = run_examples(
        devset,
        baseline_translator=baseline_translator,
        improved_translator=improved_translator,
        model=model,
        dry_run=dry_run,
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
        strategy_config=strategy_config,
    )
    artifact_paths = persist_artifacts(output_dir=output_dir, summary=summary, rows=rows)
    return {"summary": summary, "rows": rows, **artifact_paths}


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run bounded S03 retrieval comparison evaluation")
    parser.add_argument("--devset", type=Path, default=DEFAULT_DEVSET_PATH, help="Path to the S01 bidirectional dev-set JSON")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Artifact output directory")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="DeepInfra model identifier")
    parser.add_argument("--dry-run", action="store_true", help="Skip live LM calls and emit deterministic comparison rows")
    parser.add_argument("--max-examples", type=int, default=DEFAULT_MAX_EXAMPLES, help="Bounded example limit; must explicitly override to exceed 15")
    parser.add_argument("--estimated-calls-per-example", type=int, default=DEFAULT_ESTIMATED_CALLS_PER_EXAMPLE, help="Preflight estimate for combined baseline+improved calls per example")
    parser.add_argument("--estimated-cost-per-call-usd", type=float, default=DEFAULT_ESTIMATED_COST_PER_CALL_USD, help="Optional per-call cost estimate used in artifacts")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    try:
        result = run_retrieval_eval(
            devset_path=args.devset,
            output_dir=args.output_dir,
            model=args.model,
            dry_run=args.dry_run,
            max_examples=args.max_examples,
            estimated_calls_per_example=args.estimated_calls_per_example,
            estimated_cost_per_call_usd=args.estimated_cost_per_call_usd,
        )
    except (BaselineConfigError, PreflightError) as error:
        payload = {"error": safe_error_summary(error), "phase": "preflight"}
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "run_summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(payload, indent=2))
        return 2

    print(json.dumps({
        "summary_path": str(result["summary_path"]),
        "examples_path": str(result["examples_path"]),
        "report_path": str(result["report_path"]),
        "failed_example_count": result["summary"]["failed_example_count"],
        "estimated_total_calls": result["summary"]["estimated_total_calls"],
        "delta_counts": result["summary"]["delta_counts"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
