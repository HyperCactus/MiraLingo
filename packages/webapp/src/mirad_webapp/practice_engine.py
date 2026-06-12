"""Deterministic adaptive practice scheduler and session persistence helpers."""

from __future__ import annotations

import random
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from statistics import median
from typing import Any

_wordfreq_module: Any | None = None

MAX_EVENTS = 200
STALE_AFTER_SECONDS = 14 * 24 * 60 * 60
_WEAK_ACCURACY_THRESHOLD = 0.8
_NEW_ITEM_ACCURACY_THRESHOLD = 0.6
MASTERY_ACCURACY_THRESHOLD = 0.60
_MASTERY_ACCURACY_THRESHOLD = MASTERY_ACCURACY_THRESHOLD
_REINFORCE_MIN_ATTEMPTS = 3
_REPEAT_GAP = 3
MIXED_ACTIVE_DECK_SIZE = 10
_MIXED_ACTIVE_DECK_SIZE = MIXED_ACTIVE_DECK_SIZE
_BUILD_VOCABULARY_ACTIVE_DECK_SIZE = 12
_MIXED_ACTIVE_RATIO = 0.80
_BUILD_VOCABULARY_ACTIVE_RATIO = 0.80
_NEW_CARD_RELATED_BONUS = 0.35
_NEW_CARD_INVERSE_WEIGHT_MULTIPLIER = 3.0
_NUMBERS_NEW_CARD_PROBABILITY = 0.30
_DIRECTION_EXPOSURE_BALANCE_WEIGHT = 0.35
_DIRECTION_EXPOSURE_BALANCE_CAP = 4.0
_ID_RE = re.compile(r"[^a-z0-9]+")
_WORD_RE = re.compile(r"[A-Za-z']+")

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
_ACHIEVEMENT_BASE_MILESTONES = (1, 10, 20, 50, 80, 100)
_ACHIEVEMENT_REPEAT_AFTER = 100
_ACHIEVEMENT_REPEAT_STEP = 50


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
    lifecycle_rows: list[dict[str, Any]] | None = None,
    exposure_by_item: dict[str, int] | None = None,
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
    valid_events = _normalize_events(events or [], limit=None)
    stats = _stats_by_card(valid_events)
    base_stats = _stats_by_base_card(valid_events)
    recent_accuracy = _recent_accuracy(valid_events)
    weak_recent = recent_accuracy is not None and recent_accuracy < _NEW_ITEM_ACCURACY_THRESHOLD
    adaptive_state = _adaptive_session_state(valid_events)
    base_cards_with_history = {event["base_card_id"] for event in valid_events}

    seed = int(current.timestamp() * 1_000_000)
    rng = random.Random(seed)

    ranked: list[tuple[int, int, dict[str, Any], dict[str, Any]]] = []
    for index, card in enumerate(base_cards):
        directional_items = _practice_items_for_base_card(card, rng=rng)
        if _base_card_has_no_answer_history(card, directional_items, stats, base_stats):
            chosen_item = directional_items[index % len(directional_items)]
            chosen_stats = stats.get(chosen_item["id"], _empty_stats())
            reason = "new_item"
        else:
            reason, chosen_item, chosen_stats = _queue_item_for_base_card(
                card=card,
                directional_items=directional_items,
                stats=stats,
                base_stats=base_stats,
                now=current,
                weak_recent=weak_recent,
                adaptive_state=adaptive_state,
                rng=rng,
            )
        queue_item = {
            **chosen_item,
            "scheduler_reason": reason,
            "mastery": _mastery_payload(chosen_stats),
            "recency": _recency_payload(chosen_stats, current),
        }
        ranked.append((_rank(reason, base_stats.get(card["id"], _empty_stats()), current, adaptive_state), index, queue_item, card))

    ordered = _interleave_same_priority_cards(ranked, rng)
    filtered, mode_detail = _build_policy_queue(
        ordered=ordered,
        mode=normalized_mode,
        base_cards=base_cards,
        base_cards_with_history=base_cards_with_history,
        stats=stats,
        base_stats=base_stats,
        now=current,
        limit=max(0, int(limit)),
        rng=rng,
    )
    spaced, repeat_gap_satisfied = _apply_repeat_gap(
        filtered,
        repeat_gap=_REPEAT_GAP,
        adaptive_state=adaptive_state,
    )
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
        "card_count": len(base_cards),
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
            lifecycle_rows=lifecycle_rows or [],
            exposure_by_item=exposure_by_item or {},
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
    expected_alternatives = _expected_answer_alternatives(item)
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
    normalized_events = _normalize_events(events)
    queue = build_practice_queue(cards=cards, events=events, now=now, limit=len(items_by_id))
    selected = next((card for card in queue["cards"] if card["id"] == resolved_id), None)
    latest = next((event for event in reversed(normalized_events) if event["card_id"] == resolved_id), {})
    if selected is None and latest:
        selected = next((card for card in queue["cards"] if card["base_card_id"] == latest.get("base_card_id")), None)

    stats = _stats_by_card(normalized_events)
    current = _as_aware_datetime(now)
    latest_stat = stats.get(resolved_id, _empty_stats())
    latest_summary = _latest_event_summary(latest)
    weak_recent = _recent_accuracy(normalized_events) is not None and _recent_accuracy(normalized_events) < _NEW_ITEM_ACCURACY_THRESHOLD
    return {
        "ok": True,
        "phase": "practice_answer",
        "card_id": resolved_id,
        "base_card_id": latest.get("base_card_id") or (selected or {}).get("base_card_id"),
        "direction": latest.get("direction") or (selected or {}).get("direction"),
        "card_type": latest.get("card_type") or (selected or {}).get("type"),
        "correct": latest.get("correct"),
        "event_count": queue["event_count"],
        "scheduler_reason": _scheduler_reason(latest_stat, current, weak_recent) if latest else (selected or {}).get("scheduler_reason"),
        "mastery": _mastery_payload(latest_stat) if latest else (selected or {}).get("mastery"),
        "recency": _recency_payload(latest_stat, current) if latest else (selected or {}).get("recency"),
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


def build_practice_achievements(
    *, cards: list[dict[str, Any]], before_events: list[dict[str, Any]] | None, after_events: list[dict[str, Any]] | None, username: str, latest_card_id: str | None = None, now: datetime | None = None, lifecycle_rows: list[dict[str, Any]] | None = None
) -> list[dict[str, Any]]:
    """Return newly unlocked achievement payloads for mastery and streak milestones.

    Mastery detection for the after-state uses ``practice_lifecycle`` rows when
    available so that cards promoted to ``revision`` or that have a correct streak
    of 3+ are reliably counted as mastered.  The before-state always uses the
    event-window approach so that threshold crossings are correctly detected even
    when lifecycle state has already been updated by the current answer.
    """
    before_progress = build_practice_progress(cards=cards, events=before_events or [], now=now)
    after_progress = build_practice_progress(cards=cards, events=after_events or [], now=now)
    before_mastered = _mastered_item_ids(before_progress)
    after_mastered = _mastered_item_ids_from_lifecycle(after_progress, lifecycle_rows)

    unlocked: list[dict[str, Any]] = []
    before_day_streak = _practice_day_streak(before_events or [], now=now)
    after_day_streak = _practice_day_streak(after_events or [], now=now)
    for threshold in _streak_milestones_up_to(after_day_streak):
        if before_day_streak < threshold <= after_day_streak:
            unlocked.append(_streak_achievement_payload(username=username, threshold=threshold))

    if not after_mastered or len(after_mastered) <= len(before_mastered):
        return unlocked

    latest_base_card_id = None
    latest_item_id = None
    if latest_card_id:
        items_by_id, legacy_aliases = _practice_item_maps(cards)
        resolved_id = _resolve_practice_item_id(latest_card_id, items_by_id, legacy_aliases)
        if resolved_id and resolved_id in items_by_id:
            latest_item_id = resolved_id
            latest_base_card_id = str(items_by_id[resolved_id]["base_card_id"])
        elif str(latest_card_id) in {str(card.get("id")) for card in _normalize_base_cards(cards)}:
            latest_base_card_id = str(latest_card_id)

    for threshold in _achievement_milestones_up_to(len(after_mastered)):
        if len(before_mastered) < threshold <= len(after_mastered):
            if latest_item_id in after_mastered and latest_base_card_id:
                highlighted_base_card_id = latest_base_card_id
            else:
                highlighted_base_card_id = _base_card_id_from_event(next(iter(sorted(after_mastered))))
            unlocked.append(_achievement_payload(cards, username=username, threshold=threshold, highlighted_base_card_id=highlighted_base_card_id))
    return unlocked


def _mirad_english_synonyms(cards: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Build a mapping from each Mirad word to all English translations sharing it.

    For example, if "se" maps to both "is" and "are", the entry for "se"
    will be ["is", "are"].  Words with a single English translation
    (the common case) are still included as single-element lists.
    """
    base_cards = _normalize_base_cards(cards)
    synonyms: dict[str, list[str]] = {}
    for card in base_cards:
        mirad = card.get("mirad", "")
        english = card.get("english", "")
        if mirad and english:
            synonyms.setdefault(mirad, [])
            if english not in synonyms[mirad]:
                synonyms[mirad].append(english)
    return synonyms


def _expand_practice_items(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    synonyms = _mirad_english_synonyms(cards)
    items: list[dict[str, Any]] = []
    for card in _normalize_base_cards(cards):
        items.extend(_practice_items_for_base_card(card, synonyms=synonyms))
    return _attach_inverse_item_ids(items)


def _attach_inverse_item_ids(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Attach explicit inverse practice-item ids for same-Mirad opposite directions.

    General word cards are direction-specific practice items.  A card's inverse is
    any opposite-direction item with the same Mirad text, not only the same base
    card, because Mirad↔English can be one-to-many.  For example, both
    ``is → se`` and ``are → se`` are inverses of Mirad prompts for ``se``.
    """
    by_mirad: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: {ENGLISH_TO_MIRAD: [], MIRAD_TO_ENGLISH: []})
    for item in items:
        mirad = _normalize_text(item.get("mirad_text") or "")
        direction = str(item.get("direction") or "")
        if mirad and direction in by_mirad[mirad]:
            by_mirad[mirad][direction].append(item)

    enriched: list[dict[str, Any]] = []
    for item in items:
        mirad = _normalize_text(item.get("mirad_text") or "")
        direction = str(item.get("direction") or "")
        opposite = MIRAD_TO_ENGLISH if direction == ENGLISH_TO_MIRAD else ENGLISH_TO_MIRAD
        inverses = by_mirad.get(mirad, {}).get(opposite, [])
        inverse_ids = sorted({str(inverse["id"]) for inverse in inverses if inverse.get("id") != item.get("id")})
        inverse_base_ids = sorted({str(inverse["base_card_id"]) for inverse in inverses if inverse.get("base_card_id")})
        enriched.append({**item, "inverse_item_ids": inverse_ids, "inverse_base_card_ids": inverse_base_ids})
    return enriched


def _practice_items_for_base_card(card: dict[str, str], *, rng: random.Random | None = None, synonyms: dict[str, list[str]] | None = None) -> list[dict[str, str]]:
    items = [_practice_item(card, ENGLISH_TO_MIRAD, rng=rng, synonyms=synonyms)]
    if card.get("english_to_mirad_only") != "true":
        items.append(_practice_item(card, MIRAD_TO_ENGLISH, rng=rng, synonyms=synonyms))
    return items


def _choose_prompt_variant(value: str, *, card_type: str, rng: random.Random | None = None) -> str:
    if card_type != "word":
        return value
    options = [part.strip() for part in str(value).split(",") if part.strip()]
    if len(options) <= 1:
        return value
    if rng is None:
        return options[0]
    return options[rng.randrange(len(options))]


def _practice_item(card: dict[str, str], direction: str, *, rng: random.Random | None = None, synonyms: dict[str, list[str]] | None = None) -> dict[str, str]:
    if direction == ENGLISH_TO_MIRAD:
        prompt_language = "english"
        answer_language = "mirad"
        prompt = _choose_prompt_variant(card["english"], card_type=card["type"], rng=rng)
        answer = card.get("follow_up_mirad") or card["mirad"]
    else:
        prompt_language = "mirad"
        answer_language = "english"
        prompt = _choose_prompt_variant(card["mirad"], card_type=card["type"], rng=rng)
        primary_answer = card.get("follow_up_english") or card["english"]
        if synonyms:
            mirad = card.get("mirad", "")
            english_synonyms = synonyms.get(mirad, [])
            if len(english_synonyms) > 1:
                answer = ", ".join(english_synonyms)
            else:
                answer = primary_answer
        else:
            answer = primary_answer

    item = {
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
        "follow_up_english": card.get("follow_up_english", ""),
        "follow_up_mirad": card.get("follow_up_mirad", ""),
    }
    if card.get("beginner_order") is not None:
        item["beginner_order"] = str(card.get("beginner_order") or "0")
    if card.get("numbers_order") is not None:
        item["numbers_order"] = str(card.get("numbers_order") or "0")
    return item


def _base_card_has_no_answer_history(
    card: dict[str, str],
    directional_items: list[dict[str, str]],
    stats: dict[str, dict[str, Any]],
    base_stats: dict[str, dict[str, Any]],
) -> bool:
    base_stat = base_stats.get(card["id"], _empty_stats())
    if int(base_stat.get("attempts") or 0) > 0:
        return False
    return all(int(stats.get(item["id"], _empty_stats()).get("attempts") or 0) == 0 for item in directional_items)


def _queue_item_for_base_card(
    *,
    card: dict[str, str],
    directional_items: list[dict[str, str]],
    stats: dict[str, dict[str, Any]],
    base_stats: dict[str, dict[str, Any]],
    now: datetime,
    weak_recent: bool,
    adaptive_state: str,
    rng: random.Random,
) -> tuple[str, dict[str, str], dict[str, Any]]:
    direction_reasons = {
        item["direction"]: _scheduler_reason(stats.get(item["id"], _empty_stats()), now, weak_recent)
        for item in directional_items
    }
    reason = _base_scheduler_reason(directional_items, direction_reasons)
    chosen_item = _choose_direction_for_base_card(
        card=card,
        directional_items=directional_items,
        stats=stats,
        base_stats=base_stats,
        direction_reasons=direction_reasons,
        now=now,
        adaptive_state=adaptive_state,
        rng=rng,
    )
    chosen_stats = stats.get(chosen_item["id"], _empty_stats())
    return reason, chosen_item, chosen_stats


def _practice_item_maps(cards: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    items = _expand_practice_items(cards)
    by_id: dict[str, dict[str, Any]] = {}
    legacy_aliases: dict[str, str] = {}
    for item in items:
        # Import order is intentional: curated beginner/numbers content is loaded before
        # stochastic wordfreq cards. If two sources produce the same stable ID, keep the
        # curated item instead of silently letting a later generated card narrow scoring.
        by_id.setdefault(item["id"], item)
        if item["direction"] == ENGLISH_TO_MIRAD:
            legacy_aliases.setdefault(item["base_card_id"], item["id"])
    return by_id, legacy_aliases


def _base_scheduler_reason(directional_items: list[dict[str, str]], direction_reasons: dict[str, str]) -> str:
    reasons = [direction_reasons[item["direction"]] for item in directional_items]
    if "weak_recent_performance" in reasons:
        return "weak_recent_performance"
    if "stale_mastered_review" in reasons:
        return "stale_mastered_review"
    if any(reason in {"new_item", "new_item_gated_by_weak_recent_performance"} for reason in reasons):
        return "new_item_gated_by_weak_recent_performance" if all(reason == "new_item_gated_by_weak_recent_performance" for reason in reasons if reason in {"new_item", "new_item_gated_by_weak_recent_performance"}) else "new_item"
    return "mastered_recent"


def _choose_direction_for_base_card(
    *,
    card: dict[str, str],
    directional_items: list[dict[str, str]],
    stats: dict[str, dict[str, Any]],
    base_stats: dict[str, dict[str, Any]],
    direction_reasons: dict[str, str],
    now: datetime,
    adaptive_state: str,
    rng: random.Random,
) -> dict[str, str]:
    latest_event = base_stats.get(card["id"], _empty_stats()).get("latest_event")
    latest_direction = latest_event.get("direction") if isinstance(latest_event, dict) else None
    latest_seen = _parse_datetime(latest_event.get("answered_at")) if isinstance(latest_event, dict) else None
    latest_age_seconds = int((now - latest_seen).total_seconds()) if latest_seen else None
    attempts_by_direction = {
        item["direction"]: int(stats.get(item["id"], _empty_stats()).get("attempts") or 0)
        for item in directional_items
    }

    weighted_items: list[tuple[float, dict[str, str]]] = []
    for item in directional_items:
        stat = stats.get(item["id"], _empty_stats())
        reason = direction_reasons[item["direction"]]
        weight = 1.0

        if reason == "weak_recent_performance":
            weight += 6.0
        elif reason == "new_item":
            weight += 4.0
        elif reason == "new_item_gated_by_weak_recent_performance":
            weight += 2.5
        elif reason == "stale_mastered_review":
            weight += 3.0
        elif reason == "mastered_recent":
            weight += 1.0

        attempts = int(stat.get("attempts") or 0)
        if attempts == 0:
            weight += 2.0

        incorrect = int(stat.get("incorrect") or 0)
        if incorrect > 0:
            weight += 2.0

        opposite_direction = MIRAD_TO_ENGLISH if item["direction"] == ENGLISH_TO_MIRAD else ENGLISH_TO_MIRAD
        exposure_gap = attempts_by_direction.get(opposite_direction, 0) - attempts
        if exposure_gap > 0:
            weight += min(_DIRECTION_EXPOSURE_BALANCE_CAP, exposure_gap * _DIRECTION_EXPOSURE_BALANCE_WEIGHT)

        if latest_direction and item["direction"] != latest_direction:
            weight += 1.5
            if latest_age_seconds is not None and latest_age_seconds <= 24 * 60 * 60:
                weight += 2.5
        elif latest_direction and item["direction"] == latest_direction and latest_age_seconds is not None and latest_age_seconds <= 24 * 60 * 60:
            weight -= 1.0

        if adaptive_state == "struggling" and attempts > 0 and incorrect == 0:
            weight -= 0.5

        weighted_items.append((max(0.1, weight), item))

    total_weight = sum(weight for weight, _ in weighted_items)
    threshold = rng.random() * total_weight
    cursor = 0.0
    for weight, item in weighted_items:
        cursor += weight
        if threshold <= cursor:
            return item
    return directional_items[0]


def _build_policy_queue(
    *,
    ordered: list[dict[str, Any]],
    mode: str,
    base_cards: list[dict[str, str]],
    base_cards_with_history: set[str],
    stats: dict[str, dict[str, Any]],
    base_stats: dict[str, dict[str, Any]],
    now: datetime,
    limit: int,
    rng: random.Random,
) -> tuple[list[dict[str, Any]], str]:
    if limit <= 0 or not ordered:
        return [], "empty_pool"

    by_base = {item["base_card_id"]: item for item in ordered}
    card_by_base = {card["id"]: card for card in base_cards}
    mastered = [item for item in ordered if _is_mastered_item(item)]

    if mode == REVISION_MODE:
        mastered_weights = _mastered_card_probability_weights(mastered, base_stats)
        return _weighted_sequence(
            mastered,
            limit=limit,
            weight_fn=lambda item: mastered_weights.get(item["id"], 0.0),
            repeat_gap=_REPEAT_GAP,
            rng=rng,
        ), "seen_only"

    words_only = mode == BUILD_VOCABULARY_MODE
    active_deck_size = _BUILD_VOCABULARY_ACTIVE_DECK_SIZE if words_only else _MIXED_ACTIVE_DECK_SIZE
    active_ratio = _BUILD_VOCABULARY_ACTIVE_RATIO if words_only else _MIXED_ACTIVE_RATIO

    if words_only:
        ordered = [item for item in ordered if item["type"] == "word"]
        mastered = [item for item in mastered if item["type"] == "word"]
        by_base = {item["base_card_id"]: item for item in ordered}

    active_seen = [
        item for item in ordered
        if item["base_card_id"] in base_cards_with_history and not _is_mastered_item(item)
    ]
    active_seen.sort(key=lambda item: _last_seen_sort_key(item, base_stats))
    active_deck = active_seen[:active_deck_size]

    active_item_ids = {item["id"] for item in active_deck}
    beginner_unseen = _unseen_beginner_items(
        base_cards=base_cards,
        stats=stats,
        now=now,
        words_only=words_only,
        active_item_ids=active_item_ids,
    )
    beginner_gate_active = bool(beginner_unseen)
    while len(active_deck) < active_deck_size and beginner_unseen:
        chosen = _weighted_choice(beginner_unseen, _beginner_card_weight, rng)
        active_deck.append({**chosen, "scheduler_reason": "new_item"})
        active_item_ids.add(chosen["id"])
        beginner_unseen = [item for item in beginner_unseen if item["id"] != chosen["id"] and item["base_card_id"] != chosen["base_card_id"]]

    active_ids = {item["base_card_id"] for item in active_deck}
    related_bases = active_ids | {item["base_card_id"] for item in mastered}
    related_item_ids = {item["id"] for item in active_deck} | {item["id"] for item in mastered}
    unseen = [
        item for item in ordered
        if not beginner_gate_active
        and item["base_card_id"] not in base_cards_with_history
        and item["base_card_id"] not in active_ids
        and item.get("numbers_order") is None
        and item["scheduler_reason"] in {"new_item", "new_item_gated_by_weak_recent_performance"}
    ]
    numbers_unseen = [] if beginner_gate_active else _unseen_number_items(
        base_cards=base_cards,
        stats=stats,
        now=now,
        words_only=words_only,
        active_item_ids=active_item_ids,
    )
    def new_card_weight(item: dict[str, Any]) -> float:
        return _new_card_weight(item, card_by_base.get(item["base_card_id"], {}), related_bases, related_item_ids)

    while len(active_deck) < active_deck_size and (unseen or numbers_unseen):
        pool = unseen
        weight_fn = new_card_weight
        using_numbers_pool = False
        if numbers_unseen and (not unseen or rng.random() < _NUMBERS_NEW_CARD_PROBABILITY):
            pool = numbers_unseen
            weight_fn = _module_order_weight
            using_numbers_pool = True
        elif not words_only:
            preferred_type = "phrase" if rng.random() < 0.5 else "word"
            preferred_pool = [item for item in unseen if item["type"] == preferred_type]
            if preferred_pool:
                pool = preferred_pool
        chosen = _weighted_choice(pool, weight_fn, rng)
        active_deck.append({**chosen, "scheduler_reason": "new_item"})
        active_ids.add(chosen["base_card_id"])
        active_item_ids.add(chosen["id"])
        if using_numbers_pool:
            numbers_unseen = [item for item in numbers_unseen if item["id"] != chosen["id"] and item["base_card_id"] != chosen["base_card_id"] and item["id"] not in active_item_ids]
        else:
            unseen = [item for item in unseen if item["base_card_id"] != chosen["base_card_id"]]
            numbers_unseen = [item for item in numbers_unseen if item["id"] not in active_item_ids]

    active_deck = [item for item in active_deck if item["base_card_id"] in by_base]
    if not active_deck and not mastered:
        return [], "empty_pool"

    active_slots = int(round(limit * active_ratio))
    active_slots = min(limit, max(0, active_slots))
    revision_slots = limit - active_slots

    if not mastered:
        active_slots = min(limit, len(active_deck))
        revision_slots = 0
    if not active_deck:
        active_slots = 0
        revision_slots = limit

    active_sequence = _weighted_sequence(
        active_deck,
        limit=active_slots,
        weight_fn=lambda item: _active_card_weight(item, base_stats, now),
        repeat_gap=_REPEAT_GAP,
        rng=rng,
    )
    mastered_weights = _mastered_card_probability_weights(mastered, base_stats)
    mastered_sequence = _weighted_sequence(
        mastered,
        limit=revision_slots,
        weight_fn=lambda item: mastered_weights.get(item["id"], 0.0),
        repeat_gap=_REPEAT_GAP,
        rng=rng,
    )

    scheduled = _interleave_policy_groups(
        active_sequence,
        mastered_sequence,
        active_ratio=active_ratio,
        repeat_gap=_REPEAT_GAP,
    )
    detail = "new_words_only" if mode == BUILD_VOCABULARY_MODE else "default_mixed"
    return scheduled[:limit], detail


def _is_mastered_item(item: dict[str, Any]) -> bool:
    return item.get("scheduler_reason") in {"mastered_recent", "stale_mastered_review"}


def _unseen_beginner_items(
    *,
    base_cards: list[dict[str, str]],
    stats: dict[str, dict[str, Any]],
    now: datetime,
    words_only: bool,
    active_item_ids: set[str],
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for card in base_cards:
        if card.get("beginner_order") is None:
            continue
        if words_only and card.get("type") != "word":
            continue
        for direction in (ENGLISH_TO_MIRAD, MIRAD_TO_ENGLISH):
            item = _practice_item(card, direction)
            if item["id"] in active_item_ids:
                continue
            if int(stats.get(item["id"], _empty_stats()).get("attempts") or 0) > 0:
                continue
            item_stats = stats.get(item["id"], _empty_stats())
            items.append({
                **item,
                "scheduler_reason": "new_item",
                "mastery": _mastery_payload(item_stats),
                "recency": _recency_payload(item_stats, now),
            })
    return items


def _unseen_number_items(
    *,
    base_cards: list[dict[str, str]],
    stats: dict[str, dict[str, Any]],
    now: datetime,
    words_only: bool,
    active_item_ids: set[str],
) -> list[dict[str, Any]]:
    return _unseen_ordered_module_items(
        base_cards=base_cards,
        stats=stats,
        now=now,
        words_only=words_only,
        active_item_ids=active_item_ids,
        order_field="numbers_order",
    )


def _unseen_ordered_module_items(
    *,
    base_cards: list[dict[str, str]],
    stats: dict[str, dict[str, Any]],
    now: datetime,
    words_only: bool,
    active_item_ids: set[str],
    order_field: str,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for card in base_cards:
        if card.get(order_field) is None:
            continue
        if words_only and card.get("type") != "word":
            continue
        for direction in (ENGLISH_TO_MIRAD, MIRAD_TO_ENGLISH):
            item = _practice_item(card, direction)
            if item["id"] in active_item_ids:
                continue
            if int(stats.get(item["id"], _empty_stats()).get("attempts") or 0) > 0:
                continue
            item_stats = stats.get(item["id"], _empty_stats())
            items.append({
                **item,
                "scheduler_reason": "new_item",
                "mastery": _mastery_payload(item_stats),
                "recency": _recency_payload(item_stats, now),
            })
    return items


def _module_order_weight(item: dict[str, Any]) -> float:
    order_value = item.get("beginner_order") if item.get("beginner_order") is not None else item.get("numbers_order")
    try:
        order = max(0, int(str(order_value or "0")))
    except ValueError:
        order = 0
    return 1.0 / float(order + 1)


def _beginner_card_weight(item: dict[str, Any]) -> float:
    return _module_order_weight(item)


def _active_card_weight(item: dict[str, Any], base_stats: dict[str, dict[str, Any]], now: datetime) -> float:
    stat = base_stats.get(item["base_card_id"], _empty_stats())
    seen_at = _parse_datetime(stat.get("last_seen_at")) if stat.get("last_seen_at") else None
    age_seconds = max(0, int((now - seen_at).total_seconds())) if seen_at else STALE_AFTER_SECONDS
    recency_weight = 1.0 + min(10.0, age_seconds / 3600.0)
    weakness_weight = 1.0
    if item.get("scheduler_reason") == "weak_recent_performance":
        weakness_weight += 10.0
    attempts = int(stat.get("attempts") or 0)
    if attempts:
        weakness_weight += max(0.0, 1.0 - (float(stat.get("correct") or 0) / attempts))
    return recency_weight * weakness_weight


def _mastered_card_probability_weights(items: list[dict[str, Any]], base_stats: dict[str, dict[str, Any]]) -> dict[str, float]:
    """Return normalized mastered selection weights with a 1/(2n) probability floor.

    Half of the probability mass is uniform across mastered cards. The other half
    is distributed by weakness: lower accuracy and lower total attempts are more
    likely to be reviewed.
    """
    if not items:
        return {}
    item_count = len(items)
    floor_probability = 1.0 / (2.0 * item_count)
    scores = {item["id"]: _mastered_card_score(item, base_stats) for item in items}
    total_score = sum(scores.values())
    if total_score <= 0:
        return {item["id"]: 1.0 / item_count for item in items}
    return {
        item["id"]: floor_probability + 0.5 * (scores[item["id"]] / total_score)
        for item in items
    }


def _mastered_card_score(item: dict[str, Any], base_stats: dict[str, dict[str, Any]]) -> float:
    stat = base_stats.get(item["base_card_id"], _empty_stats())
    attempts = int(stat.get("attempts") or 0)
    if attempts <= 0:
        return 1.0
    accuracy = float(stat.get("correct") or 0) / attempts
    accuracy_gap = max(0.0, 1.0 - accuracy)
    exposure_gap = 1.0 / (attempts + 1.0)
    return max(0.01, accuracy_gap + exposure_gap)


def _new_card_weight(item: dict[str, Any], card: dict[str, str], related_bases: set[str], related_item_ids: set[str] | None = None) -> float:
    frequency_score = _normalized_english_frequency(card.get("english") or item.get("english_text") or "")
    related_bonus = _NEW_CARD_RELATED_BONUS * _related_card_count(card, related_bases)
    weight = max(0.01, frequency_score + related_bonus)
    inverse_ids = {str(item_id) for item_id in item.get("inverse_item_ids", [])}
    if related_item_ids and inverse_ids & related_item_ids:
        weight *= _NEW_CARD_INVERSE_WEIGHT_MULTIPLIER
    return weight


def _normalized_english_frequency(text: str) -> float:
    words = _WORD_RE.findall(str(text).casefold())
    if not words:
        return 0.01
    wordfreq_module = _wordfreq()
    if wordfreq_module is None:
        return 0.5
    scores = [max(0.0, min(1.0, wordfreq_module.zipf_frequency(word, "en") / 7.0)) for word in words]
    return float(median(scores))


def _wordfreq() -> Any | None:
    global _wordfreq_module
    if _wordfreq_module is not None:
        return _wordfreq_module
    try:
        import wordfreq as imported_wordfreq
    except ImportError:  # pragma: no cover - exercised only in minimal local environments
        return None
    _wordfreq_module = imported_wordfreq
    return _wordfreq_module


def _related_card_count(card: dict[str, str], related_bases: set[str]) -> int:
    if not related_bases:
        return 0
    card_id = str(card.get("id") or "")
    if card_id in related_bases:
        return 1
    tokens = set(_WORD_RE.findall(str(card.get("english") or "").casefold())) | set(_WORD_RE.findall(str(card.get("mirad") or "").casefold()))
    if not tokens:
        return 0
    count = 0
    for related in related_bases:
        related_tokens = set(_WORD_RE.findall(str(related).casefold()))
        if tokens & related_tokens:
            count += 1
    return count


def _last_seen_sort_key(item: dict[str, Any], base_stats: dict[str, dict[str, Any]]) -> tuple[int, str]:
    stat = base_stats.get(item["base_card_id"], _empty_stats())
    seen_at = _parse_datetime(stat.get("last_seen_at")) if stat.get("last_seen_at") else None
    timestamp = int(seen_at.timestamp()) if seen_at else 0
    return (timestamp, item["base_card_id"])


def _weighted_sequence(
    items: list[dict[str, Any]],
    *,
    limit: int,
    weight_fn: Any,
    repeat_gap: int,
    rng: random.Random,
) -> list[dict[str, Any]]:
    if limit <= 0 or not items:
        return []
    sequence: list[dict[str, Any]] = []
    recent: list[str] = []
    used_item_ids: set[str] = set()
    for index in range(limit):
        allowed = [item for item in items if item["base_card_id"] not in set(recent[-repeat_gap:])]
        candidates = allowed or items
        if index < len(items):
            unused_candidates = [item for item in candidates if item["id"] not in used_item_ids]
            if unused_candidates:
                candidates = unused_candidates
            chosen = max(candidates, key=weight_fn)
        else:
            chosen = _weighted_choice(candidates, weight_fn, rng)
        sequence.append(chosen)
        used_item_ids.add(chosen["id"])
        recent.append(chosen["base_card_id"])
    return sequence


def _weighted_choice(items: list[dict[str, Any]], weight_fn: Any, rng: random.Random) -> dict[str, Any]:
    weighted = [(max(0.01, float(weight_fn(item))), item) for item in items]
    total = sum(weight for weight, _ in weighted)
    threshold = rng.random() * total
    cursor = 0.0
    for weight, item in weighted:
        cursor += weight
        if threshold <= cursor:
            return item
    return items[-1]


def _interleave_policy_groups(
    active: list[dict[str, Any]],
    mastered: list[dict[str, Any]],
    *,
    active_ratio: float,
    repeat_gap: int,
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    active_index = 0
    mastered_index = 0
    total = len(active) + len(mastered)
    for position in range(total):
        desired_active = int(round((position + 1) * active_ratio))
        active_so_far = sum(1 for item in result if not _is_mastered_item(item))
        prefer_active = active_index < len(active) and active_so_far < desired_active
        pools = ["active", "mastered"] if prefer_active else ["mastered", "active"]
        chosen_group = None
        for group in pools:
            candidate = active[active_index] if group == "active" and active_index < len(active) else mastered[mastered_index] if group == "mastered" and mastered_index < len(mastered) else None
            if candidate is None:
                continue
            if candidate["base_card_id"] not in {item["base_card_id"] for item in result[-repeat_gap:]}:
                chosen_group = group
                break
        if chosen_group is None:
            chosen_group = "active" if prefer_active and active_index < len(active) else "mastered" if mastered_index < len(mastered) else "active"
        if chosen_group == "active" and active_index < len(active):
            result.append(active[active_index])
            active_index += 1
        elif mastered_index < len(mastered):
            result.append(mastered[mastered_index])
            mastered_index += 1
        elif active_index < len(active):
            result.append(active[active_index])
            active_index += 1
    return result


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
        revised = [
            item for item in ordered
            if item["scheduler_reason"] in {"stale_mastered_review", "mastered_recent", "weak_recent_performance"}
            and item_is_seen(item)
        ]
        return revised, "seen_only"
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


def _interleave_same_priority_cards(
    ranked: list[tuple[int, int, dict[str, Any], dict[str, Any]]], rng: random.Random
) -> list[dict[str, Any]]:
    """Order scheduler ranks while mixing card types at the base-pair level within equal-priority buckets."""
    by_rank: dict[int, list[tuple[int, dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    for rank, index, item, card in ranked:
        by_rank[rank].append((index, item, card))

    ordered: list[dict[str, Any]] = []
    for rank in sorted(by_rank):
        by_group: dict[str, list[dict[str, Any]]] = defaultdict(list)
        group_order: list[str] = []
        for _, item, card in sorted(by_rank[rank], key=lambda row: row[0]):
            group = card["type"]
            if group not in by_group:
                group_order.append(group)
            by_group[group].append(item)

        for group in group_order:
            rng.shuffle(by_group[group])

        while any(by_group.values()):
            for group in group_order:
                if by_group[group]:
                    ordered.append(by_group[group].pop())
    return ordered


def _build_mixed_mode_diagnostics(
    *,
    selected_cards: list[dict[str, Any]],
    all_items: list[dict[str, Any]],
    stats: dict[str, dict[str, Any]],
    repeat_gap_satisfied: bool,
    lifecycle_rows: list[dict[str, Any]],
    exposure_by_item: dict[str, int],
) -> dict[str, Any]:
    requested_active_revision_ratio = {"active": _MIXED_ACTIVE_RATIO, "revision": round(1.0 - _MIXED_ACTIVE_RATIO, 2)}
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
    if round(abs(actual_active - requested_active_revision_ratio["active"]), 2) >= 0.2:
        fallback_reasons.append("ratio_drift")
    if round(abs(actual_word - requested_word_phrase_mix["word"]), 2) > 0.2:
        fallback_reasons.append("mix_drift")

    lifecycle_counts = {
        "active": sum(1 for row in lifecycle_rows if str(row.get("lifecycle") or "") == "active"),
        "revision": sum(1 for row in lifecycle_rows if str(row.get("lifecycle") or "") == "revision"),
    }

    return {
        "requested_active_revision_ratio": requested_active_revision_ratio,
        "actual_active_revision_ratio": {"active": actual_active, "revision": actual_revision},
        "requested_word_phrase_mix": requested_word_phrase_mix,
        "actual_word_phrase_mix": {"word": actual_word, "phrase": actual_phrase},
        "weighting_inputs": {"exposure_weight": 0.5, "recent_performance_weight": 0.5},
        "per_card_weights": per_card_weights,
        "lifecycle_counts": lifecycle_counts,
        "exposure_by_item": exposure_by_item,
        "repeat_gap": _REPEAT_GAP,
        "repeat_gap_satisfied": repeat_gap_satisfied,
        "repeat_gap_relaxed": not repeat_gap_satisfied,
        "fallback_reasons": fallback_reasons,
    }


def _apply_repeat_gap(items: list[dict[str, Any]], *, repeat_gap: int, adaptive_state: str = "neutral") -> tuple[list[dict[str, Any]], bool]:
    if not items:
        return [], False

    pending = list(items)
    scheduled: list[dict[str, Any]] = []
    recent_base_ids: list[str] = []
    repeat_gap_satisfied = True

    while pending:
        blocked_bases = set(recent_base_ids[-repeat_gap:])
        allowed_indexes = [index for index, item in enumerate(pending) if item["base_card_id"] not in blocked_bases]

        if adaptive_state == "struggling" and allowed_indexes:
            seen_allowed = [
                index
                for index in allowed_indexes
                if item_is_seen(pending[index])
            ]
            if seen_allowed:
                candidate_index = seen_allowed[0]
            else:
                seen_pending = [index for index, item in enumerate(pending) if item_is_seen(item)]
                if seen_pending:
                    repeat_gap_satisfied = False
                    candidate_index = seen_pending[0]
                else:
                    candidate_index = allowed_indexes[0]
        else:
            candidate_index = allowed_indexes[0] if allowed_indexes else None

        if candidate_index is None:
            repeat_gap_satisfied = False
            if adaptive_state == "struggling":
                seen_pending = [index for index, item in enumerate(pending) if item_is_seen(item)]
                candidate_index = seen_pending[0] if seen_pending else 0
            else:
                candidate_index = 0
        chosen = pending.pop(candidate_index)
        scheduled.append(chosen)
        recent_base_ids.append(chosen["base_card_id"])

    if len({item["base_card_id"] for item in items}) <= repeat_gap:
        repeat_gap_satisfied = False

    return scheduled, repeat_gap_satisfied


def item_is_seen(item: dict[str, Any]) -> bool:
    return item.get("scheduler_reason") not in {"new_item", "new_item_gated_by_weak_recent_performance"}


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


def _mastered_item_ids(progress_payload: dict[str, Any]) -> set[str]:
    mastered: set[str] = set()
    for key in ("mastered_cards", "stale_cards"):
        mastered.update(
            str(card_id)
            for card_id in (progress_payload.get(key) or [])
            if isinstance(card_id, str) and card_id
        )
    return mastered


def _mastered_item_ids_from_lifecycle(progress_payload: dict[str, Any], lifecycle_rows: list[dict[str, Any]] | None) -> set[str]:
    """Return mastered item IDs using lifecycle status and scheduler mastery.

    Cards in lifecycle ``revision`` are always mastered.  Cards in
    ``active`` that meet the scheduler mastery threshold
    (consecutive_correct >= 3, accuracy >= 0.60) are also mastered
    so that milestones are detected at the same threshold as the
    practice scheduler.

    When lifecycle data is unavailable, falls back to the progress
    payload's ``mastered_cards`` list.
    """
    if lifecycle_rows:
        lifecycle_mastered_ids: set[str] = set()
        for row in lifecycle_rows:
            row_dict = row if isinstance(row, dict) else (row.public_dict() if hasattr(row, "public_dict") else {})
            base_id = str(row_dict.get("base_card_id") or "")
            direction = str(row_dict.get("direction") or "")
            if not base_id or not direction:
                continue
            item_id = f"{base_id}#{direction.replace('_', '-')}"
            lifecycle = str(row_dict.get("lifecycle") or "").lower()
            if lifecycle == "revision":
                lifecycle_mastered_ids.add(item_id)
            elif lifecycle == "active":
                # Active items can still be mastered by scheduler criteria.
                consecutive = int(row_dict.get("correct_streak") or row_dict.get("consecutive_correct") or 0)
                if consecutive >= 3:
                    # Verify accuracy >= 0.60 from per_card data if available.
                    card_accuracy = None
                    per_card_data = progress_payload.get("per_card") or []
                    for item in per_card_data if isinstance(per_card_data, list) else []:
                        item_dir = str(item.get("direction") or "").replace("_", "-")
                        if str(item.get("base_card_id") or "") == base_id and item_dir == direction.replace("_", "-"):
                            card_attempts = int(item.get("attempts") or 0)
                            card_correct = int(item.get("correct") or 0)
                            card_accuracy = (card_correct / card_attempts) if card_attempts > 0 else 0.0
                            break
                    if card_accuracy is not None and card_accuracy >= _MASTERY_ACCURACY_THRESHOLD:
                        lifecycle_mastered_ids.add(item_id)

        return _mastered_item_ids(progress_payload) | lifecycle_mastered_ids

    return _mastered_item_ids(progress_payload)


def _mastered_base_card_ids(progress_payload: dict[str, Any]) -> set[str]:
    mastered_items = {
        str(card_id)
        for card_id in (progress_payload.get("mastered_cards") or [])
        if isinstance(card_id, str) and card_id
    }
    per_direction: dict[str, set[str]] = defaultdict(set)
    for item_id in mastered_items:
        base_card_id = _base_card_id_from_event(item_id)
        direction = _normalize_direction(None, item_id)
        per_direction[base_card_id].add(direction)
    return {
        base_card_id
        for base_card_id, directions in per_direction.items()
        if ENGLISH_TO_MIRAD in directions and MIRAD_TO_ENGLISH in directions
    }


def build_practice_achievement_candidates(
    *,
    cards: list[dict[str, Any]],
    username: str,
    mastered_count: int,
    streak_days: int,
    latest_card_id: str | None = None,
) -> list[dict[str, Any]]:
    """Return all achievement payloads eligible for the given canonical snapshot.

    This function does not decide whether a payload is newly unlocked. Durable
    storage owns that decision via the ``practice_achievements`` table.
    """
    candidates: list[dict[str, Any]] = []
    for threshold in _streak_milestones_up_to(max(0, int(streak_days))):
        candidates.append(_streak_achievement_payload(username=username, threshold=threshold))

    highlighted_base_card_id = _highlight_base_card_id(cards, latest_card_id)
    for threshold in _achievement_milestones_up_to(max(0, int(mastered_count))):
        candidates.append(_achievement_payload(cards, username=username, threshold=threshold, highlighted_base_card_id=highlighted_base_card_id))
    return candidates


def _highlight_base_card_id(cards: list[dict[str, Any]], latest_card_id: str | None) -> str:
    base_cards = _normalize_base_cards(cards)
    base_ids = {str(card.get("id")) for card in base_cards}
    if latest_card_id:
        items_by_id, legacy_aliases = _practice_item_maps(cards)
        resolved_id = _resolve_practice_item_id(latest_card_id, items_by_id, legacy_aliases)
        if resolved_id and resolved_id in items_by_id:
            return str(items_by_id[resolved_id]["base_card_id"])
        latest_base = _base_card_id_from_event(str(latest_card_id))
        if latest_base in base_ids:
            return latest_base
    return sorted(base_ids)[0] if base_ids else ""


def _achievement_milestones_up_to(count: int) -> list[int]:
    milestones = [value for value in _ACHIEVEMENT_BASE_MILESTONES if value <= count]
    if count <= _ACHIEVEMENT_REPEAT_AFTER:
        return milestones

    next_threshold = _ACHIEVEMENT_REPEAT_AFTER + _ACHIEVEMENT_REPEAT_STEP
    while next_threshold <= count:
        milestones.append(next_threshold)
        next_threshold += _ACHIEVEMENT_REPEAT_STEP
    return milestones


def _streak_milestones_up_to(count: int) -> list[int]:
    if count < 5:
        return []
    return list(range(5, count + 1, 5))


def _practice_day_streak(events: list[dict[str, Any]], *, now: datetime | None = None) -> int:
    days = set()
    for event in events:
        answered_at = _parse_datetime(event.get("answered_at") if isinstance(event, dict) else None)
        if answered_at is not None:
            days.add(answered_at.date())
    if not days:
        return 0
    today = _as_aware_datetime(now).date()
    latest_allowed = today if today in days else today - timedelta(days=1)
    streak = 0
    cursor = latest_allowed
    while cursor in days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def _streak_achievement_payload(*, username: str, threshold: int) -> dict[str, Any]:
    return {
        "id": f"practice-streak-{threshold}",
        "kind": "practice_streak",
        "threshold": threshold,
        "title": f"🔥 {threshold}-day streak!",
        "message": (
            f"Congratulations {username}! ✨\n"
            f"You practiced {threshold} days in a row.\n"
            "Keep the streak alive with one small session tomorrow! 🚀"
        ),
        "sound": "achievement",
    }


def _achievement_payload(cards: list[dict[str, Any]], *, username: str, threshold: int, highlighted_base_card_id: str) -> dict[str, Any]:
    base_cards = {str(card.get("id")): card for card in _normalize_base_cards(cards)}
    highlighted_card = base_cards.get(highlighted_base_card_id, {})
    english = str(highlighted_card.get("english") or "this pair")
    mirad = str(highlighted_card.get("mirad") or "Mirad")
    pair_label = f"{english} ↔ {mirad}"

    if threshold == 1:
        title = "🏆 First card mastered!"
        message = (
            f"Congratulations {username}! 🎉\n"
            f"You have mastered your first card: {pair_label}\n"
            "Keep up the good work! 🚀"
        )
    else:
        title = f"🏆 {threshold} cards mastered!"
        message = (
            f"Congratulations {username}! ✨\n"
            f"You have now mastered {threshold} cards. Latest win: {pair_label}\n"
            "Your Mirad is getting stronger every session! 🔥"
        )

    return {
        "id": f"mastered-cards-{threshold}",
        "kind": "mastered_cards",
        "threshold": threshold,
        "title": title,
        "message": message,
        "highlighted_base_card_id": highlighted_base_card_id,
        "highlighted_pair": {"english": english, "mirad": mirad},
        "sound": "achievement",
    }


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
    if card.get("follow_up_english"):
        typed["follow_up_english"] = str(card.get("follow_up_english") or "").strip()
    if card.get("follow_up_mirad"):
        typed["follow_up_mirad"] = str(card.get("follow_up_mirad") or "").strip()
    if card.get("beginner_order") is not None:
        typed["beginner_order"] = str(card.get("beginner_order") or "0").strip()
    if card.get("numbers_order") is not None:
        typed["numbers_order"] = str(card.get("numbers_order") or "0").strip()
    if card.get("english_to_mirad_only"):
        typed["english_to_mirad_only"] = "true"
    return typed


def _normalize_events(events: list[dict[str, Any]], *, limit: int | None = MAX_EVENTS) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    if limit is None:
        bounded_events = events
    else:
        bounded_events = events[-int(limit):] if int(limit) > 0 else []
    for event in bounded_events:
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
        stat["consecutive_correct"] = stat["consecutive_correct"] + 1 if event["correct"] else 0
        stat["last_seen_at"] = event["answered_at"]
        stat["latest_event"] = event
    return dict(stats)


def _stats_by_base_card(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    stats = defaultdict(_empty_stats)
    for event in events:
        stat = stats[event["base_card_id"]]
        stat["attempts"] += 1
        stat["correct"] += 1 if event["correct"] else 0
        stat["incorrect"] += 0 if event["correct"] else 1
        stat["consecutive_correct"] = stat["consecutive_correct"] + 1 if event["correct"] else 0
        stat["last_seen_at"] = event["answered_at"]
        stat["latest_event"] = event
    return dict(stats)


def _empty_stats() -> dict[str, Any]:
    return {"attempts": 0, "correct": 0, "incorrect": 0, "consecutive_correct": 0, "last_seen_at": None, "latest_event": None}


def _mastery_payload(stat: dict[str, Any]) -> dict[str, Any]:
    attempts = stat["attempts"]
    consecutive_correct = int(stat.get("consecutive_correct") or 0)
    accuracy = None if attempts == 0 else stat["correct"] / attempts
    mastered = consecutive_correct >= 3 and (accuracy is not None and accuracy >= _MASTERY_ACCURACY_THRESHOLD)
    return {
        "attempts": attempts,
        "correct": stat["correct"],
        "incorrect": stat["incorrect"],
        "accuracy": accuracy,
        "consecutive_correct": consecutive_correct,
        "streak_required": 3,
        "mastered": mastered,
    }


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
    consecutive_correct = int(stat.get("consecutive_correct") or 0)
    if consecutive_correct >= 3 and accuracy >= _MASTERY_ACCURACY_THRESHOLD:
        seen = _parse_datetime(stat["last_seen_at"])
        if seen and int((now - seen).total_seconds()) >= STALE_AFTER_SECONDS:
            return "stale_mastered_review"
        return "mastered_recent"
    if accuracy < _WEAK_ACCURACY_THRESHOLD:
        return "weak_recent_performance"
    return "new_item_gated_by_weak_recent_performance" if weak_recent else "new_item"


def _rank(reason: str, stat: dict[str, Any], now: datetime, adaptive_state: str = "neutral") -> int:
    order = _rank_order_for_state(adaptive_state)
    base = order.get(reason, 9) * 10
    return base + _adaptive_rank_offset(reason, stat, now, adaptive_state)


def _rank_order_for_state(adaptive_state: str) -> dict[str, int]:
    """State-aware primary ordering.

    Struggling sessions should avoid introducing new material too aggressively.
    """
    if adaptive_state == "struggling":
        return {
            "weak_recent_performance": 0,
            "mastered_recent": 1,
            "stale_mastered_review": 2,
            "new_item": 3,
            "new_item_gated_by_weak_recent_performance": 4,
        }

    return {
        "weak_recent_performance": 0,
        "stale_mastered_review": 1,
        "new_item": 2,
        "new_item_gated_by_weak_recent_performance": 3,
        "mastered_recent": 4,
    }


def _adaptive_rank_offset(reason: str, stat: dict[str, Any], now: datetime, adaptive_state: str) -> int:
    """Small in-band rank adjustment so session performance nudges recency selection efficiently."""
    if reason != "mastered_recent":
        return 0

    attempts = int(stat.get("attempts") or 0)
    # Keep low-exposure mastered items near the front so first-time correct cards
    # are reinforced quickly instead of disappearing from rotation.
    if attempts < _REINFORCE_MIN_ATTEMPTS:
        return -3

    seen_at_raw = stat.get("last_seen_at")
    seen_at = _parse_datetime(seen_at_raw) if seen_at_raw else None
    age_seconds = int((now - seen_at).total_seconds()) if seen_at else 0

    # Struggling learners: favor recently seen mastered cards (lower offset = earlier).
    if adaptive_state == "struggling":
        return 0 if age_seconds <= 2 * 24 * 60 * 60 else 2

    # Strong learners: favor less-recent mastered cards to widen spacing.
    if adaptive_state == "strong":
        return 0 if age_seconds >= 2 * 24 * 60 * 60 else 2

    return 1


def _adaptive_session_state(events: list[dict[str, Any]]) -> str:
    """Classify session performance from a short trailing window: struggling/neutral/strong."""
    if not events:
        return "neutral"
    recent = events[-8:]
    accuracy = sum(1 for event in recent if event["correct"]) / len(recent)
    if accuracy <= 0.4:
        return "struggling"
    if accuracy >= 0.85:
        return "strong"
    return "neutral"


def _recent_accuracy(events: list[dict[str, Any]]) -> float | None:
    if not events:
        return None
    recent = events[-5:]
    return sum(1 for event in recent if event["correct"]) / len(recent)


def _normalize_answer_alternatives(value: Any) -> set[str]:
    normalized = {_normalize_text(part) for part in str(value).split(",")}
    return {part for part in normalized if part}


def _expected_answer_alternatives(item: dict[str, Any]) -> set[str]:
    return _normalize_answer_alternatives(item.get("answer", ""))


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
