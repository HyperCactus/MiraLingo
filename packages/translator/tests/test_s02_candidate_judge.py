from __future__ import annotations

import importlib
from copy import deepcopy
from pathlib import Path

import pytest

DEVSET_PATH = Path("data/eval/devset_s01_bidirectional.json")

candidate_judge = importlib.import_module("mirad_translator.candidate_judge")

load_devset = candidate_judge.load_devset
build_candidate_record = candidate_judge.build_candidate_record
score_judge_output = candidate_judge.score_judge_output
evaluate_example_candidates = candidate_judge.evaluate_example_candidates
CandidateJudgeContractError = candidate_judge.CandidateJudgeContractError


@pytest.fixture
def devset():
    return load_devset(DEVSET_PATH)


@pytest.fixture
def example(devset):
    return deepcopy(devset[0])


@pytest.fixture
def base_candidates(example):
    return [
        {
            "candidate_id": f"{example['id']}-cand-01",
            "prediction": example["expected_text"],
            "source": "generator-A",
            "prompt_variant": "baseline",
            "retrieval_rule_ids": ["rule.progressive"],
            "retrieval_context": ["rule snippet one"],
            "raw_candidate_output": {"text": example["expected_text"]},
        },
        {
            "candidate_id": f"{example['id']}-cand-02",
            "prediction": "It peya dom.",
            "source": "generator-B",
            "prompt_variant": "baseline",
            "retrieval_rule_ids": ["rule.motion"],
            "retrieval_context": ["rule snippet two"],
            "raw_candidate_output": {"text": "It peya dom."},
        },
        {
            "candidate_id": f"{example['id']}-cand-03",
            "prediction": "Peya tam.",
            "source": "generator-C",
            "prompt_variant": "ablation",
            "retrieval_rule_ids": [],
            "retrieval_context": [],
            "raw_candidate_output": {"text": "Peya tam."},
        },
    ]


@pytest.fixture
def valid_judge_payload(base_candidates):
    return {
        "selected_candidate_id": base_candidates[0]["candidate_id"],
        "confidence": 0.93,
        "confidence_bucket": "high",
        "passes_threshold": True,
        "rationale": "Candidate 1 best preserves tense, pronoun, and destination.",
        "criteria_scores": {
            "semantic_fidelity": 0.98,
            "grammar": 0.91,
            "fluency": 0.9,
        },
        "rejected_candidates": [
            {
                "candidate_id": base_candidates[1]["candidate_id"],
                "reason": "Wrong destination noun.",
            },
            {
                "candidate_id": base_candidates[2]["candidate_id"],
                "reason": "Drops pronoun and tense marking.",
            },
        ],
        "raw_judge_output": {
            "decision": "choose candidate 1",
            "notes": "kept for audit",
        },
    }


def test_build_candidate_record_preserves_candidate_audit_fields(example, base_candidates):
    record = build_candidate_record(
        example=example,
        candidate=base_candidates[0],
        candidate_index=1,
        max_candidates=3,
    )

    assert record["example_id"] == example["id"]
    assert record["direction"] == example["direction"]
    assert record["candidate_id"] == base_candidates[0]["candidate_id"]
    assert record["candidate_rank"] == 1
    assert record["candidate_count"] == 3
    assert record["is_selected"] is False
    assert record["is_rejected"] is False
    assert record["prediction"] == example["expected_text"]
    assert record["source"] == "generator-A"
    assert record["prompt_variant"] == "baseline"
    assert record["retrieval_rule_ids"] == ["rule.progressive"]
    assert record["retrieval_context"] == ["rule snippet one"]
    assert record["raw_candidate_output"] == {"text": example["expected_text"]}


def test_score_judge_output_partitions_selected_and_rejected_candidates(example, base_candidates, valid_judge_payload):
    result = score_judge_output(
        example=example,
        candidates=deepcopy(base_candidates),
        judge_payload=deepcopy(valid_judge_payload),
        max_candidates=3,
    )

    selected = result["selected_candidate"]
    rejected = result["rejected_candidates"]
    summary = result["judge_summary"]

    assert selected["candidate_id"] == base_candidates[0]["candidate_id"]
    assert selected["is_selected"] is True
    assert selected["is_rejected"] is False
    assert len(rejected) == 2
    assert {row["candidate_id"] for row in rejected} == {
        base_candidates[1]["candidate_id"],
        base_candidates[2]["candidate_id"],
    }
    assert all(row["is_rejected"] is True for row in rejected)
    assert summary["selected_candidate_id"] == base_candidates[0]["candidate_id"]
    assert summary["candidate_count"] == 3
    assert summary["passes_threshold"] is True
    assert summary["confidence"] == pytest.approx(0.93)
    assert summary["confidence_bucket"] == "high"
    assert summary["raw_judge_output"] == valid_judge_payload["raw_judge_output"]


def test_score_judge_output_aggregates_multi_criteria_scores(example, base_candidates, valid_judge_payload):
    result = score_judge_output(
        example=example,
        candidates=deepcopy(base_candidates),
        judge_payload=deepcopy(valid_judge_payload),
        max_candidates=3,
    )

    summary = result["judge_summary"]
    selected = result["selected_candidate"]

    assert summary["criteria_scores"] == {
        "semantic_fidelity": pytest.approx(0.98),
        "grammar": pytest.approx(0.91),
        "fluency": pytest.approx(0.9),
    }
    assert summary["aggregate_score"] == pytest.approx((0.98 + 0.91 + 0.9) / 3)
    assert selected["criteria_scores"] == summary["criteria_scores"]
    assert selected["aggregate_score"] == summary["aggregate_score"]


