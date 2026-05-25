from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

MODULE_PATH = Path("packages/translator/scripts/run_s03_retrieval_eval.py")
SPEC = importlib.util.spec_from_file_location("run_s03_retrieval_eval", MODULE_PATH)
assert SPEC and SPEC.loader
run_s03_retrieval_eval = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = run_s03_retrieval_eval
SPEC.loader.exec_module(run_s03_retrieval_eval)

DEFAULT_MODEL = run_s03_retrieval_eval.DEFAULT_MODEL
DEFAULT_ESTIMATED_CALLS_PER_EXAMPLE = run_s03_retrieval_eval.DEFAULT_ESTIMATED_CALLS_PER_EXAMPLE
PreflightError = run_s03_retrieval_eval.PreflightError
RetrievalStrategyConfig = run_s03_retrieval_eval.RetrievalStrategyConfig
load_devset = run_s03_retrieval_eval.load_devset
preflight_devset = run_s03_retrieval_eval.preflight_devset
render_markdown_report = run_s03_retrieval_eval.render_markdown_report
run_retrieval_eval = run_s03_retrieval_eval.run_retrieval_eval
write_markdown_report = run_s03_retrieval_eval.write_markdown_report
main = run_s03_retrieval_eval.main


class FakeTranslator:
    def __init__(self, *, variant, responses):
        self.variant = variant
        self.responses = responses
        self.calls = []

    def __call__(self, source_text, direction, example, index):
        self.calls.append((self.variant, source_text, direction, example["id"], index))
        response = self.responses[example["id"]]
        if isinstance(response, Exception):
            raise response
        return response


@pytest.fixture
def devset() -> list[dict]:
    return load_devset(Path("data/eval/devset_s01_bidirectional.json"))


@pytest.fixture
def output_dir(tmp_path) -> Path:
    return tmp_path / "artifacts"


@pytest.fixture
def fake_factory(devset):
    baseline_responses = {}
    improved_responses = {}
    for idx, example in enumerate(devset):
        output_key = "mirad_text" if example["direction"] == "en_to_mir" else "english_text"
        payload = {
            "normalized_search_terms": ["taxonomy", f"term-{idx}"],
            "lexicon_pairs": [{"source": "s", "target": "t", "match_type": "semantic"}],
            "grammar_rules": [{"rule_id": f"rule.{idx:02d}", "passage": f"rule passage {idx}", "source_section": "tests"}],
            "few_shot_examples": [{"id": devset[(idx + 1) % len(devset)]["id"], "direction": example["direction"], "source_text": "x", "expected_text": "y", "taxonomy_focus": ["focus"], "score": 11}],
            "warnings": [],
        }
        baseline_responses[example["id"]] = {
            output_key: example["expected_text"] if idx == 0 else f"baseline::{idx}",
            "retrieval_payload": payload,
        }
        improved_responses[example["id"]] = {
            output_key: example["expected_text"] if idx in {0, 1} else f"improved::{idx}",
            "retrieval_payload": payload,
        }

    baseline = FakeTranslator(variant="baseline", responses=baseline_responses)
    improved = FakeTranslator(variant="improved", responses=improved_responses)

    def factory(*, dry_run, model, variant, devset, strategy_config):
        assert dry_run is False
        assert model == DEFAULT_MODEL
        assert isinstance(strategy_config, RetrievalStrategyConfig)
        return baseline if variant == "baseline" else improved

    return factory, baseline, improved


def test_preflight_reports_bounded_calls(devset):
    preflight = preflight_devset(
        devset,
        estimated_calls_per_example=DEFAULT_ESTIMATED_CALLS_PER_EXAMPLE,
        estimated_cost_per_call_usd=0.01,
        model=DEFAULT_MODEL,
    )

    assert preflight["devset_size"] == 12
    assert preflight["direction_counts"] == {"en_to_mir": 6, "mir_to_en": 6}
    assert preflight["estimated_total_calls"] == 24
    assert preflight["estimated_cost_usd"] == 0.24


def test_preflight_rejects_dataset_over_limit_without_override(devset):
    expanded = devset + [dict(devset[0], id=f"extra-{n}") for n in range(4)]
    with pytest.raises(PreflightError, match="exceeding bounded limit 15"):
        preflight_devset(expanded)


