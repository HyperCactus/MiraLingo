from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable


ALLOWED_DIRECTIONS = {"en_to_mir", "mir_to_en"}
REQUIRED_DEVSET_FIELDS = {
    "id",
    "direction",
    "source_text",
    "expected_text",
    "rationale",
    "taxonomy_focus",
    "source_reference",
}
DEFAULT_MAX_CANDIDATES = 3
CONFIDENCE_THRESHOLDS = {
    "high": 0.85,
    "medium": 0.6,
    "pass": 0.6,
}
DEFAULT_CRITERIA_BY_DIRECTION = {
    "en_to_mir": [
        "semantic_fidelity",
        "grammar",
        "direction_correctness",
        "fluency",
    ],
    "mir_to_en": [
        "semantic_fidelity",
        "grammar",
        "direction_correctness",
        "literalness",
    ],
}


class CandidateJudgeContractError(ValueError):
    """Raised when candidate or judge payloads violate the S02 contract."""


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    prediction: str
    source: str = "unknown"
    prompt_variant: str = "default"
    retrieval_rule_ids: list[str] = field(default_factory=list)
    retrieval_context: list[str] = field(default_factory=list)
    raw_candidate_output: Any = None


@dataclass(frozen=True)
class JudgeScore:
    selected_candidate_id: str
    confidence: float
    confidence_bucket: str
    passes_threshold: bool
    rationale: str
    criteria_scores: dict[str, float]
    aggregate_score: float
    rejected_candidates: list[dict[str, str]]
    raw_judge_output: Any = None


@dataclass(frozen=True)
class CandidateJudgeRow:
    example_id: str
    direction: str
    candidate_id: str
    candidate_rank: int
    candidate_count: int
    prediction: str
    source: str
    prompt_variant: str
    retrieval_rule_ids: list[str]
    retrieval_context: list[str]
    raw_candidate_output: Any
    is_selected: bool = False
    is_rejected: bool = False
    rejection_reason: str | None = None
    criteria_scores: dict[str, float] | None = None
    aggregate_score: float | None = None
    judge_rationale: str | None = None
    raw_judge_output: Any = None


