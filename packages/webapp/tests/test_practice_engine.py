from __future__ import annotations

from datetime import datetime, timedelta, timezone

from mirad_webapp.practice import MAX_EVENTS
from mirad_webapp.practice_engine import build_practice_queue, record_practice_answer


NOW = datetime(2026, 5, 23, 12, 0, tzinfo=timezone.utc)


CARDS = [
    {"id": "phrase:hello-world", "type": "phrase", "english": "hello world", "mirad": "ha world"},
    {"id": "phrase:good-morning", "type": "phrase", "english": "good morning", "mirad": "gud morgen"},
    {"id": "word:the", "type": "word", "english": "the", "mirad": "te"},
    {"id": "word:be", "type": "word", "english": "be", "mirad": "bi"},
]


def test_build_practice_queue_returns_bounded_diagnostics_for_new_session() -> None:
    queue = build_practice_queue(cards=CARDS, events=[], now=NOW, limit=3)

    assert queue == {
        "ok": True,
        "phase": "practice_queue",
        "card_count": 4,
        "event_count": 0,
        "limit": 3,
        "cards": [
            {
                "id": "phrase:hello-world",
                "type": "phrase",
                "prompt": "hello world",
                "answer": "ha world",
                "scheduler_reason": "new_item",
                "mastery": {"attempts": 0, "correct": 0, "incorrect": 0, "accuracy": None},
                "recency": {"last_seen_at": None, "age_seconds": None},
            },
            {
                "id": "phrase:good-morning",
                "type": "phrase",
                "prompt": "good morning",
                "answer": "gud morgen",
                "scheduler_reason": "new_item",
                "mastery": {"attempts": 0, "correct": 0, "incorrect": 0, "accuracy": None},
                "recency": {"last_seen_at": None, "age_seconds": None},
            },
            {
                "id": "word:the",
                "type": "word",
                "prompt": "the",
                "answer": "te",
                "scheduler_reason": "new_item",
                "mastery": {"attempts": 0, "correct": 0, "incorrect": 0, "accuracy": None},
                "recency": {"last_seen_at": None, "age_seconds": None},
            },
        ],
    }


def test_incorrect_answer_records_event_and_prioritizes_weak_card() -> None:
    events = record_practice_answer(
        cards=CARDS,
        events=[],
        card_id="word:the",
        submitted_answer="de",
        now=NOW,
    )

    assert events == [
        {
            "card_id": "word:the",
            "card_type": "word",
            "submitted_answer": "de",
            "expected_answer": "te",
            "correct": False,
            "answered_at": "2026-05-23T12:00:00+00:00",
        }
    ]

    queue = build_practice_queue(cards=CARDS, events=events, now=NOW + timedelta(minutes=1), limit=2)

    assert queue["cards"][0]["id"] == "word:the"
    assert queue["cards"][0]["scheduler_reason"] == "weak_recent_performance"
    assert queue["cards"][0]["mastery"] == {
        "attempts": 1,
        "correct": 0,
        "incorrect": 1,
        "accuracy": 0.0,
    }


def test_weak_recent_performance_gates_new_items_until_reviewed() -> None:
    events = [
        {
            "card_id": "phrase:hello-world",
            "card_type": "phrase",
            "submitted_answer": "wrong",
            "expected_answer": "ha world",
            "correct": False,
            "answered_at": (NOW - timedelta(minutes=3)).isoformat(),
        },
        {
            "card_id": "word:the",
            "card_type": "word",
            "submitted_answer": "wrong",
            "expected_answer": "te",
            "correct": False,
            "answered_at": (NOW - timedelta(minutes=2)).isoformat(),
        },
    ]

    queue = build_practice_queue(cards=CARDS, events=events, now=NOW, limit=3)

    assert [card["scheduler_reason"] for card in queue["cards"]] == [
        "weak_recent_performance",
        "weak_recent_performance",
        "new_item_gated_by_weak_recent_performance",
    ]
    assert queue["cards"][2]["id"] in {"phrase:good-morning", "word:be"}


