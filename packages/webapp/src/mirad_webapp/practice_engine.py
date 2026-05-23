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


def stable_card_id(card: dict[str, Any]) -> str:
    """Derive a stable id from card type and normalized English content."""
    card_type = str(card.get("type") or "card").strip().casefold() or "card"
    english = _normalize_text(card.get("english") or card.get("prompt") or "")
    slug = _ID_RE.sub("-", english).strip("-") or "untitled"
    return f"{card_type}:{slug}"


def build_practice_queue(
    *, cards: list[dict[str, Any]], events: list[dict[str, Any]] | None, now: datetime | None = None, limit: int = 10
) -> dict[str, Any]:
    """Return a bounded, diagnostic practice queue without mutating session state."""
    current = _as_aware_datetime(now)
    normalized_cards = [_normalize_card(card) for card in cards]
    valid_events = _normalize_events(events or [])
    stats = _stats_by_card(valid_events)
    recent_accuracy = _recent_accuracy(valid_events)
    weak_recent = recent_accuracy is not None and recent_accuracy < _NEW_ITEM_ACCURACY_THRESHOLD

    ranked: list[tuple[int, str, dict[str, Any]]] = []
    for index, card in enumerate(normalized_cards):
        card_stats = stats.get(card["id"], _empty_stats())
        reason = _scheduler_reason(card_stats, current, weak_recent)
        item = {
            "id": card["id"],
            "type": card["type"],
            "prompt": card["english"],
            "answer": card["mirad"],
            "scheduler_reason": reason,
            "mastery": _mastery_payload(card_stats),
            "recency": _recency_payload(card_stats, current),
        }
        ranked.append((_rank(reason, card_stats, current), f"{index:06d}:{card['id']}", item))

    ranked.sort(key=lambda row: (row[0], row[1]))
    bounded_limit = max(0, min(int(limit), len(ranked)))
    return {
        "ok": True,
        "phase": "practice_queue",
        "card_count": len(normalized_cards),
        "event_count": len(valid_events),
        "limit": bounded_limit,
        "cards": [row[2] for row in ranked[:bounded_limit]],
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
    cards_by_id = {_normalize_card(card)["id"]: _normalize_card(card) for card in cards}
    if card_id not in cards_by_id:
        return {
            "ok": False,
            "error": "unknown_card",
            "phase": "practice_answer",
            "card_id": card_id,
            "event_count": len(valid_events),
            "detail": "Practice card was not found in the configured content source.",
        }

    card = cards_by_id[card_id]
    submitted = str(submitted_answer).strip()
    expected = card["mirad"]
    is_correct = bool(correct) if correct is not None else _normalize_text(submitted) == _normalize_text(expected)
    event = {
        "card_id": card["id"],
        "card_type": card["type"],
        "submitted_answer": submitted,
        "expected_answer": expected,
        "correct": is_correct,
        "answered_at": current.isoformat(),
    }
    return (valid_events + [event])[-MAX_EVENTS:]


def answer_summary(cards: list[dict[str, Any]], events: list[dict[str, Any]], card_id: str, now: datetime | None = None) -> dict[str, Any]:
    """Return API-facing diagnostics for the latest answer."""
    queue = build_practice_queue(cards=cards, events=events, now=now, limit=len(cards))
    selected = next((card for card in queue["cards"] if card["id"] == card_id), None) or {}
    latest = next((event for event in reversed(_normalize_events(events)) if event["card_id"] == card_id), {})
    latest_summary = {
        "card_id": latest.get("card_id"),
        "card_type": latest.get("card_type"),
        "correct": latest.get("correct"),
        "answered_at": latest.get("answered_at"),
    }
    return {
        "ok": True,
        "phase": "practice_answer",
        "card_id": card_id,
        "card_type": latest.get("card_type"),
        "correct": latest.get("correct"),
        "event_count": queue["event_count"],
        "scheduler_reason": selected.get("scheduler_reason"),
        "mastery": selected.get("mastery"),
        "recency": selected.get("recency"),
        "latest_event": latest_summary,
    }


def _normalize_card(card: dict[str, Any]) -> dict[str, str]:
    typed = {"type": str(card.get("type") or "card"), "english": str(card.get("english") or ""), "mirad": str(card.get("mirad") or "")}
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
        normalized.append({
            "card_id": str(event["card_id"]),
            "card_type": str(event.get("card_type") or "card"),
            "submitted_answer": str(event.get("submitted_answer") or ""),
            "expected_answer": str(event.get("expected_answer") or ""),
            "correct": bool(event.get("correct")),
            "answered_at": answered_at.isoformat(),
        })
    return normalized


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