def load_devset(path: Path) -> list[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    _validate_devset(payload)
    return payload


def _validate_devset(payload: Any) -> None:
    if not isinstance(payload, list):
        raise CandidateJudgeContractError("dev-set must be a list")
    ids: set[str] = set()
    directions: set[str] = set()
    for index, example in enumerate(payload, start=1):
        example_id = example.get("id", f"index-{index}") if isinstance(example, dict) else f"index-{index}"
        if not isinstance(example, dict):
            raise CandidateJudgeContractError(f"{example_id}: each example must be an object")
        missing = sorted(REQUIRED_DEVSET_FIELDS - set(example))
        if missing:
            raise CandidateJudgeContractError(f"{example_id}: missing required fields {missing}")
        if example_id in ids:
            raise CandidateJudgeContractError(f"{example_id}: duplicate id")
        ids.add(example_id)
        direction = example["direction"]
        if direction not in ALLOWED_DIRECTIONS:
            raise CandidateJudgeContractError(f"{example_id}: unknown direction '{direction}'")
        directions.add(direction)
    if directions and directions != ALLOWED_DIRECTIONS:
        raise CandidateJudgeContractError(f"dev-set must include both directions, got {sorted(directions)}")


def build_candidate_record(
    *,
    example: dict[str, Any],
    candidate: dict[str, Any] | Candidate,
    candidate_index: int,
    max_candidates: int,
) -> dict[str, Any]:
    candidate_obj = _coerce_candidate(candidate)
    if candidate_index < 1:
        raise CandidateJudgeContractError("candidate_index must be >= 1")
    if max_candidates < 1:
        raise CandidateJudgeContractError("max_candidates must be >= 1")
    return asdict(
        CandidateJudgeRow(
            example_id=_require_non_empty_string(example, "id"),
            direction=_require_direction(example),
            candidate_id=candidate_obj.candidate_id,
            candidate_rank=candidate_index,
            candidate_count=max_candidates,
            prediction=candidate_obj.prediction,
            source=candidate_obj.source,
            prompt_variant=candidate_obj.prompt_variant,
            retrieval_rule_ids=list(candidate_obj.retrieval_rule_ids),
            retrieval_context=list(candidate_obj.retrieval_context),
            raw_candidate_output=candidate_obj.raw_candidate_output,
        )
    )


def generate_dry_run_candidates(
    *,
    example: dict[str, Any],
    base_prediction: str,
    expected_text: str | None = None,
    max_candidates: int = DEFAULT_MAX_CANDIDATES,
) -> list[dict[str, Any]]:
    if max_candidates < 1:
        raise CandidateJudgeContractError("max_candidates must be >= 1")
    example_id = _require_non_empty_string(example, "id")
    expected = (expected_text or example.get("expected_text") or "").strip()
    base = (base_prediction or "").strip()
    source = (example.get("source_text") or "").strip()
    variants = [
        base or expected,
        expected or base,
        source or base or expected,
    ]
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    for idx, prediction in enumerate(variants, start=1):
        if not prediction or prediction in seen:
            continue
        seen.add(prediction)
        candidates.append(
            {
                "candidate_id": f"{example_id}-cand-{idx:02d}",
                "prediction": prediction,
                "source": f"dry-run-{idx}",
                "prompt_variant": "deterministic",
                "retrieval_rule_ids": [],
                "retrieval_context": [],
                "raw_candidate_output": {"text": prediction, "mode": "dry-run"},
            }
        )
        if len(candidates) >= max_candidates:
            break
    if not candidates:
        raise CandidateJudgeContractError("no candidates generated for dry run")
    return candidates


def make_candidate_generator(generator: Callable[..., Any]) -> Callable[..., list[dict[str, Any]]]:
    def wrapped(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        raw = generator(*args, **kwargs)
        return normalize_candidate_outputs(raw)

    return wrapped


def make_judge_runner(judge: Callable[..., Any]) -> Callable[..., dict[str, Any]]:
    def wrapped(*args: Any, **kwargs: Any) -> dict[str, Any]:
        raw = judge(*args, **kwargs)
        if not isinstance(raw, dict):
            raise CandidateJudgeContractError("judge output must be an object")
        return raw

    return wrapped


def normalize_candidate_outputs(raw_candidates: Any) -> list[dict[str, Any]]:
    if raw_candidates is None:
        return []
    if not isinstance(raw_candidates, list):
        raise CandidateJudgeContractError("candidates must be a list")
    normalized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, raw_candidate in enumerate(raw_candidates, start=1):
        candidate = _coerce_candidate(raw_candidate, fallback_id=f"candidate-{index:02d}")
        if candidate.candidate_id in seen_ids:
            raise CandidateJudgeContractError(f"duplicate candidate ids: {candidate.candidate_id}")
        seen_ids.add(candidate.candidate_id)
        normalized.append(asdict(candidate))
    return normalized


def score_judge_output(
    *,
    example: dict[str, Any],
    candidates: list[dict[str, Any]] | list[Candidate],
    judge_payload: dict[str, Any],
    max_candidates: int = DEFAULT_MAX_CANDIDATES,
) -> dict[str, Any]:
    normalized_candidates = normalize_candidate_outputs(candidates)
    if not normalized_candidates:
        raise CandidateJudgeContractError("no candidates available for judging")
    if len(normalized_candidates) > max_candidates:
        raise CandidateJudgeContractError(f"candidate count exceeds max_candidates={max_candidates}")
    score = parse_judge_output(
        judge_payload=judge_payload,
        direction=_require_direction(example),
        candidate_ids=[candidate["candidate_id"] for candidate in normalized_candidates],
    )

    rejected_reasons = {
        item["candidate_id"]: item["reason"]
        for item in score.rejected_candidates
    }
    selected_row: dict[str, Any] | None = None
    rejected_rows: list[dict[str, Any]] = []

    for index, candidate in enumerate(normalized_candidates, start=1):
        row = build_candidate_record(
            example=example,
            candidate=candidate,
            candidate_index=index,
            max_candidates=len(normalized_candidates),
        )
        row["criteria_scores"] = dict(score.criteria_scores)
        row["aggregate_score"] = score.aggregate_score
        row["judge_rationale"] = score.rationale
        row["raw_judge_output"] = score.raw_judge_output

        candidate_id = row["candidate_id"]
        if candidate_id == score.selected_candidate_id:
            row["is_selected"] = True
            selected_row = row
        elif candidate_id in rejected_reasons:
            row["is_rejected"] = True
            row["rejection_reason"] = rejected_reasons[candidate_id]
            rejected_rows.append(row)

    if selected_row is None:
        raise CandidateJudgeContractError("selected_candidate_id does not match any candidate")

    summary = asdict(score)
    summary["candidate_count"] = len(normalized_candidates)
    return {
        "selected_candidate": selected_row,
        "rejected_candidates": rejected_rows,
        "judge_summary": summary,
    }


def parse_judge_output(
    *,
    judge_payload: dict[str, Any],
    direction: str,
    candidate_ids: list[str],
) -> JudgeScore:
    if not isinstance(judge_payload, dict):
        raise CandidateJudgeContractError("judge payload must be an object")

    selected_candidate_id = _require_non_empty_string(judge_payload, "selected_candidate_id")
    if selected_candidate_id not in candidate_ids:
        raise CandidateJudgeContractError("selected_candidate_id does not match a provided candidate")

    confidence = _require_numeric(judge_payload, "confidence")
    if not 0.0 <= confidence <= 1.0:
        raise CandidateJudgeContractError("confidence must be between 0 and 1")

    rationale = _require_non_empty_string(judge_payload, "rationale")
    criteria_scores = _normalize_criteria_scores(judge_payload.get("criteria_scores"), direction)
    aggregate_score = calculate_aggregate_score(criteria_scores)
    confidence_bucket = assign_confidence_bucket(confidence)
    passes_threshold = confidence >= CONFIDENCE_THRESHOLDS["pass"]

    given_bucket = judge_payload.get("confidence_bucket")
    if given_bucket is not None and given_bucket != confidence_bucket:
        raise CandidateJudgeContractError(
            f"confidence_bucket mismatch: expected '{confidence_bucket}' for confidence {confidence}"
        )
    given_passes = judge_payload.get("passes_threshold")
    if given_passes is not None and bool(given_passes) is not passes_threshold:
        raise CandidateJudgeContractError(
            f"passes_threshold mismatch: expected {passes_threshold} for confidence {confidence}"
        )

    rejected_candidates = judge_payload.get("rejected_candidates") or []
    if not isinstance(rejected_candidates, list):
        raise CandidateJudgeContractError("rejected_candidates must be a list")

    normalized_rejections: list[dict[str, str]] = []
    seen_rejected: set[str] = set()
    for item in rejected_candidates:
        if not isinstance(item, dict):
            raise CandidateJudgeContractError("rejected_candidates items must be objects")
        candidate_id = _require_non_empty_string(item, "candidate_id")
        reason = _require_non_empty_string(item, "reason")
        if candidate_id == selected_candidate_id:
            raise CandidateJudgeContractError("selected candidate cannot also be rejected")
        if candidate_id not in candidate_ids:
            raise CandidateJudgeContractError(f"rejected candidate not found: {candidate_id}")
        if candidate_id in seen_rejected:
            raise CandidateJudgeContractError(f"duplicate rejected candidate id: {candidate_id}")
        seen_rejected.add(candidate_id)
        normalized_rejections.append({"candidate_id": candidate_id, "reason": reason})

    return JudgeScore(
        selected_candidate_id=selected_candidate_id,
        confidence=confidence,
        confidence_bucket=confidence_bucket,
        passes_threshold=passes_threshold,
        rationale=rationale,
        criteria_scores=criteria_scores,
        aggregate_score=aggregate_score,
        rejected_candidates=normalized_rejections,
        raw_judge_output=judge_payload.get("raw_judge_output"),
    )


def calculate_aggregate_score(criteria_scores: dict[str, float]) -> float:
    if not criteria_scores:
        raise CandidateJudgeContractError("criteria_scores must not be empty")
    return sum(criteria_scores.values()) / len(criteria_scores)


def assign_confidence_bucket(confidence: float) -> str:
    if not 0.0 <= confidence <= 1.0:
        raise CandidateJudgeContractError("confidence must be between 0 and 1")
    if confidence >= CONFIDENCE_THRESHOLDS["high"]:
        return "high"
    if confidence >= CONFIDENCE_THRESHOLDS["medium"]:
        return "medium"
    return "low"


def evaluate_example_candidates(
    *,
    example: dict[str, Any],
    candidates: list[dict[str, Any]] | list[Candidate],
    judge_payload: dict[str, Any] | None = None,
    candidate_generator: Callable[..., Any] | None = None,
    judge_runner: Callable[..., Any] | None = None,
    max_candidates: int = DEFAULT_MAX_CANDIDATES,
) -> dict[str, Any]:
    try:
        normalized_candidates = normalize_candidate_outputs(candidates)
        if candidate_generator is not None and not normalized_candidates:
            normalized_candidates = make_candidate_generator(candidate_generator)(example=example)
        if not normalized_candidates:
            raise CandidateJudgeContractError("no candidates available for judging")

        payload = judge_payload
        if payload is None:
            if judge_runner is None:
                raise CandidateJudgeContractError("judge_payload or judge_runner is required")
            payload = make_judge_runner(judge_runner)(example=example, candidates=normalized_candidates)

        result = score_judge_output(
            example=example,
            candidates=normalized_candidates,
            judge_payload=payload,
            max_candidates=max_candidates,
        )
        summary = result["judge_summary"]
        return {
            "status": "ok",
            "phase": "judge_scoring",
            "example_id": _require_non_empty_string(example, "id"),
            "direction": _require_direction(example),
            "candidate_count": summary["candidate_count"],
            "passes_threshold": summary["passes_threshold"],
            "selected_candidate": result["selected_candidate"],
            "rejected_candidates": result["rejected_candidates"],
            "raw_judge_output": summary.get("raw_judge_output"),
            "judge_summary": summary,
        }
    except Exception as exc:
        return render_safe_error_row(
            example=example,
            phase="judge_scoring",
            candidates=candidates,
            raw_judge_output=(judge_payload or {}).get("raw_judge_output") if isinstance(judge_payload, dict) else None,
            error=exc,
        )


def render_safe_error_row(
    *,
    example: dict[str, Any],
    phase: str,
    candidates: list[dict[str, Any]] | list[Candidate] | None,
    raw_judge_output: Any,
    error: Exception,
) -> dict[str, Any]:
    candidate_count = len(candidates) if isinstance(candidates, list) else 0
    return {
        "status": "error",
        "phase": phase,
        "example_id": example.get("id"),
        "direction": example.get("direction"),
        "candidate_count": candidate_count,
        "passes_threshold": False,
        "selected_candidate": None,
        "rejected_candidates": [],
        "raw_judge_output": raw_judge_output,
        "error": _safe_error_message(error),
    }


def _coerce_candidate(candidate: dict[str, Any] | Candidate, fallback_id: str | None = None) -> Candidate:
    if isinstance(candidate, Candidate):
        candidate_id = candidate.candidate_id
        prediction = candidate.prediction
        source = candidate.source
        prompt_variant = candidate.prompt_variant
        retrieval_rule_ids = candidate.retrieval_rule_ids
        retrieval_context = candidate.retrieval_context
        raw_candidate_output = candidate.raw_candidate_output
    elif isinstance(candidate, dict):
        candidate_id = str(candidate.get("candidate_id") or fallback_id or "").strip()
        prediction = str(candidate.get("prediction") or "").strip()
        source = str(candidate.get("source") or "unknown").strip()
        prompt_variant = str(candidate.get("prompt_variant") or "default").strip()
        retrieval_rule_ids = candidate.get("retrieval_rule_ids") or []
        retrieval_context = candidate.get("retrieval_context") or []
        raw_candidate_output = candidate.get("raw_candidate_output")
    else:
        raise CandidateJudgeContractError("candidate must be an object")

    if not candidate_id:
        raise CandidateJudgeContractError("candidate_id is required")
    if not prediction:
        raise CandidateJudgeContractError(f"candidate '{candidate_id}' prediction is required")
    if not isinstance(retrieval_rule_ids, list):
        raise CandidateJudgeContractError(f"candidate '{candidate_id}' retrieval_rule_ids must be a list")
    if not isinstance(retrieval_context, list):
        raise CandidateJudgeContractError(f"candidate '{candidate_id}' retrieval_context must be a list")

    return Candidate(
        candidate_id=candidate_id,
        prediction=prediction,
        source=source or "unknown",
        prompt_variant=prompt_variant or "default",
        retrieval_rule_ids=[str(item) for item in retrieval_rule_ids],
        retrieval_context=[str(item) for item in retrieval_context],
        raw_candidate_output=raw_candidate_output,
    )


def _normalize_criteria_scores(value: Any, direction: str) -> dict[str, float]:
    if not isinstance(value, dict) or not value:
        raise CandidateJudgeContractError("criteria_scores must be a non-empty object")
    normalized: dict[str, float] = {}
    for key, raw_score in value.items():
        score = _coerce_float(raw_score, f"criteria_scores.{key}")
        if not 0.0 <= score <= 1.0:
            raise CandidateJudgeContractError(f"criteria_scores.{key} must be between 0 and 1")
        normalized[str(key)] = score

    required_direction_key = "fluency" if direction == "en_to_mir" else "literalness"
    if "semantic_fidelity" not in normalized:
        raise CandidateJudgeContractError("criteria_scores.semantic_fidelity is required")
    if required_direction_key not in normalized:
        raise CandidateJudgeContractError(f"criteria_scores.{required_direction_key} is required for {direction}")
    return normalized


def _require_numeric(payload: dict[str, Any], field_name: str) -> float:
    if field_name not in payload:
        raise CandidateJudgeContractError(f"{field_name} is required")
    return _coerce_float(payload[field_name], field_name)


def _coerce_float(value: Any, field_name: str) -> float:
    if isinstance(value, bool):
        raise CandidateJudgeContractError(f"{field_name} must be numeric")
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise CandidateJudgeContractError(f"{field_name} must be numeric") from exc


def _require_non_empty_string(payload: dict[str, Any], field_name: str) -> str:
    value = payload.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise CandidateJudgeContractError(f"{field_name} is required")
    return value.strip()


def _require_direction(example: dict[str, Any]) -> str:
    direction = _require_non_empty_string(example, "direction")
    if direction not in ALLOWED_DIRECTIONS:
        raise CandidateJudgeContractError(f"unknown direction '{direction}'")
    return direction


def _safe_error_message(error: Exception) -> str:
    message = str(error).strip() or error.__class__.__name__
    message = message.replace("Traceback", "")
    return " ".join(message.split())