def test_run_retrieval_eval_supports_dry_run_and_persists_comparison_artifacts(output_dir, monkeypatch):
    monkeypatch.delenv("DEEPINFRA_API_KEY", raising=False)

    result = run_retrieval_eval(
        devset_path=Path("data/eval/devset_s01_bidirectional.json"),
        output_dir=output_dir,
        dry_run=True,
    )

    assert result["summary_path"].exists()
    assert result["examples_path"].exists()
    assert result["report_path"].exists()
    assert result["summary"]["api_preflight"]["status"] == "not-required"
    assert result["summary"]["estimated_total_calls"] == 24
    assert result["summary"]["failed_example_count"] == 0
    assert result["summary"]["delta_counts"] == {
        "improved": 3,
        "regressed": 3,
        "pass": 3,
        "fail": 3,
        "held": 0,
        "error": 0,
    }

    first = result["rows"][0]
    assert first["status"] == "dry-run"
    assert first["phase"] == "dry_run"
    assert sorted(first["improved_retrieval"].keys()) == [
        "few_shot_examples",
        "grammar_rules",
        "lexicon_pairs",
        "normalized_search_terms",
        "warnings",
    ]
    assert isinstance(first["selected_examples"], list)
    assert isinstance(first["retrieval_rule_ids"], list)

    report_text = result["report_path"].read_text(encoding="utf-8")
    assert "# M006 S03 Retrieval Comparison Report" in report_text
    assert "## Strategy Config" in report_text
    assert "## Delta Summary" in report_text
    assert "## Detailed Examples" in report_text


def test_run_retrieval_eval_uses_injected_live_translators_and_persists_rows(output_dir, monkeypatch, fake_factory):
    monkeypatch.setenv("DEEPINFRA_API_KEY", "test-key")
    factory, baseline, improved = fake_factory

    result = run_retrieval_eval(
        devset_path=Path("data/eval/devset_s01_bidirectional.json"),
        output_dir=output_dir,
        translator_factory=factory,
        estimated_cost_per_call_usd=0.01,
    )

    assert len(baseline.calls) == 12
    assert len(improved.calls) == 12
    assert result["summary"]["estimated_total_calls"] == 24
    assert result["summary"]["total_calls"] == 24
    assert result["summary"]["failed_example_count"] == 0
    assert result["summary"]["delta_counts"]["improved"] == 1
    assert result["summary"]["delta_counts"]["pass"] == 1
    assert result["summary"]["delta_counts"]["fail"] == 10

    improved_row = result["rows"][1]
    assert improved_row["delta_classification"] == "improved"
    assert improved_row["baseline_normalized_match"] is False
    assert improved_row["improved_normalized_match"] is True
    assert improved_row["retrieval_rule_ids"] == ["rule.01"]
    assert len(improved_row["selected_examples"]) == 1

    disk_rows = json.loads(result["examples_path"].read_text(encoding="utf-8"))
    assert disk_rows[1]["delta_classification"] == "improved"


def test_main_writes_stacktrace_free_preflight_summary_when_api_key_missing(tmp_path, monkeypatch):
    monkeypatch.delenv("DEEPINFRA_API_KEY", raising=False)
    output_dir = tmp_path / "cli-artifacts"

    exit_code = main([
        "--output-dir",
        str(output_dir),
    ])

    assert exit_code == 2
    summary = json.loads((output_dir / "run_summary.json").read_text(encoding="utf-8"))
    assert summary["phase"] == "preflight"
    assert "DEEPINFRA_API_KEY" in summary["error"]
    assert "Traceback" not in summary["error"]


def test_render_markdown_report_handles_preflight_failure_without_crashing():
    report_text = render_markdown_report(
        {"phase": "preflight", "error": "PreflightError: missing api key"},
        [],
    )

    assert "status: preflight-failed" in report_text
    assert "Preflight failed before baseline/improved comparisons started." in report_text
    assert "No comparisons were generated." in report_text


def test_write_markdown_report_does_not_leave_partial_file_on_schema_error(tmp_path):
    output_dir = tmp_path / "artifacts"
    output_dir.mkdir(parents=True, exist_ok=True)

    with pytest.raises(Exception, match="report summary missing keys"):
        write_markdown_report(output_dir=output_dir, summary={"started_at": "only"}, rows=[])

    assert not (output_dir / "latest.md").exists()