@pytest.mark.parametrize(
    ("confidence", "expected_bucket", "expected_passes"),
    [
        (0.91, "high", True),
        (0.70, "medium", True),
        (0.49, "low", False),
    ],
)
def test_score_judge_output_calibrates_confidence_bucket_and_pass_fail(
    example,
    base_candidates,
    valid_judge_payload,
    confidence,
    expected_bucket,
    expected_passes,
):
    payload = deepcopy(valid_judge_payload)
    payload["confidence"] = confidence
    payload["confidence_bucket"] = expected_bucket
    payload["passes_threshold"] = expected_passes

    result = score_judge_output(
        example=example,
        candidates=deepcopy(base_candidates),
        judge_payload=payload,
        max_candidates=3,
    )

    summary = result["judge_summary"]
    assert summary["confidence"] == pytest.approx(confidence)
    assert summary["confidence_bucket"] == expected_bucket
    assert summary["passes_threshold"] is expected_passes


def test_score_judge_output_preserves_raw_rationale_and_raw_output(example, base_candidates, valid_judge_payload):
    result = score_judge_output(
        example=example,
        candidates=deepcopy(base_candidates),
        judge_payload=deepcopy(valid_judge_payload),
        max_candidates=3,
    )

    summary = result["judge_summary"]
    selected = result["selected_candidate"]

    assert summary["rationale"] == valid_judge_payload["rationale"]
    assert summary["raw_judge_output"] == valid_judge_payload["raw_judge_output"]
    assert selected["judge_rationale"] == valid_judge_payload["rationale"]
    assert selected["raw_judge_output"] == valid_judge_payload["raw_judge_output"]


def test_evaluate_example_candidates_returns_structured_stacktrace_free_error_for_malformed_judge_payload(
    example,
    base_candidates,
    valid_judge_payload,
):
    payload = deepcopy(valid_judge_payload)
    del payload["selected_candidate_id"]

    result = evaluate_example_candidates(
        example=example,
        candidates=deepcopy(base_candidates),
        judge_payload=payload,
        max_candidates=3,
    )

    assert result["status"] == "error"
    assert result["phase"] == "judge_scoring"
    assert result["example_id"] == example["id"]
    assert result["direction"] == example["direction"]
    assert result["candidate_count"] == 3
    assert result["passes_threshold"] is False
    assert result["selected_candidate"] is None
    assert result["rejected_candidates"] == []
    assert result["raw_judge_output"] == payload.get("raw_judge_output")
    assert "selected_candidate_id" in result["error"]
    assert "Traceback" not in result["error"]
    assert "candidate_judge.py" not in result["error"]


def test_evaluate_example_candidates_fails_closed_for_zero_candidates(example, valid_judge_payload):
    result = evaluate_example_candidates(
        example=example,
        candidates=[],
        judge_payload=deepcopy(valid_judge_payload),
        max_candidates=3,
    )

    assert result["status"] == "error"
    assert result["phase"] == "judge_scoring"
    assert result["candidate_count"] == 0
    assert result["passes_threshold"] is False
    assert result["selected_candidate"] is None
    assert result["rejected_candidates"] == []
    assert "no candidates" in result["error"].lower()
    assert "Traceback" not in result["error"]


def test_score_judge_output_rejects_non_numeric_criteria_scores(example, base_candidates, valid_judge_payload):
    payload = deepcopy(valid_judge_payload)
    payload["criteria_scores"]["grammar"] = "strong"

    with pytest.raises(CandidateJudgeContractError, match=r"criteria_scores\.grammar.*numeric"):
        score_judge_output(
            example=example,
            candidates=deepcopy(base_candidates),
            judge_payload=payload,
            max_candidates=3,
        )


def test_score_judge_output_rejects_missing_rationale(example, base_candidates, valid_judge_payload):
    payload = deepcopy(valid_judge_payload)
    payload["rationale"] = ""

    with pytest.raises(CandidateJudgeContractError, match="rationale"):
        score_judge_output(
            example=example,
            candidates=deepcopy(base_candidates),
            judge_payload=payload,
            max_candidates=3,
        )


def test_score_judge_output_rejects_out_of_range_confidence(example, base_candidates, valid_judge_payload):
    payload = deepcopy(valid_judge_payload)
    payload["confidence"] = 1.2

    with pytest.raises(CandidateJudgeContractError, match="confidence.*0.*1"):
        score_judge_output(
            example=example,
            candidates=deepcopy(base_candidates),
            judge_payload=payload,
            max_candidates=3,
        )


def test_score_judge_output_enforces_bounded_default_candidate_count(example, base_candidates, valid_judge_payload):
    candidates = deepcopy(base_candidates) + [
        {
            "candidate_id": f"{example['id']}-cand-04",
            "prediction": "overflow",
            "source": "generator-D",
            "prompt_variant": "overflow",
            "retrieval_rule_ids": [],
            "retrieval_context": [],
            "raw_candidate_output": {"text": "overflow"},
        }
    ]

    with pytest.raises(CandidateJudgeContractError, match="max_candidates"):
        score_judge_output(
            example=example,
            candidates=candidates,
            judge_payload=deepcopy(valid_judge_payload),
            max_candidates=3,
        )
