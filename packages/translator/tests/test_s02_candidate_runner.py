from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

MODULE_PATH = Path("packages/translator/scripts/run_s02_candidate_judge.py")
SPEC = importlib.util.spec_from_file_location("run_s02_candidate_judge", MODULE_PATH)
assert SPEC and SPEC.loader
run_s02_candidate_judge = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = run_s02_candidate_judge
SPEC.loader.exec_module(run_s02_candidate_judge)

DEFAULT_MODEL = run_s02_candidate_judge.DEFAULT_MODEL
DEFAULT_CANDIDATES_PER_EXAMPLE = run_s02_candidate_judge.DEFAULT_CANDIDATES_PER_EXAMPLE
PreflightError = run_s02_candidate_judge.PreflightError
RunnerConfigError = run_s02_candidate_judge.RunnerConfigError
load_devset = run_s02_candidate_judge.load_devset
preflight_devset = run_s02_candidate_judge.preflight_devset
render_markdown_report = run_s02_candidate_judge.render_markdown_report
run_candidate_judge = run_s02_candidate_judge.run_candidate_judge
write_markdown_report = run_s02_candidate_judge.write_markdown_report


class FakeCandidateGenerator:
    def __init__(self, responses):
        self._responses = responses
        self.calls = []

    def __call__(self, *, example, max_candidates):
        self.calls.append((example["id"], max_candidates))
        response = self._responses[example["id"]]
        if isinstance(response, Exception):
            raise response
        return response


class FakeJudgeRunner:
    def __init__(self, responses):
        self._responses = responses
        self.calls = []

    def __call__(self, *, example, candidates):
        self.calls.append((example["id"], [candidate["candidate_id"] for candidate in candidates]))
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


@pytest.fixture
def fake_candidate_map(devset):
    responses = {}
    for example in devset:
        responses[example["id"]] = [
            {
                "candidate_id": f"{example['id']}-cand-01",
                "prediction": example["expected_text"],
                "source": "generator-A",
                "prompt_variant": "baseline",
                "retrieval_rule_ids": ["rule.primary"],
                "retrieval_context": ["rule snippet one"],
                "raw_candidate_output": {"text": example["expected_text"], "rank": 1},
            },
            {
                "candidate_id": f"{example['id']}-cand-02",
                "prediction": f"wrong::{example['id']}",
                "source": "generator-B",
                "prompt_variant": "contrastive",
                "retrieval_rule_ids": ["rule.secondary"],
                "retrieval_context": ["rule snippet two"],
                "raw_candidate_output": {"text": f"wrong::{example['id']}", "rank": 2},
            },
        ]
    return responses


@pytest.fixture
def fake_judge_map(devset, fake_candidate_map):
    responses = {}
    for example in devset:
        candidates = fake_candidate_map[example["id"]]
        criteria_scores = {
            "semantic_fidelity": 0.95,
            "grammar": 0.9,
            "fluency" if example["direction"] == "en_to_mir" else "literalness": 0.88,
        }
        responses[example["id"]] = {
            "selected_candidate_id": candidates[0]["candidate_id"],
            "confidence": 0.84,
            "confidence_bucket": "medium",
            "passes_threshold": True,
            "rationale": f"Selected {candidates[0]['candidate_id']} for highest fidelity.",
            "criteria_scores": criteria_scores,
            "rejected_candidates": [
                {
                    "candidate_id": candidates[1]["candidate_id"],
                    "reason": "Dropped critical meaning.",
                }
            ],
            "raw_judge_output": {
                "decision": candidates[0]["candidate_id"],
                "notes": "kept for audit",
            },
        }
    return responses


def _candidate_factory(generator):
    def factory(*, dry_run, model):
        assert model == DEFAULT_MODEL
        assert dry_run is False
        return generator

    return factory



def _judge_factory(judge):
    def factory(*, dry_run, model):
        assert model == DEFAULT_MODEL
        assert dry_run is False
        return judge

    return factory



