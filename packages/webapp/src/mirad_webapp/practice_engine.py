"""Deterministic adaptive practice scheduler and session persistence helpers."""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

MAX_EVENTS = 200
STALE_AFTER_SECONDS = 14 * 24 * 60 * 60
_WEAK_ACCURACY_THRESHOLD = 0.8
_NEW_ITEM_ACCURACY_THRESHOLD = 0.6
_REPEAT_GAP = 10
_ID_RE = re.compile(r"[^a-z0-9]+")

MIXED_MODE = "mixed"
REVISION_MODE = "revision"
BUILD_VOCABULARY_MODE = "build_vocabulary"
_VALID_QUEUE_MODES = {MIXED_MODE, REVISION_MODE, BUILD_VOCABULARY_MODE}

ENGLISH_TO_MIRAD = "english_to_mirad"
MIRAD_TO_ENGLISH = "mirad_to_english"
_DIRECTION_SUFFIXES = {
    ENGLISH_TO_MIRAD: "english-to-mirad",
    MIRAD_TO_ENGLISH: "mirad-to-english",
}
_SUFFIX_TO_DIRECTION = {suffix: direction for direction, suffix in _DIRECTION_SUFFIXES.items()}


def stable_card_id(card: dict[str, Any]) -> str:
    """Derive a stable base id from card type and normalized English content."""
    card_type = str(card.get("type") or "card").strip().casefold() or "card"
    english = _normalize_text(card.get("english") or card.get("prompt") or "")
    slug = _ID_RE.sub("-", english).strip("-") or "untitled"
    return f"{card_type}:{slug}"


def direction_item_id(base_card_id: str, direction: str) -> str:
    """Return the deterministic direction-aware practice item id."""
    return f"{base_card_id}#{_DIRECTION_SUFFIXES[direction]}"


def build_practice_queue(
    *,
    cards: list[dict[str, Any]],
    events: list[dict[str, Any]] | None,
    now: datetime | None = None,
    limit: int = 10,
    mode: str = MIXED_MODE,
) -> dict[str, Any]:
    """Return a bounded, diagnostic practice queue without mutating session state."""
    normalized_mode = _normalize_queue_mode(mode)
    if normalized_mode is None:
        return _invalid_queue_mode_result(mode)

    current = _as_aware_datetime(now)
    base_cards = _normalize_base_cards(cards)
    practice_items = _expand_practice_items(cards)
    valid_events = _normalize_events(events or [])
    stats = _stats_by_card(valid_events)
    recent_accuracy = _recent_accuracy(valid_events)
    weak_recent = recent_accuracy is not None and recent_accuracy < _NEW_ITEM_ACCURACY_THRESHOLD
    base_cards_with_history = {event["base_card_id"] for event in valid_events}

    ranked: list[tuple[int, int, dict[str, Any]]] = []
    for index, item in enumerate(practice_items):
        card_stats = stats.get(item["id"], _empty_stats())
        reason = _scheduler_reason(card_stats, current, weak_recent)
        queue_item = {
            **item,
            "scheduler_reason": reason,
            "mastery": _mastery_payload(card_stats),
            "recency": _recency_payload(card_stats, current),
        }
        ranked.append((_rank(reason, card_stats, current), index, queue_item))

    ordered = _interleave_same_priority_cards(ranked)
    filtered, mode_detail = _filter_queue_for_mode(ordered, normalized_mode, base_cards_with_history)
    diversified = _diversify_mixed_queue(filtered, normalized_mode)
    spaced, repeat_gap_satisfied = _apply_repeat_gap(diversified, repeat_gap=_REPEAT_GAP)
    bounded_limit = max(0, min(int(limit), len(spaced)))
    if not spaced and not filtered:
        repeat_gap_satisfied = False
        mode_detail = "empty_pool"

    result = {
        "ok": True,
        "phase": "practice_queue",
        "mode": normalized_mode,
        "mode_detail": mode_detail,
        "repeat_gap": _REPEAT_GAP,
        "repeat_gap_satisfied": repeat_gap_satisfied,
        "card_count": len(practice_items),
        "base_card_count": len(base_cards),
        "event_count": len(valid_events),
        "limit": bounded_limit,
        "cards": spaced[:bounded_limit],
    }

    if normalized_mode == MIXED_MODE and (practice_items or valid_events):
        result["diagnostics"] = _build_mixed_mode_diagnostics(
            selected_cards=spaced[:bounded_limit],
            all_items=practice_items,
            stats=stats,
            repeat_gap_satisfied=repeat_gap_satisfied,
        )

    return result


