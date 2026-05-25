import importlib.util
import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest

MODULE_PATH = Path("packages/translator/scripts/run_s01_baseline.py")
SPEC = importlib.util.spec_from_file_location("run_s01_baseline", MODULE_PATH)
assert SPEC and SPEC.loader
run_s01_baseline = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = run_s01_baseline
SPEC.loader.exec_module(run_s01_baseline)

DEFAULT_MODEL = run_s01_baseline.DEFAULT_MODEL
BaselineConfigError = run_s01_baseline.BaselineConfigError
PreflightError = run_s01_baseline.PreflightError
load_devset = run_s01_baseline.load_devset
preflight_devset = run_s01_baseline.preflight_devset
render_markdown_report = run_s01_baseline.render_markdown_report
run_baseline = run_s01_baseline.run_baseline
write_markdown_report = run_s01_baseline.write_markdown_report


class FakeTranslator:
    def __init__(self, responses):
        self._responses = responses
        self.calls = []

    def __call__(self, source_text, direction, example):
        self.calls.append((source_text, direction, example["id"]))
        response = self._responses[example["id"]]
        if isinstance(response, Exception):
            raise response
        return response


@pytest.fixture
def real_devset_path() -> Path:
    return Path("data/eval/devset_s01_bidirectional.json")


@pytest.fixture
def devset(real_devset_path):
    return load_devset(real_devset_path)


@pytest.fixture
def output_dir(tmp_path):
    return tmp_path / "artifacts"


def _factory_for(translator):
    def factory(*, dry_run, model):
        assert model == DEFAULT_MODEL
        assert dry_run is False
        return translator

    return factory


def test_preflight_reports_exact_bounded_counts(devset):
    preflight = preflight_devset(
        devset,
        estimated_calls_per_example=2,
        estimated_cost_per_call_usd=0.0125,
        model=DEFAULT_MODEL,
    )

    assert preflight["devset_size"] == 12
    assert preflight["direction_counts"] == {"en_to_mir": 6, "mir_to_en": 6}
    assert preflight["estimated_total_calls"] == 24
    assert preflight["estimated_cost_usd"] == 0.3


def test_preflight_rejects_dataset_over_limit_without_explicit_override(devset):
    expanded = deepcopy(devset)
    extra = deepcopy(expanded[0])
    extra["id"] = "s01-013-extra"
    expanded.extend(deepcopy(extra) for _ in range(4))
    for index, item in enumerate(expanded[12:], start=13):
        item["id"] = f"s01-{index:03d}-extra"

    with pytest.raises(PreflightError, match="exceeding bounded limit 15"):
        preflight_devset(expanded)


def test_load_devset_rejects_missing_expected_text(tmp_path):
    broken = [
        {
            "id": "s01-bad",
            "direction": "en_to_mir",
            "source_text": "hello",
            "expected_text": "",
            "taxonomy_focus": ["test"],
        }
    ]
    path = tmp_path / "broken.json"
    path.write_text(json.dumps(broken), encoding="utf-8")

    with pytest.raises(BaselineConfigError, match="expected_text must be a non-empty string"):
        load_devset(path)


def test_load_devset_rejects_unknown_direction(tmp_path):
    broken = [
        {
            "id": "s01-bad-direction",
            "direction": "english_to_mirad",
            "source_text": "hello",
            "expected_text": "halo",
            "taxonomy_focus": ["test"],
        }
    ]
    path = tmp_path / "broken.json"
    path.write_text(json.dumps(broken), encoding="utf-8")

    with pytest.raises(BaselineConfigError, match="unknown direction"):
        load_devset(path)


def test_run_baseline_requires_api_key_for_live_mode(devset, output_dir, monkeypatch):
    monkeypatch.delenv("DEEPINFRA_API_KEY", raising=False)

    with pytest.raises(PreflightError, match="DEEPINFRA_API_KEY"):
        run_baseline(
            devset_path=Path("data/eval/devset_s01_bidirectional.json"),
            output_dir=output_dir,
            translator_factory=lambda **_: FakeTranslator({}),
        )


