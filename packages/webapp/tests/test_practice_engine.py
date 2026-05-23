from __future__ import annotations

from datetime import datetime, timedelta, timezone

from mirad_webapp.practice import MAX_EVENTS
from mirad_webapp.practice_engine import build_practice_progress, build_practice_queue, record_practice_answer


NOW = datetime(2026, 5, 23, 12, 0, tzinfo=timezone.utc)


CARDS = [
    {"id": "phrase:hello-world", "type": "phrase", "english": "hello world", "mirad": "ha world"},
    {"id": "phrase:good-morning", "type": "phrase", "english": "good morning", "mirad": "gud morgen"},
    {"id": "word:the", "type": "word", "english": "the", "mirad": "te"},
    {"id": "word:be", "type": "word", "english": "be", "mirad": "bi"},
]


def test_build_practice_queue_expands_words_and_phrases_into_both_directions() -> None:
    queue = build_practice_queue(cards=CARDS, events=[], now=NOW, limit=5)

    assert queue["ok"] is True
    assert queue["phase"] == "practice_queue"
    assert queue["card_count"] == 8
    assert queue["base_card_count"] == 4
    assert queue["event_count"] == 0
    assert queue["limit"] == 5
    assert [card["id"] for card in queue["cards"]] == [
        "phrase:hello-world#english-to-mirad",
        "phrase:hello-world#mirad-to-english",
        "word:the#english-to-mirad",
        "word:the#mirad-to-english",
        "phrase:good-morning#english-to-mirad",
    ]

    english_to_mirad = queue["cards"][0]
    assert english_to_mirad == {
        "id": "phrase:hello-world#english-to-mirad",
        "base_card_id": "phrase:hello-world",
        "audio_card_id": "phrase:hello-world",
        "type": "phrase",
        "direction": "english_to_mirad",
        "prompt_language": "english",
        "answer_language": "mirad",
        "prompt": "hello world",
        "answer": "ha world",
        "english_text": "hello world",
        "mirad_text": "ha world",
        "scheduler_reason": "new_item",
        "mastery": {"attempts": 0, "correct": 0, "incorrect": 0, "accuracy": None},
        "recency": {"last_seen_at": None, "age_seconds": None},
    }
    mirad_to_english = queue["cards"][1]
    assert mirad_to_english["direction"] == "mirad_to_english"
    assert mirad_to_english["prompt_language"] == "mirad"
    assert mirad_to_english["answer_language"] == "english"
    assert mirad_to_english["prompt"] == "ha world"
    assert mirad_to_english["answer"] == "hello world"


def test_incorrect_answer_records_direction_event_and_prioritizes_only_that_item() -> None:
    events = record_practice_answer(
        cards=CARDS,
        events=[],
        card_id="word:the#mirad-to-english",
        submitted_answer="wrong",
        now=NOW,
    )

    assert events == [
        {
            "card_id": "word:the#mirad-to-english",
            "base_card_id": "word:the",
            "direction": "mirad_to_english",
            "card_type": "word",
            "submitted_answer": "wrong",
            "expected_answer": "the",
            "correct": False,
            "answered_at": "2026-05-23T12:00:00+00:00",
        }
    ]

    queue = build_practice_queue(cards=CARDS, events=events, now=NOW + timedelta(minutes=1), limit=4)
    cards = {card["id"]: card for card in queue["cards"]}

    assert queue["cards"][0]["id"] == "word:the#mirad-to-english"
    assert cards["word:the#mirad-to-english"]["scheduler_reason"] == "weak_recent_performance"
    assert cards["word:the#mirad-to-english"]["mastery"] == {
        "attempts": 1,
        "correct": 0,
        "incorrect": 1,
        "accuracy": 0.0,
    }
    assert cards["word:the#english-to-mirad"]["scheduler_reason"] == "new_item_gated_by_weak_recent_performance"
    assert cards["word:the#english-to-mirad"]["mastery"]["attempts"] == 0


def test_mirad_to_english_exact_answer_comparison_uses_english_expected_answer() -> None:
    correct = record_practice_answer(
        cards=CARDS,
        events=[],
        card_id="phrase:hello-world#mirad-to-english",
        submitted_answer="hello world",
        now=NOW,
    )
    incorrect = record_practice_answer(
        cards=CARDS,
        events=[],
        card_id="phrase:hello-world#mirad-to-english",
        submitted_answer="ha world",
        now=NOW,
    )

    assert isinstance(correct, list)
    assert correct[-1]["expected_answer"] == "hello world"
    assert correct[-1]["correct"] is True
    assert isinstance(incorrect, list)
    assert incorrect[-1]["correct"] is False