def test_preflight_estimates_candidate_and_judge_calls(devset):
    preflight = preflight_devset(
        devset,
        candidates_per_example=2,
        estimated_cost_per_call_usd=0.01,
        model=DEFAULT_MODEL,
    )

    assert preflight["devset_size"] == 12
    assert preflight["direction_counts"] == {"en_to_mir": 6, "mir_to_en": 6}
    assert preflight["estimated_total_calls"] == 36
    assert preflight["estimated_cost_usd"] == 0.36



def test_preflight_rejects_unbounded_candidate_count_without_override(devset):
    with pytest.raises(PreflightError, match="candidates_per_example 4 exceeds bounded safe limit 3"):
        preflight_devset(devset, candidates_per_example=4)



def test_run_candidate_judge_requires_api_key_for_live_mode(output_dir, monkeypatch):
    monkeypatch.delenv("DEEPINFRA_API_KEY", raising=False)

    with pytest.raises(PreflightError, match="DEEPINFRA_API_KEY"):
        run_candidate_judge(
            devset_path=Path("data/eval/devset_s01_bidirectional.json"),
            output_dir=output_dir,
            candidate_generator_factory=lambda **_: FakeCandidateGenerator({}),
            judge_runner_factory=lambda **_: FakeJudgeRunner({}),
        )



def test_run_candidate_judge_supports_dry_run_and_persists_artifacts(output_dir, monkeypatch):
    monkeypatch.delenv("DEEPINFRA_API_KEY", raising=False)

    result = run_candidate_judge(
        devset_path=Path("data/eval/devset_s01_bidirectional.json"),
        output_dir=output_dir,
        dry_run=True,
    )

    assert result["summary_path"].exists()
    assert result["examples_path"].exists()
    assert result["report_path"].exists()
    assert result["summary"]["api_preflight"]["status"] == "not-required"
    assert result["summary"]["estimated_total_calls"] == 48
    assert result["summary"]["failed_example_count"] == 0
    assert all(row["status"] == "dry-run" for row in result["rows"])
    assert all(row["phase"] == "dry_run" for row in result["rows"])
    assert all(row["selected_candidate"] is not None for row in result["rows"])
    assert all(row["raw_judge_output"]["mode"] == "dry-run" for row in result["rows"])

    report_text = result["report_path"].read_text(encoding="utf-8")
    assert "# M006 S02 Candidate Judge Inspection Report" in report_text
    assert "## Run Metadata" in report_text
    assert "## Preflight Call and Cost Estimate" in report_text
    assert "## Per-Example Summary" in report_text
    assert "## Detailed Examples" in report_text



def test_run_candidate_judge_persists_selected_rejected_candidates_and_judge_fields(
    devset,
    output_dir,
    monkeypatch,
    fake_candidate_map,
    fake_judge_map,
):
    monkeypatch.setenv("DEEPINFRA_API_KEY", "test-key")

    candidate_generator = FakeCandidateGenerator(fake_candidate_map)
    judge_runner = FakeJudgeRunner(fake_judge_map)
    result = run_candidate_judge(
        devset_path=Path("data/eval/devset_s01_bidirectional.json"),
        output_dir=output_dir,
        candidates_per_example=2,
        estimated_cost_per_call_usd=0.01,
        candidate_generator_factory=_candidate_factory(candidate_generator),
        judge_runner_factory=_judge_factory(judge_runner),
    )

    assert result["summary"]["failed_example_count"] == 0
    assert result["summary"]["estimated_total_calls"] == 36
    assert result["summary"]["total_calls"] == 36
    assert len(candidate_generator.calls) == len(devset)
    assert len(judge_runner.calls) == len(devset)

    first = result["rows"][0]
    assert first["status"] == "ok"
    assert first["phase"] == "judge_scoring"
    assert first["candidate_count"] == 2
    assert first["selected_candidate"]["candidate_id"].endswith("cand-01")
    assert first["selected_candidate"]["is_selected"] is True
    assert first["rejected_candidates"][0]["candidate_id"].endswith("cand-02")
    assert first["rejected_candidates"][0]["rejection_reason"] == "Dropped critical meaning."
    assert first["judge_summary"]["criteria_scores"]["semantic_fidelity"] == pytest.approx(0.95)
    assert first["judge_summary"]["confidence_bucket"] == "medium"
    assert first["judge_summary"]["passes_threshold"] is True
    assert first["judge_summary"]["rationale"].startswith("Selected")
    assert first["raw_judge_output"] == {"decision": first["selected_candidate"]["candidate_id"], "notes": "kept for audit"}
    assert first["estimated_calls"] == 3
    assert first["estimated_cost_usd"] == 0.03

    disk_rows = json.loads(result["examples_path"].read_text(encoding="utf-8"))
    assert disk_rows[0]["selected_candidate"]["candidate_id"] == first["selected_candidate"]["candidate_id"]
    assert disk_rows[0]["rejected_candidates"][0]["rejection_reason"] == "Dropped critical meaning."