def test_run_baseline_persists_expected_artifacts_with_fake_translator(devset, output_dir, monkeypatch):
    monkeypatch.setenv("DEEPINFRA_API_KEY", "test-key")

    responses = {
        devset[0]["id"]: {
            "mirad_text": devset[0]["expected_text"],
            "context": ["rule snippet"],
            "used_rule_ids": ["rule.progressive"],
        },
        devset[1]["id"]: {
            "mirad_text": "wrong answer",
            "context": [{"unsafe": "coerced"}],
            "used_rule_ids": "rule.comparison",
        },
    }
    for example in devset[2:]:
        key = "mirad_text" if example["direction"] == "en_to_mir" else "english_text"
        responses[example["id"]] = {
            key: example["expected_text"],
            "context": [],
            "used_rule_ids": [],
        }

    translator = FakeTranslator(responses)
    result = run_baseline(
        devset_path=Path("data/eval/devset_s01_bidirectional.json"),
        output_dir=output_dir,
        translator_factory=_factory_for(translator),
        estimated_calls_per_example=2,
        estimated_cost_per_call_usd=0.01,
    )

    summary = result["summary"]
    rows = result["rows"]
    assert result["summary_path"].exists()
    assert result["examples_path"].exists()
    assert result["report_path"].exists()
    assert summary["api_preflight"]["status"] == "ok"
    assert summary["estimated_total_calls"] == 24
    assert summary["total_calls"] == 24
    assert summary["failed_example_count"] == 0
    assert len(rows) == len(devset)

    first = rows[0]
    assert first["status"] == "ok"
    assert first["prediction"] == devset[0]["expected_text"]
    assert first["exact_match"] is True
    assert first["normalized_match"] is True
    assert first["retrieval_context"] == ["rule snippet"]
    assert first["retrieval_rule_ids"] == ["rule.progressive"]
    assert first["failure_labels"] == devset[0]["taxonomy_focus"]
    assert first["elapsed_ms"] >= 0
    assert first["model"] == DEFAULT_MODEL
    assert first["estimated_calls"] == 2
    assert first["estimated_cost_usd"] == 0.02

    second = rows[1]
    assert second["exact_match"] is False
    assert second["normalized_match"] is False
    assert second["retrieval_context"] == ["{'unsafe': 'coerced'}"]
    assert second["retrieval_warning"] == "retrieval_context_malformed"

    report_text = result["report_path"].read_text(encoding="utf-8")
    assert "# M006 S01 Baseline Inspection Report" in report_text
    assert "## Run Metadata" in report_text
    assert "## Preflight Call and Cost Estimate" in report_text
    assert "## Score Summary by Direction" in report_text
    assert "## Failure Taxonomy Legend" in report_text
    assert "## Per-Example Table" in report_text
    assert "## Detailed Examples" in report_text
    assert "### s01-001-en-to-mir-progressive-going-home" in report_text
    assert "rule.progressive" in report_text
    assert "rule snippet" in report_text
    assert "retrieval_context_malformed" in report_text

    disk_summary = json.loads(result["summary_path"].read_text(encoding="utf-8"))
    disk_rows = json.loads(result["examples_path"].read_text(encoding="utf-8"))
    assert disk_summary["failed_example_count"] == 0
    assert disk_rows[0]["id"] == devset[0]["id"]


