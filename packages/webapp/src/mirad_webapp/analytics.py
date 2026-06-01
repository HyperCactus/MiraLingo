from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def build_practice_analytics(
    cards: list[dict[str, Any]],
    events: list[dict[str, Any]],
    sessions: list[dict[str, Any]],
    lifecycle_rows: list[dict[str, Any]],
    shown_cards: list[dict[str, Any]] | None = None,
    now: datetime | None = None,
    filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    valid_events = [e for e in events if _parse_iso(str(e.get("answered_at") or "")) is not None]

    total = len(valid_events)
    correct = sum(1 for e in valid_events if bool(e.get("correct")))
    incorrect = total - correct
    accuracy = round(correct / total, 4) if total else None

    per_type: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "correct": 0, "incorrect": 0})
    direction_breakdown: dict[str, dict[str, int]] = defaultdict(lambda: {"attempts": 0, "correct": 0, "incorrect": 0})
    card_type_breakdown: dict[str, dict[str, int]] = defaultdict(lambda: {"attempts": 0, "correct": 0, "incorrect": 0})
    per_card: dict[str, dict[str, Any]] = {}

    latest_event = None
    latest_ts = None
    first_ts = None
    streak_days: set[str] = set()

    for event in valid_events:
        ts = _parse_iso(str(event.get("answered_at")))
        if ts is None:
            continue
        first_ts = ts if first_ts is None else min(first_ts, ts)
        if latest_ts is None or ts > latest_ts:
            latest_ts = ts
            latest_event = {
                "card_id": event.get("card_id"),
                "base_card_id": event.get("base_card_id"),
                "direction": event.get("direction"),
                "card_type": event.get("card_type"),
                "correct": bool(event.get("correct")),
                "answered_at": event.get("answered_at"),
            }

        day = ts.date().isoformat()
        streak_days.add(day)

        t = str(event.get("card_type") or "unknown")
        d = str(event.get("direction") or "unknown")
        per_type[t]["total"] += 1
        per_type[t]["correct"] += int(bool(event.get("correct")))
        per_type[t]["incorrect"] += int(not bool(event.get("correct")))

        direction_breakdown[d]["attempts"] += 1
        direction_breakdown[d]["correct"] += int(bool(event.get("correct")))
        direction_breakdown[d]["incorrect"] += int(not bool(event.get("correct")))

        card_type_breakdown[t]["attempts"] += 1
        card_type_breakdown[t]["correct"] += int(bool(event.get("correct")))
        card_type_breakdown[t]["incorrect"] += int(not bool(event.get("correct")))

        key = str(event.get("card_id") or f"{event.get('base_card_id')}#{str(event.get('direction') or '').replace('_', '-')}")
        row = per_card.setdefault(
            key,
            {
                "card_id": key,
                "base_card_id": event.get("base_card_id"),
                "direction": event.get("direction"),
                "card_type": event.get("card_type"),
                "attempts": 0,
                "correct": 0,
                "incorrect": 0,
                "last_answered_at": None,
            },
        )
        row["attempts"] += 1
        row["correct"] += int(bool(event.get("correct")))
        row["incorrect"] += int(not bool(event.get("correct")))
        if row["last_answered_at"] is None or ts > _parse_iso(str(row["last_answered_at"])):
            row["last_answered_at"] = event.get("answered_at")

    lifecycle_count = len(lifecycle_rows)
    session_count = len(sessions)

    streak = {
        "current_days": 1 if latest_ts and latest_ts.date().isoformat() in streak_days else 0,
        "best_days": len(streak_days),
        "trajectory": sorted(streak_days),
    }

    sparse = {
        "is_sparse": total == 0 and session_count == 0 and lifecycle_count == 0,
        "events": total,
        "sessions": session_count,
        "lifecycles": lifecycle_count,
        "reason": "new_learner" if total == 0 and session_count == 0 and lifecycle_count == 0 else "established",
    }

    return {
        "ok": True,
        "phase": "practice_analytics",
        "event_count": total,
        "session_count": session_count,
        "lifecycle_count": lifecycle_count,
        "total": total,
        "correct": correct,
        "incorrect": incorrect,
        "accuracy": accuracy,
        "per_type": dict(per_type),
        "latest_event": latest_event,
        "sparse_history": sparse,
        "sessions": {"count": session_count, "items": sessions},
        "timing": {
            "first_answered_at": first_ts.isoformat() if first_ts else None,
            "last_answered_at": latest_ts.isoformat() if latest_ts else None,
        },
        "streak": streak,
        "direction_breakdown": dict(direction_breakdown),
        "card_type_breakdown": dict(card_type_breakdown),
        "lifecycle": {"count": lifecycle_count, "active": sum(1 for r in lifecycle_rows if r.get("lifecycle") == "active"), "revision": sum(1 for r in lifecycle_rows if r.get("lifecycle") == "revision")},
        "per_card": per_card,
        "filters": filters or {},
        "shown_card_count": len(shown_cards or []),
    }
