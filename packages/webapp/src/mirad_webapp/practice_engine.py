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
_ID_RE = re.compile(r"[^a-z0-9]+")

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
    *, cards: list[dict[str, Any]], events: list[dict[str, Any]] | None, now: datetime | None = None, limit: int = 10
) -> dict[str, Any]:
    """Return a bounded, diagnostic practice queue without mutating session state."""
    current = _as_aware_datetime(now)
    practice_items = _expand_practice_items(cards)
    valid_events = _normalize_events(events or [])
    stats = _stats_by_card(valid_events)
    recent_accuracy = _recent_accuracy(valid_events)
    weak_recent = recent_accuracy is not None and recent_accuracy < _NEW_ITEM_ACCURACY_THRESHOLD

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
    bounded_limit = max(0, min(int(limit), len(ordered)))
    return {
        "ok": True,
        "phase": "practice_queue",
        "card_count": len(practice_items),
        "base_card_count": len(_normalize_base_cards(cards)),
        "event_count": len(valid_events),
        "limit": bounded_limit,
        "cards": ordered[:bounded_limit],
    }


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
    is_correct = bool(correct) if correct is not None else _normalize_text(submitted) == _normalize_text(expected)
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


def _resolve_practice_item_id(card_id: str, items_by_id: dict[str, dict[str, Any]], legacy_aliases: dict[str, str]) -> str | None:
    normalized = str(card_id or "").strip()
    if normalized in items_by_id:
        return normalized
    return legacy_aliases.get(normalized)


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


def _normalize_text(value: Any) -> str:
    return " ".join(str(value).casefold().split())


def _as_aware_datetime(value: datetime | None) -> datetime:
    result = value or datetime.now(timezone.utc)
    return result if result.tzinfo else result.replace(tzinfo=timezone.utc)


def _parse_datetime(value: Any) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