def test_weak_recent_performance_gates_new_direction_items_until_reviewed() -> None:
    events = [
        {
            "card_id": "phrase:hello-world#english-to-mirad",
            "base_card_id": "phrase:hello-world",
            "direction": "english_to_mirad",
            "card_type": "phrase",
            "submitted_answer": "wrong",
            "expected_answer": "ha world",
            "correct": False,
            "answered_at": (NOW - timedelta(minutes=3)).isoformat(),
        },
        {
            "card_id": "word:the#mirad-to-english",
            "base_card_id": "word:the",
            "direction": "mirad_to_english",
            "card_type": "word",
            "submitted_answer": "wrong",
            "expected_answer": "the",
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
    assert queue["cards"][2]["id"] not in {"phrase:hello-world#english-to-mirad", "word:the#mirad-to-english"}


def test_stale_mastered_item_resurfaces_before_new_cards() -> None:
    old = NOW - timedelta(days=15)
    events = [
        {
            "card_id": "word:the#english-to-mirad",
            "base_card_id": "word:the",
            "direction": "english_to_mirad",
            "card_type": "word",
            "submitted_answer": "te",
            "expected_answer": "te",
            "correct": True,
            "answered_at": old.isoformat(),
        },
        {
            "card_id": "word:the#english-to-mirad",
            "base_card_id": "word:the",
            "direction": "english_to_mirad",
            "card_type": "word",
            "submitted_answer": "te",
            "expected_answer": "te",
            "correct": True,
            "answered_at": (old + timedelta(minutes=1)).isoformat(),
        },
    ]

    queue = build_practice_queue(cards=CARDS, events=events, now=NOW, limit=2)

    assert queue["cards"][0]["id"] == "word:the#english-to-mirad"
    assert queue["cards"][0]["scheduler_reason"] == "stale_mastered_review"
    assert queue["cards"][0]["recency"] == {
        "last_seen_at": "2026-05-08T12:01:00+00:00",
        "age_seconds": 1295940,
    }


def test_unknown_direction_card_answer_is_structured_and_does_not_append_event() -> None:
    result = record_practice_answer(
        cards=CARDS,
        events=[],
        card_id="word:the#bad-direction",
        submitted_answer="x",
        now=NOW,
    )

    assert result == {
        "ok": False,
        "error": "unknown_card",
        "phase": "practice_answer",
        "card_id": "word:the#bad-direction",
        "event_count": 0,
        "detail": "Practice card was not found in the configured content source.",
    }


def test_legacy_base_card_id_answers_remain_supported_as_english_to_mirad() -> None:
    result = record_practice_answer(cards=CARDS, events=[], card_id="word:the", submitted_answer="te", now=NOW)

    assert isinstance(result, list)
    assert result[-1]["card_id"] == "word:the#english-to-mirad"
    assert result[-1]["direction"] == "english_to_mirad"
    assert result[-1]["correct"] is True


def test_empty_card_list_returns_empty_queue() -> None:
    queue = build_practice_queue(cards=[], events=[], now=NOW, limit=5)

    assert queue == {
        "ok": True,
        "phase": "practice_queue",
        "card_count": 0,
        "base_card_count": 0,
        "event_count": 0,
        "limit": 0,
        "cards": [],
    }


def test_cards_missing_english_or_mirad_do_not_create_unusable_direction_items() -> None:
    queue = build_practice_queue(
        cards=[
            {"id": "word:ok", "type": "word", "english": "ok", "mirad": "oke"},
            {"id": "word:missing-english", "type": "word", "english": "", "mirad": "x"},
            {"id": "word:missing-mirad", "type": "word", "english": "x", "mirad": ""},
        ],
        events=[],
        now=NOW,
        limit=10,
    )

    assert queue["card_count"] == 2
    assert {card["id"] for card in queue["cards"]} == {"word:ok#english-to-mirad", "word:ok#mirad-to-english"}


def test_malformed_and_legacy_events_are_ignored_or_normalized_without_crashing() -> None:
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
    progress = build_practice_progress(cards=CARDS, events=events, now=NOW + timedelta(seconds=30))

    assert queue["event_count"] == 1
    assert progress["latest_event"]["card_id"] == "word:the#english-to-mirad"
    assert progress["latest_event"]["direction"] == "english_to_mirad"


def test_single_recent_event_has_zero_age_recency() -> None:
    events = record_practice_answer(
        cards=CARDS,
        events=[],
        card_id="word:be#english-to-mirad",
        submitted_answer="bi",
        now=NOW,
    )

    queue = build_practice_queue(cards=CARDS, events=events, now=NOW, limit=8)
    card = next(item for item in queue["cards"] if item["id"] == "word:be#english-to-mirad")

    assert card["recency"] == {"last_seen_at": "2026-05-23T12:00:00+00:00", "age_seconds": 0}
    assert card["scheduler_reason"] == "mastered_recent"


def test_session_history_is_trimmed_to_latest_200_events() -> None:
    events = []
    for index in range(MAX_EVENTS + 5):
        events.append(
            {
                "card_id": "word:the#english-to-mirad",
                "base_card_id": "word:the",
                "direction": "english_to_mirad",
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
        card_id="word:be#english-to-mirad",
        submitted_answer="bi",
        now=NOW + timedelta(minutes=10),
    )

    assert isinstance(result, list)
    assert len(result) == MAX_EVENTS
    assert result[0]["answered_at"] == "2026-05-23T12:00:06+00:00"
    assert result[-1]["card_id"] == "word:be#english-to-mirad"