def test_stale_mastered_item_resurfaces_before_new_cards() -> None:
    old = NOW - timedelta(days=15)
    events = [
        {
            "card_id": "word:the",
            "card_type": "word",
            "submitted_answer": "te",
            "expected_answer": "te",
            "correct": True,
            "answered_at": old.isoformat(),
        },
        {
            "card_id": "word:the",
            "card_type": "word",
            "submitted_answer": "te",
            "expected_answer": "te",
            "correct": True,
            "answered_at": (old + timedelta(minutes=1)).isoformat(),
        },
    ]

    queue = build_practice_queue(cards=CARDS, events=events, now=NOW, limit=2)

    assert queue["cards"][0]["id"] == "word:the"
    assert queue["cards"][0]["scheduler_reason"] == "stale_mastered_review"
    assert queue["cards"][0]["recency"] == {
        "last_seen_at": "2026-05-08T12:01:00+00:00",
        "age_seconds": 1295940,
    }


def test_unknown_card_answer_is_structured_and_does_not_append_event() -> None:
    result = record_practice_answer(
        cards=CARDS,
        events=[],
        card_id="word:missing",
        submitted_answer="x",
        now=NOW,
    )

    assert result == {
        "ok": False,
        "error": "unknown_card",
        "phase": "practice_answer",
        "card_id": "word:missing",
        "event_count": 0,
        "detail": "Practice card was not found in the configured content source.",
    }


def test_empty_card_list_returns_empty_queue() -> None:
    queue = build_practice_queue(cards=[], events=[], now=NOW, limit=5)

    assert queue == {
        "ok": True,
        "phase": "practice_queue",
        "card_count": 0,
        "event_count": 0,
        "limit": 0,
        "cards": [],
    }


def test_malformed_events_are_ignored_without_blocking_valid_history() -> None:
    events = [
        {"card_id": "word:the", "correct": False},
        {"card_id": "word:be", "correct": True, "answered_at": "not-a-date"},
        {
            "card_id": "word:the",
            "card_type": "word",
            "submitted_answer": "te",
            "expected_answer": "te",
            "correct": True,
            "answered_at": NOW.isoformat(),
        },
    ]

    queue = build_practice_queue(cards=CARDS, events=events, now=NOW + timedelta(seconds=30), limit=1)

    assert queue["event_count"] == 1
    assert queue["cards"][0]["id"] == "phrase:hello-world"


def test_single_recent_event_has_zero_age_recency() -> None:
    events = record_practice_answer(
        cards=CARDS,
        events=[],
        card_id="word:be",
        submitted_answer="bi",
        now=NOW,
    )

    queue = build_practice_queue(cards=CARDS, events=events, now=NOW, limit=4)
    card = next(item for item in queue["cards"] if item["id"] == "word:be")

    assert card["recency"] == {"last_seen_at": "2026-05-23T12:00:00+00:00", "age_seconds": 0}
    assert card["scheduler_reason"] == "mastered_recent"


def test_session_history_is_trimmed_to_latest_200_events() -> None:
    events = []
    for index in range(MAX_EVENTS + 5):
        events.append(
            {
                "card_id": "word:the",
                "card_type": "word",
                "submitted_answer": "te",
                "expected_answer": "te",
                "correct": True,
                "answered_at": (NOW + timedelta(seconds=index)).isoformat(),
            }
        )

    result = record_practice_answer(
        cards=CARDS,
        events=events,
        card_id="word:be",
        submitted_answer="bi",
        now=NOW + timedelta(minutes=10),
    )

    assert isinstance(result, list)
    assert len(result) == MAX_EVENTS
    assert result[0]["answered_at"] == "2026-05-23T12:00:06+00:00"
    assert result[-1]["card_id"] == "word:be"