def test_run_baseline_records_stacktrace_free_example_error_row(devset, output_dir, monkeypatch):
    monkeypatch.setenv("DEEPINFRA_API_KEY", "test-key")

    responses = {
        devset[0]["id"]: RuntimeError("translator backend timed out"),
    }
    for example in devset[1:]:
        key = "mirad_text" if example["direction"] == "en_to_mir" else "english_text"
        responses[example["id"]] = {key: example["expected_text"]}

    translator = FakeTranslator(responses)
    result = run_baseline(
        devset_path=Path("data/eval/devset_s01_bidirectional.json"),
        output_dir=output_dir,
        translator_factory=_factory_for(translator),
    )

    error_row = result["rows"][0]
    assert error_row["status"] == "error"
    assert error_row["phase"] == "model_call"
    assert error_row["error"] == "RuntimeError: translator backend timed out"
    assert "Traceback" not in error_row["error"]
    assert result["summary"]["failed_example_count"] == 1
    assert result["summary"]["failed_example_ids"] == [devset[0]["id"]]

    report_text = result["report_path"].read_text(encoding="utf-8")
    assert "RuntimeError: translator backend timed out" in report_text
    assert "- phase: model_call" in report_text


def test_run_baseline_marks_non_string_prediction_as_parse_error(devset, output_dir, monkeypatch):
    monkeypatch.setenv("DEEPINFRA_API_KEY", "test-key")

    responses = {
        devset[0]["id"]: {"mirad_text": 12345},
    }
    for example in devset[1:]:
        key = "mirad_text" if example["direction"] == "en_to_mir" else "english_text"
        responses[example["id"]] = {key: example["expected_text"]}

    translator = FakeTranslator(responses)
    result = run_baseline(
        devset_path=Path("data/eval/devset_s01_bidirectional.json"),
        output_dir=output_dir,
        translator_factory=_factory_for(translator),
    )

    row = result["rows"][0]
    assert row["status"] == "error"
    assert row["phase"] == "parse_prediction"
    assert "non-string prediction type int" in row["error"]


def test_run_baseline_supports_dry_run_without_api_key(output_dir, monkeypatch):
    monkeypatch.delenv("DEEPINFRA_API_KEY", raising=False)

    result = run_baseline(
        devset_path=Path("data/eval/devset_s01_bidirectional.json"),
        output_dir=output_dir,
        dry_run=True,
    )

    assert result["summary"]["api_preflight"]["status"] == "not-required"
    assert result["summary"]["failed_example_count"] == 0
    assert all(row["status"] == "dry-run" for row in result["rows"])
    assert all(row["phase"] == "dry_run" for row in result["rows"])


def test_render_markdown_report_handles_preflight_failure_without_crashing():
    report_text = render_markdown_report(
        {"phase": "preflight", "error": "PreflightError: missing api key"},
        [],
    )

    assert "status: preflight-failed" in report_text
    assert "Preflight failed before predictions were generated" in report_text
    assert "No predictions were generated." in report_text


def test_render_markdown_report_rejects_missing_examples_key_fields():
    summary = {
        "started_at": "2026-01-01T00:00:00+00:00",
        "completed_at": "2026-01-01T00:00:01+00:00",
        "dry_run": False,
        "model": DEFAULT_MODEL,
        "api_preflight": {"status": "ok"},
        "devset_size": 1,
        "direction_counts": {"en_to_mir": 1, "mir_to_en": 0},
        "estimated_total_calls": 1,
        "estimated_cost_usd": 0.0,
        "total_calls": 1,
        "elapsed_ms": 1,
        "failed_example_count": 0,
        "failed_example_ids": [],
        "preflight": {"ok": True},
    }

    with pytest.raises(BaselineConfigError, match="report example 1 missing keys"):
        render_markdown_report(summary, [{"id": "missing-fields"}])


def test_write_markdown_report_does_not_leave_partial_file_on_schema_error(tmp_path):
    output_dir = tmp_path / "artifacts"
    output_dir.mkdir(parents=True, exist_ok=True)

    with pytest.raises(BaselineConfigError, match="report summary missing keys"):
        write_markdown_report(output_dir=output_dir, summary={"started_at": "only-one-key"}, rows=[])

    assert not (output_dir / "latest.md").exists()
