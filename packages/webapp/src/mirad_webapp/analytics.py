from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from .practice_engine import MASTERY_ACCURACY_THRESHOLD


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def _day_streak(days: set[str], now: datetime) -> dict[str, Any]:
    parsed = set()
    for value in days:
        try:
            parsed.add(datetime.fromisoformat(str(value)[:10]).date())
        except Exception:
            continue
    if not parsed:
        return {"current_days": 0, "best_days": 0, "trajectory": []}

    today = now.date()
    latest_allowed = today if today in parsed else today - timedelta(days=1)
    current_days = 0
    cursor = latest_allowed
    while cursor in parsed:
        current_days += 1
        cursor -= timedelta(days=1)

    best_days = 0
    run = 0
    previous = None
    for day in sorted(parsed):
        if previous is not None and (day - previous).days == 1:
            run += 1
        else:
            run = 1
        best_days = max(best_days, run)
        previous = day

    return {"current_days": current_days, "best_days": best_days, "trajectory": [day.isoformat() for day in sorted(parsed)]}


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

    # Ensure lifecycle rows (cards promoted without events in this window) still
    # appear in the per-card breakdown and mastery counts.
    _lc_ts = now.isoformat()
    for _row in lifecycle_rows:
        _bid = str(_row.get("base_card_id") or "")
        _dir = str(_row.get("direction") or "")
        if not _bid or not _dir:
            continue
        _cid = f"{_bid}#{_dir.replace('_', '-')}"
        if _cid not in per_card:
            _lc = str(_row.get("lifecycle") or "active").lower()
            per_card[_cid] = {
                "card_id": _cid,
                "base_card_id": _bid,
                "direction": _dir,
                "card_type": _row.get("card_type"),
                "attempts": 0,
                "correct": 0,
                "incorrect": 0,
                "consecutive_correct": 0,
                "last_answered_at": None,
                "lifecycle": _lc,
                "is_mastered": _lc == "revision",
                "mastered_by_criteria": _lc == "revision",
            }

    recent_by_base_direction: dict[str, dict[str, list[bool]]] = defaultdict(lambda: defaultdict(list))

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
        base_key = str(event.get("base_card_id") or "")
        direction_key = str(event.get("direction") or "")
        if base_key and direction_key:
            recent_by_base_direction[base_key][direction_key].append(bool(event.get("correct")))
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
                "consecutive_correct": 0,
                "last_answered_at": None,
            },
        )
        row["attempts"] += 1
        row["correct"] += int(bool(event.get("correct")))
        row["incorrect"] += int(not bool(event.get("correct")))
        if bool(event.get("correct")):
            row["consecutive_correct"] = row.get("consecutive_correct", 0) + 1
        else:
            row["consecutive_correct"] = 0
        if row["last_answered_at"] is None or ts > _parse_iso(str(row["last_answered_at"])):
            row["last_answered_at"] = event.get("answered_at")

    lifecycle_count = len(lifecycle_rows)
    session_count = len(sessions)

    streak = _day_streak(streak_days, now)

    sparse = {
        "is_sparse": total == 0 and session_count == 0 and lifecycle_count == 0,
        "events": total,
        "sessions": session_count,
        "lifecycles": lifecycle_count,
        "reason": "new_learner" if total == 0 and session_count == 0 and lifecycle_count == 0 else "established",
    }

    mastered_recent: dict[str, dict[str, Any]] = {}
    for base_card_id, per_direction in recent_by_base_direction.items():
        en_recent = per_direction.get("english_to_mirad", [])[-5:]
        mi_recent = per_direction.get("mirad_to_english", [])[-5:]
        en_pass = len(en_recent) == 5 and all(en_recent)
        mi_pass = len(mi_recent) == 5 and all(mi_recent)
        mastered_recent[base_card_id] = {
            "english_to_mirad": {"window": 5, "attempts": len(en_recent), "all_correct": en_pass},
            "mirad_to_english": {"window": 5, "attempts": len(mi_recent), "all_correct": mi_pass},
            "mastered": en_pass and mi_pass,
        }

    # Build authoritative lifecycle lookup so per_card entries carry the
    # exact lifecycle value used for mastered/active summary counts.
    # per_card keys use the same card_id shape as lifecycle rows:
    # "base_card_id#direction" (direction dashes normalized to underscores).
    lifecycle_by_card_id: dict[str, str] = {}
    for row in lifecycle_rows:
        base_id = str(row.get("base_card_id") or "")
        direction = str(row.get("direction") or "")
        card_id = f"{base_id}#{direction.replace('_', '-')}"
        lifecycle_by_card_id[card_id] = str(row.get("lifecycle") or "active")

    for card_id, card_row in per_card.items():
        card_row["lifecycle"] = lifecycle_by_card_id.get(card_id, card_row.get("lifecycle", "active"))
        # A card is mastered when lifecycle is revision, OR when it meets
        # the scheduler criteria: consecutive_correct >= 3 AND accuracy >= threshold.
        card_lifecycle = str(card_row.get("lifecycle") or "active")
        card_consecutive = int(card_row.get("consecutive_correct") or 0)
        card_attempts = int(card_row.get("attempts") or 0)
        card_correct = int(card_row.get("correct") or 0)
        card_accuracy = (card_correct / card_attempts) if card_attempts > 0 else None
        is_mastered_by_criteria = (
            card_lifecycle != "revision"
            and card_consecutive >= 3
            and card_accuracy is not None
            and card_accuracy >= MASTERY_ACCURACY_THRESHOLD
        )
        card_row["is_mastered"] = card_lifecycle == "revision" or is_mastered_by_criteria
        card_row["mastered_by_criteria"] = is_mastered_by_criteria
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
        "mastered_count": sum(1 for r in per_card.values() if bool(r.get("is_mastered"))),
        "active_count": sum(1 for r in per_card.values() if str(r.get("lifecycle") or "active") != "revision" and not bool(r.get("is_mastered"))),
        "per_card": per_card,
        "mastered_recent": mastered_recent,
        "filters": filters or {},
        "shown_card_count": len(shown_cards or []),
    }