def test_run_candidate_judge_records_candidate_generation_error_row(
    devset,
    output_dir,
    monkeypatch,
    fake_candidate_map,
    fake_judge_map,
):
    monkeypatch.setenv("DEEPINFRA_API_KEY", "test-key")
    fake_candidate_map = dict(fake_candidate_map)
    fake_candidate_map[devset[0]["id"]] = RuntimeError("generator backend timed out")

    result = run_candidate_judge(
        devset_path=Path("data/eval/devset_s01_bidirectional.json"),
        output_dir=output_dir,
        candidates_per_example=2,
        candidate_generator_factory=_candidate_factory(FakeCandidateGenerator(fake_candidate_map)),
        judge_runner_factory=_judge_factory(FakeJudgeRunner(fake_judge_map)),
    )

    row = result["rows"][0]
    assert row["status"] == "error"
    assert row["phase"] == "candidate_generation"
    assert row["error"] == "CandidateGeneratorError: generator backend timed out"
    assert row["selected_candidate"] is None
    assert row["rejected_candidates"] == []
    assert "Traceback" not in row["error"]
    assert result["summary"]["failed_example_ids"] == [devset[0]["id"]]



def test_run_candidate_judge_records_judge_execution_error_row(
    devset,
    output_dir,
    monkeypatch,
    fake_candidate_map,
    fake_judge_map,
):
    monkeypatch.setenv("DEEPINFRA_API_KEY", "test-key")
    fake_judge_map = dict(fake_judge_map)
    fake_judge_map[devset[0]["id"]] = RuntimeError("judge backend unavailable")

    result = run_candidate_judge(
        devset_path=Path("data/eval/devset_s01_bidirectional.json"),
        output_dir=output_dir,
        candidates_per_example=2,
        candidate_generator_factory=_candidate_factory(FakeCandidateGenerator(fake_candidate_map)),
        judge_runner_factory=_judge_factory(FakeJudgeRunner(fake_judge_map)),
    )

    row = result["rows"][0]
    assert row["status"] == "error"
    assert row["phase"] == "judge_execution"
    assert row["error"] == "JudgeExecutionError: judge backend unavailable"
    assert row["selected_candidate"] is None
    assert row["rejected_candidates"] == []
    assert "Traceback" not in row["error"]



def test_render_markdown_report_handles_preflight_failure_without_crashing():
    report_text = render_markdown_report(
        {"phase": "preflight", "error": "PreflightError: missing api key"},
        [],
    )

    assert "status: preflight-failed" in report_text
    assert "Preflight failed before candidate generation or judging started." in report_text
    assert "No examples available." in report_text



def test_write_markdown_report_does_not_leave_partial_file_on_schema_error(tmp_path):
    output_dir = tmp_path / "artifacts"
    output_dir.mkdir(parents=True, exist_ok=True)

    with pytest.raises(RunnerConfigError, match="report summary missing keys"):
        write_markdown_report(output_dir=output_dir, summary={"started_at": "only-one-key"}, rows=[])

    assert not (output_dir / "latest.md").exists()