def record_practice_answer(
    *,
    cards: list[dict[str, Any]],
    events: list[dict[str, Any]] | None,
    card_id: str,
    submitted_answer: str = "",
    correct: bool | None = None,
    now: datetime | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Validate and append a JSON-serializable practice event, or return a structured error."""
    current = _as_aware_datetime(now)
    valid_events = _normalize_events(events or [])
    items_by_id, legacy_aliases = _practice_item_maps(cards)
    resolved_id = _resolve_practice_item_id(card_id, items_by_id, legacy_aliases)
    if resolved_id is None:
        return {
            "ok": False,
            "error": "unknown_card",
            "phase": "practice_answer",
            "card_id": card_id,
            "event_count": len(valid_events),
            "detail": "Practice card was not found in the configured content source.",
        }

    item = items_by_id[resolved_id]
    submitted = str(submitted_answer).strip()
    expected = item["answer"]
    expected_alternatives = _normalize_answer_alternatives(expected)
    normalized_submitted = _normalize_text(submitted)
    is_correct = bool(correct) if correct is not None else normalized_submitted in expected_alternatives
    event = {
        "card_id": item["id"],
        "base_card_id": item["base_card_id"],
        "direction": item["direction"],
        "card_type": item["type"],
        "submitted_answer": submitted,
        "expected_answer": expected,
        "correct": is_correct,
        "answered_at": current.isoformat(),
    }
    return (valid_events + [event])[-MAX_EVENTS:]


def answer_summary(cards: list[dict[str, Any]], events: list[dict[str, Any]], card_id: str, now: datetime | None = None) -> dict[str, Any]:
    """Return API-facing diagnostics for the latest answer."""
    items_by_id, legacy_aliases = _practice_item_maps(cards)
    resolved_id = _resolve_practice_item_id(card_id, items_by_id, legacy_aliases) or str(card_id)
    queue = build_practice_queue(cards=cards, events=events, now=now, limit=len(items_by_id))
    selected = next((card for card in queue["cards"] if card["id"] == resolved_id), None) or {}
    latest = next((event for event in reversed(_normalize_events(events)) if event["card_id"] == resolved_id), {})
    latest_summary = _latest_event_summary(latest)
    return {
        "ok": True,
        "phase": "practice_answer",
        "card_id": resolved_id,
        "base_card_id": latest.get("base_card_id") or selected.get("base_card_id"),
        "direction": latest.get("direction") or selected.get("direction"),
        "card_type": latest.get("card_type") or selected.get("type"),
        "correct": latest.get("correct"),
        "event_count": queue["event_count"],
        "scheduler_reason": selected.get("scheduler_reason"),
        "mastery": selected.get("mastery"),
        "recency": selected.get("recency"),
        "latest_event": latest_summary,
    }


def build_practice_progress(
    *, cards: list[dict[str, Any]], events: list[dict[str, Any]] | None, now: datetime | None = None
) -> dict[str, Any]:
    """Aggregate bounded session practice events into API-facing progress diagnostics."""
    current = _as_aware_datetime(now)
    practice_items = _expand_practice_items(cards)
    valid_events = _normalize_events(events or [])
    stats = _stats_by_card(valid_events)
    recent_accuracy = _recent_accuracy(valid_events)
    weak_recent = recent_accuracy is not None and recent_accuracy < _NEW_ITEM_ACCURACY_THRESHOLD

    by_type = {"word": _empty_type_stats(), "phrase": _empty_type_stats()}
    by_direction = {ENGLISH_TO_MIRAD: _empty_type_stats(), MIRAD_TO_ENGLISH: _empty_type_stats()}
    for event in valid_events:
        card_type = event["card_type"] if event["card_type"] in by_type else "other"
        by_type.setdefault(card_type, _empty_type_stats())
        _increment_type_stats(by_type[card_type], event["correct"])
        direction = event.get("direction") if event.get("direction") in by_direction else "unknown"
        by_direction.setdefault(direction, _empty_type_stats())
        _increment_type_stats(by_direction[direction], event["correct"])

    per_card: list[dict[str, Any]] = []
    states: dict[str, list[str]] = {"weak": [], "mastered": [], "stale": [], "new": []}
    for item in practice_items:
        card_stats = stats.get(item["id"], _empty_stats())
        reason = _scheduler_reason(card_stats, current, weak_recent)
        state = _progress_state(reason)
        states[state].append(item["id"])
        per_card.append(
            {
                **item,
                "attempts": card_stats["attempts"],
                "correct": card_stats["correct"],
                "incorrect": card_stats["incorrect"],
                "accuracy": None if card_stats["attempts"] == 0 else card_stats["correct"] / card_stats["attempts"],
                "scheduler_reason": reason,
                "mastery": _mastery_payload(card_stats),
                "recency": _recency_payload(card_stats, current),
                "state": state,
            }
        )

    correct = sum(1 for event in valid_events if event["correct"])
    incorrect = len(valid_events) - correct
    latest = valid_events[-1] if valid_events else {}
    return {
        "ok": True,
        "phase": "practice_progress",
        "card_count": len(practice_items),
        "base_card_count": len(_normalize_base_cards(cards)),
        "event_count": len(valid_events),
        "total": len(valid_events),
        "correct": correct,
        "incorrect": incorrect,
        "accuracy": None if not valid_events else correct / len(valid_events),
        "per_type": {card_type: _finalize_type_stats(type_stats) for card_type, type_stats in by_type.items()},
        "per_direction": {direction: _finalize_type_stats(type_stats) for direction, type_stats in by_direction.items()},
        "per_card": per_card,
        "latest_event": _latest_event_summary(latest),
        "weak_count": len(states["weak"]),
        "mastered_count": len(states["mastered"]),
        "stale_count": len(states["stale"]),
        "new_count": len(states["new"]),
        "weak_cards": states["weak"],
        "mastered_cards": states["mastered"],
        "stale_cards": states["stale"],
        "new_cards": states["new"],
    }


def _expand_practice_items(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for card in _normalize_base_cards(cards):
        items.append(_practice_item(card, ENGLISH_TO_MIRAD))
        items.append(_practice_item(card, MIRAD_TO_ENGLISH))
    return items


def _practice_item(card: dict[str, str], direction: str) -> dict[str, str]:
    if direction == ENGLISH_TO_MIRAD:
        prompt_language = "english"
        answer_language = "mirad"
        prompt = card["english"]
        answer = card["mirad"]
    else:
        prompt_language = "mirad"
        answer_language = "english"
        prompt = card["mirad"]
        answer = card["english"]

    return {
        "id": direction_item_id(card["id"], direction),
        "base_card_id": card["id"],
        "audio_card_id": card["id"],
        "type": card["type"],
        "direction": direction,
        "prompt_language": prompt_language,
        "answer_language": answer_language,
        "prompt": prompt,
        "answer": answer,
        "english_text": card["english"],
        "mirad_text": card["mirad"],
    }


def _practice_item_maps(cards: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    items = _expand_practice_items(cards)
    by_id = {item["id"]: item for item in items}
    legacy_aliases = {item["base_card_id"]: item["id"] for item in items if item["direction"] == ENGLISH_TO_MIRAD}
    return by_id, legacy_aliases


def _normalize_queue_mode(mode: Any) -> str | None:
    normalized = str(mode or MIXED_MODE).strip().casefold()
    return normalized if normalized in _VALID_QUEUE_MODES else None


def _invalid_queue_mode_result(mode: Any) -> dict[str, Any]:
    return {
        "ok": False,
        "phase": "practice_queue",
        "error": "invalid_mode",
        "mode": str(mode or ""),
        "allowed_modes": sorted(_VALID_QUEUE_MODES),
        "detail": "Practice mode must be one of mixed, revision, or build_vocabulary.",
    }


def _filter_queue_for_mode(
    ordered: list[dict[str, Any]], mode: str, base_cards_with_history: set[str]
) -> tuple[list[dict[str, Any]], str]:
    if mode == REVISION_MODE:
        return [item for item in ordered if item["scheduler_reason"] == "stale_mastered_review"], "stale_only"
    if mode == BUILD_VOCABULARY_MODE:
        return [
            {
                **item,
                "scheduler_reason": "new_item" if item["scheduler_reason"] == "new_item_gated_by_weak_recent_performance" else item["scheduler_reason"],
            }
            for item in ordered
            if item["type"] == "word"
            and item["base_card_id"] not in base_cards_with_history
            and item["scheduler_reason"] in {"new_item", "new_item_gated_by_weak_recent_performance"}
        ], "new_words_only"
    return _prioritize_intro_content(ordered, base_cards_with_history), "default_mixed"


def _resolve_practice_item_id(card_id: str, items_by_id: dict[str, dict[str, Any]], legacy_aliases: dict[str, str]) -> str | None:
    normalized = str(card_id or "").strip()
    if normalized in items_by_id:
        return normalized
    return legacy_aliases.get(normalized)


def _prioritize_intro_content(ordered: list[dict[str, Any]], base_cards_with_history: set[str]) -> list[dict[str, Any]]:
    """Bias early mixed-mode cards toward onboarding phrases for new learners."""
    if not ordered:
        return ordered
    if base_cards_with_history:
        return ordered

    unseen = [item for item in ordered if item["base_card_id"] not in base_cards_with_history]
    seen = [item for item in ordered if item["base_card_id"] in base_cards_with_history]

    # Starter phrase: "my name is ..." should appear early for brand-new users.
    starter = [
        item for item in unseen
        if item["type"] == "phrase"
        and item["direction"] == ENGLISH_TO_MIRAD
        and str(item.get("english_text") or "").strip().casefold().startswith("my name is")
    ]
    starter_ids = {item["id"] for item in starter}

    remaining_unseen = [item for item in unseen if item["id"] not in starter_ids]
    phrase_unseen = [item for item in remaining_unseen if item["type"] == "phrase"]
    word_unseen = [item for item in remaining_unseen if item["type"] == "word"]

    prefix: list[dict[str, Any]] = []
    if starter:
        prefix.extend(starter[:1])

    # Keep first impression mixed: alternate phrase/word for initial run.
    while len(prefix) < 12 and (phrase_unseen or word_unseen):
        if phrase_unseen:
            prefix.append(phrase_unseen.pop(0))
        if len(prefix) >= 12:
            break
        if word_unseen:
            prefix.append(word_unseen.pop(0))

    used_ids = {item["id"] for item in prefix}
    tail = [item for item in ordered if item["id"] not in used_ids]
    return prefix + tail


def _diversify_mixed_queue(items: list[dict[str, Any]], mode: str) -> list[dict[str, Any]]:
    """Keep mixed mode adaptive without displacing high-priority weak/review items."""
    if mode != MIXED_MODE or not items:
        return items

    weak = [item for item in items if item.get("scheduler_reason") == "weak_recent_performance"]
    non_weak = [item for item in items if item.get("scheduler_reason") != "weak_recent_performance"]

    weak_cap = max(6, int(len(items) * 0.6))
    return weak[:weak_cap] + non_weak


def _interleave_same_priority_cards(ranked: list[tuple[int, int, dict[str, Any]]]) -> list[dict[str, Any]]:
    """Order scheduler ranks while mixing card types and directions within equal-priority buckets."""
    by_rank: dict[int, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    for rank, index, item in ranked:
        by_rank[rank].append((index, item))

    ordered: list[dict[str, Any]] = []
    for rank in sorted(by_rank):
        by_group: dict[tuple[str, str], list[tuple[int, dict[str, Any]]]] = defaultdict(list)
        group_order: list[tuple[str, str]] = []
        for index, item in sorted(by_rank[rank], key=lambda row: row[0]):
            group = (item["type"], item["direction"])
            if group not in by_group:
                group_order.append(group)
            by_group[group].append((index, item))

        while any(by_group.values()):
            for group in group_order:
                if by_group[group]:
                    ordered.append(by_group[group].pop(0)[1])
    return ordered


def _build_mixed_mode_diagnostics(
    *,
    selected_cards: list[dict[str, Any]],
    all_items: list[dict[str, Any]],
    stats: dict[str, dict[str, Any]],
    repeat_gap_satisfied: bool,
) -> dict[str, Any]:
    requested_active_revision_ratio = {"active": 0.7, "revision": 0.3}
    requested_word_phrase_mix = {"word": 0.5, "phrase": 0.5}

    active_count = sum(1 for card in selected_cards if card.get("scheduler_reason") in {"new_item", "new_item_gated_by_weak_recent_performance", "weak_recent_performance"})
    revision_count = max(0, len(selected_cards) - active_count)
    total = len(selected_cards) or 1

    word_count = sum(1 for card in selected_cards if card.get("type") == "word")
    phrase_count = sum(1 for card in selected_cards if card.get("type") == "phrase")

    per_card_weights: dict[str, dict[str, float]] = {}
    max_attempts = max((stats.get(item["id"], _empty_stats())["attempts"] for item in all_items), default=0)
    for item in all_items:
        item_stats = stats.get(item["id"], _empty_stats())
        attempts = item_stats["attempts"]
        accuracy = 1.0 if attempts == 0 else (item_stats["correct"] / attempts)
        exposure_factor = 1.0 + max(0.0, (max_attempts - attempts) / max(1, max_attempts or 1))
        recent_performance_factor = 1.0 + max(0.0, 1.0 - accuracy)
        per_card_weights[item["id"]] = {
            "exposure_factor": exposure_factor,
            "recent_performance_factor": recent_performance_factor,
        }

    unique_bases = len({item.get("base_card_id") for item in all_items})
    fallback_reasons: list[str] = []
    if unique_bases <= _REPEAT_GAP:
        fallback_reasons.append("small_pool")
    actual_active = active_count / total
    actual_revision = revision_count / total
    actual_word = word_count / total
    actual_phrase = phrase_count / total
    if abs(actual_active - requested_active_revision_ratio["active"]) > 0.2:
        fallback_reasons.append("ratio_drift")
    if abs(actual_word - requested_word_phrase_mix["word"]) > 0.2:
        fallback_reasons.append("mix_drift")

    return {
        "requested_active_revision_ratio": requested_active_revision_ratio,
        "actual_active_revision_ratio": {"active": actual_active, "revision": actual_revision},
        "requested_word_phrase_mix": requested_word_phrase_mix,
        "actual_word_phrase_mix": {"word": actual_word, "phrase": actual_phrase},
        "weighting_inputs": {"exposure_weight": 0.5, "recent_performance_weight": 0.5},
        "per_card_weights": per_card_weights,
        "repeat_gap": _REPEAT_GAP,
        "repeat_gap_satisfied": repeat_gap_satisfied,
        "repeat_gap_relaxed": not repeat_gap_satisfied,
        "fallback_reasons": fallback_reasons,
    }


def _apply_repeat_gap(items: list[dict[str, Any]], *, repeat_gap: int) -> tuple[list[dict[str, Any]], bool]:
    if not items:
        return [], False

    pending = list(items)
    scheduled: list[dict[str, Any]] = []
    recent_base_ids: list[str] = []
    repeat_gap_satisfied = True

    while pending:
        blocked_bases = set(recent_base_ids[-repeat_gap:])
        candidate_index = next((index for index, item in enumerate(pending) if item["base_card_id"] not in blocked_bases), None)
        if candidate_index is None:
            repeat_gap_satisfied = False
            candidate_index = 0
        chosen = pending.pop(candidate_index)
        scheduled.append(chosen)
        recent_base_ids.append(chosen["base_card_id"])

    if len({item["base_card_id"] for item in items}) <= repeat_gap:
        repeat_gap_satisfied = False

    return scheduled, repeat_gap_satisfied


def _empty_type_stats() -> dict[str, Any]:
    return {"attempts": 0, "correct": 0, "incorrect": 0, "accuracy": None}


def _increment_type_stats(stats: dict[str, Any], correct: bool) -> None:
    stats["attempts"] += 1
    stats["correct"] += 1 if correct else 0
    stats["incorrect"] += 0 if correct else 1


def _finalize_type_stats(stats: dict[str, Any]) -> dict[str, Any]:
    attempts = stats["attempts"]
    return {
        "attempts": attempts,
        "correct": stats["correct"],
        "incorrect": stats["incorrect"],
        "accuracy": None if attempts == 0 else stats["correct"] / attempts,
    }


def _latest_event_summary(event: dict[str, Any]) -> dict[str, Any] | None:
    if not event:
        return None
    return {
        "card_id": event.get("card_id"),
        "base_card_id": event.get("base_card_id"),
        "direction": event.get("direction"),
        "card_type": event.get("card_type"),
        "correct": event.get("correct"),
        "answered_at": event.get("answered_at"),
    }


def _progress_state(reason: str) -> str:
    if reason == "weak_recent_performance":
        return "weak"
    if reason == "stale_mastered_review":
        return "stale"
    if reason == "mastered_recent":
        return "mastered"
    return "new"


def _normalize_base_cards(cards: list[dict[str, Any]]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for card in cards:
        typed = _normalize_card(card)
        if not typed["english"] or not typed["mirad"]:
            continue
        normalized.append(typed)
    return normalized


def _normalize_card(card: dict[str, Any]) -> dict[str, str]:
    typed = {"type": str(card.get("type") or "card"), "english": str(card.get("english") or "").strip(), "mirad": str(card.get("mirad") or "").strip()}
    typed["id"] = str(card.get("id") or stable_card_id(typed))
    return typed


def _normalize_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for event in events[-MAX_EVENTS:]:
        if not isinstance(event, dict) or not event.get("card_id") or "correct" not in event:
            continue
        answered_at = _parse_datetime(event.get("answered_at"))
        if answered_at is None:
            continue
        raw_card_id = str(event["card_id"])
        direction = _normalize_direction(event.get("direction"), raw_card_id)
        base_card_id = str(event.get("base_card_id") or _base_card_id_from_event(raw_card_id))
        card_id = raw_card_id if "#" in raw_card_id else direction_item_id(base_card_id, direction)
        normalized.append({
            "card_id": card_id,
            "base_card_id": base_card_id,
            "direction": direction,
            "card_type": str(event.get("card_type") or "card"),
            "submitted_answer": str(event.get("submitted_answer") or ""),
            "expected_answer": str(event.get("expected_answer") or ""),
            "correct": bool(event.get("correct")),
            "answered_at": answered_at.isoformat(),
        })
    return normalized


def _normalize_direction(value: Any, card_id: str) -> str:
    raw = str(value or "").strip()
    if raw in _DIRECTION_SUFFIXES:
        return raw
    if "#" in card_id:
        suffix = card_id.rsplit("#", maxsplit=1)[1]
        return _SUFFIX_TO_DIRECTION.get(suffix, ENGLISH_TO_MIRAD)
    return ENGLISH_TO_MIRAD


def _base_card_id_from_event(card_id: str) -> str:
    return card_id.split("#", maxsplit=1)[0]


def _stats_by_card(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    stats = defaultdict(_empty_stats)
    for event in events:
        stat = stats[event["card_id"]]
        stat["attempts"] += 1
        stat["correct"] += 1 if event["correct"] else 0
        stat["incorrect"] += 0 if event["correct"] else 1
        stat["last_seen_at"] = event["answered_at"]
    return dict(stats)


def _empty_stats() -> dict[str, Any]:
    return {"attempts": 0, "correct": 0, "incorrect": 0, "last_seen_at": None}


def _mastery_payload(stat: dict[str, Any]) -> dict[str, Any]:
    attempts = stat["attempts"]
    return {"attempts": attempts, "correct": stat["correct"], "incorrect": stat["incorrect"], "accuracy": None if attempts == 0 else stat["correct"] / attempts}


def _recency_payload(stat: dict[str, Any], now: datetime) -> dict[str, Any]:
    if not stat.get("last_seen_at"):
        return {"last_seen_at": None, "age_seconds": None}
    seen = _parse_datetime(stat["last_seen_at"])
    return {"last_seen_at": seen.isoformat(), "age_seconds": int((now - seen).total_seconds())}


def _scheduler_reason(stat: dict[str, Any], now: datetime, weak_recent: bool) -> str:
    attempts = stat["attempts"]
    if attempts == 0:
        return "new_item_gated_by_weak_recent_performance" if weak_recent else "new_item"
    accuracy = stat["correct"] / attempts
    if stat["incorrect"] > 0 or accuracy < _WEAK_ACCURACY_THRESHOLD:
        return "weak_recent_performance"
    seen = _parse_datetime(stat["last_seen_at"])
    if seen and int((now - seen).total_seconds()) >= STALE_AFTER_SECONDS:
        return "stale_mastered_review"
    return "mastered_recent"


def _rank(reason: str, stat: dict[str, Any], now: datetime) -> int:
    order = {"weak_recent_performance": 0, "stale_mastered_review": 1, "new_item": 2, "new_item_gated_by_weak_recent_performance": 3, "mastered_recent": 4}
    return order.get(reason, 9)


def _recent_accuracy(events: list[dict[str, Any]]) -> float | None:
    if not events:
        return None
    recent = events[-5:]
    return sum(1 for event in recent if event["correct"]) / len(recent)


def _normalize_answer_alternatives(value: Any) -> set[str]:
    normalized = {_normalize_text(part) for part in str(value).split(",")}
    return {part for part in normalized if part}


def _normalize_text(value: Any) -> str:
    text = str(value).casefold()
    text = re.sub(r"[^\w\s']", " ", text)
    return " ".join(text.split())


def _as_aware_datetime(value: datetime | None) -> datetime:
    result = value or datetime.now(timezone.utc)
    return result if result.tzinfo else result.replace(tzinfo=timezone.utc)


def _parse_datetime(value: Any) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
