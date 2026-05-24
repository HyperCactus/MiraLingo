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
    assert queue["mode"] == "mixed"
    assert queue["mode_detail"] == "default_mixed"
    assert queue["repeat_gap"] == 10
    assert queue["repeat_gap_satisfied"] is False
    assert queue["card_count"] == 8
    assert queue["base_card_count"] == 4
    assert queue["event_count"] == 0
    assert queue["limit"] == 5
    assert [card["id"] for card in queue["cards"]] == [
        "phrase:hello-world#english-to-mirad",
        "word:the#english-to-mirad",
        "phrase:good-morning#english-to-mirad",
        "word:be#english-to-mirad",
        "phrase:hello-world#mirad-to-english",
    ]
    assert [card["base_card_id"] for card in queue["cards"][:4]] == [
        "phrase:hello-world",
        "word:the",
        "phrase:good-morning",
        "word:be",
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
    mirad_to_english = next(card for card in queue["cards"] if card["id"] == "phrase:hello-world#mirad-to-english")
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
    assert [card["base_card_id"] for card in queue["cards"]] == [
        "word:the",
        "phrase:hello-world",
        "word:be",
        "phrase:good-morning",
    ]
    assert cards["word:the#mirad-to-english"]["scheduler_reason"] == "weak_recent_performance"
    assert cards["word:the#mirad-to-english"]["mastery"] == {
        "attempts": 1,
        "correct": 0,
        "incorrect": 1,
        "accuracy": 0.0,
    }
    full_queue = build_practice_queue(cards=CARDS, events=events, now=NOW + timedelta(minutes=1), limit=8)
    full_cards = {card["id"]: card for card in full_queue["cards"]}
    assert full_cards["word:the#english-to-mirad"]["scheduler_reason"] == "new_item_gated_by_weak_recent_performance"
    assert full_cards["word:the#english-to-mirad"]["mastery"]["attempts"] == 0


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
        "mode": "mixed",
        "mode_detail": "empty_pool",
        "repeat_gap": 10,
        "repeat_gap_satisfied": False,
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


def _mode_cards() -> list[dict[str, str]]:
    return [
        {"id": "phrase:greeting", "type": "phrase", "english": "good day", "mirad": "gud dey"},
        {"id": "word:alpha", "type": "word", "english": "alpha", "mirad": "alfa"},
        {"id": "word:bravo", "type": "word", "english": "bravo", "mirad": "brava"},
        {"id": "word:charlie", "type": "word", "english": "charlie", "mirad": "charli"},
        {"id": "word:delta", "type": "word", "english": "delta", "mirad": "delta"},
    ]


def _repeat_gap_cards(count: int) -> list[dict[str, str]]:
    return [
        {
            "id": f"word:{index:02d}",
            "type": "word",
            "english": f"english {index:02d}",
            "mirad": f"mirad {index:02d}",
        }
        for index in range(1, count + 1)
    ]


def _event(
    card_id: str,
    *,
    correct: bool,
    answered_at: datetime,
    base_card_id: str | None = None,
    direction: str | None = None,
    card_type: str = "word",
    submitted_answer: str = "x",
    expected_answer: str = "x",
) -> dict[str, object]:
    resolved_direction = direction or card_id.rsplit("#", maxsplit=1)[1].replace("-", "_")
    resolved_base_card_id = base_card_id or card_id.split("#", maxsplit=1)[0]
    return {
        "card_id": card_id,
        "base_card_id": resolved_base_card_id,
        "direction": resolved_direction,
        "card_type": card_type,
        "submitted_answer": submitted_answer,
        "expected_answer": expected_answer,
        "correct": correct,
        "answered_at": answered_at.isoformat(),
    }


def test_build_practice_queue_default_mode_reports_mode_and_repeat_gap_diagnostics() -> None:
    cards = _mode_cards()
    events = [
        _event(
            "word:alpha#english-to-mirad",
            correct=True,
            answered_at=NOW - timedelta(days=20),
            expected_answer="alfa",
            submitted_answer="alfa",
        ),
        _event(
            "word:alpha#english-to-mirad",
            correct=True,
            answered_at=NOW - timedelta(days=19, minutes=59),
            expected_answer="alfa",
            submitted_answer="alfa",
        ),
        _event(
            "word:bravo#english-to-mirad",
            correct=False,
            answered_at=NOW - timedelta(minutes=5),
            expected_answer="brava",
            submitted_answer="wrong",
        ),
    ]

    queue = build_practice_queue(cards=cards, events=events, now=NOW, limit=6, mode="mixed")

    assert queue["ok"] is True
    assert queue["phase"] == "practice_queue"
    assert queue["mode"] == "mixed"
    assert queue["mode_detail"] == "default_mixed"
    assert queue["repeat_gap"] == 10
    assert queue["repeat_gap_satisfied"] is False
    assert queue["base_card_count"] == 5
    assert queue["card_count"] == 10
    assert queue["event_count"] == 3
    assert queue["cards"][0]["id"] == "word:bravo#english-to-mirad"
    assert queue["cards"][0]["scheduler_reason"] == "weak_recent_performance"
    assert queue["cards"][1]["id"] == "word:alpha#english-to-mirad"
    assert queue["cards"][1]["scheduler_reason"] == "stale_mastered_review"


def test_revision_mode_returns_only_stale_mastered_review_items() -> None:
    cards = _mode_cards()
    events = [
        _event(
            "word:alpha#english-to-mirad",
            correct=True,
            answered_at=NOW - timedelta(days=20),
            expected_answer="alfa",
            submitted_answer="alfa",
        ),
        _event(
            "word:alpha#english-to-mirad",
            correct=True,
            answered_at=NOW - timedelta(days=19, minutes=59),
            expected_answer="alfa",
            submitted_answer="alfa",
        ),
        _event(
            "word:bravo#english-to-mirad",
            correct=False,
            answered_at=NOW - timedelta(minutes=5),
            expected_answer="brava",
            submitted_answer="wrong",
        ),
    ]

    queue = build_practice_queue(cards=cards, events=events, now=NOW, limit=10, mode="revision")

    assert queue["mode"] == "revision"
    assert queue["mode_detail"] == "stale_only"
    assert queue["event_count"] == 3
    assert queue["cards"]
    assert {card["scheduler_reason"] for card in queue["cards"]} == {"stale_mastered_review"}
    assert {card["id"] for card in queue["cards"]} == {"word:alpha#english-to-mirad"}


def test_build_vocabulary_mode_returns_only_new_word_items_without_prior_events() -> None:
    cards = _mode_cards()
    events = [
        _event(
            "word:charlie#english-to-mirad",
            correct=True,
            answered_at=NOW - timedelta(hours=2),
            expected_answer="charli",
            submitted_answer="charli",
        ),
        _event(
            "phrase:greeting#english-to-mirad",
            correct=False,
            answered_at=NOW - timedelta(hours=1),
            base_card_id="phrase:greeting",
            card_type="phrase",
            expected_answer="gud dey",
            submitted_answer="wrong",
        ),
    ]

    queue = build_practice_queue(cards=cards, events=events, now=NOW, limit=10, mode="build_vocabulary")

    assert queue["mode"] == "build_vocabulary"
    assert queue["mode_detail"] == "new_words_only"
    assert queue["cards"]
    assert {card["type"] for card in queue["cards"]} == {"word"}
    assert {card["scheduler_reason"] for card in queue["cards"]} == {"new_item"}
    assert {card["base_card_id"] for card in queue["cards"]} == {"word:alpha", "word:bravo", "word:delta"}
    assert all(card["base_card_id"] != "word:charlie" for card in queue["cards"])
    assert all(card["base_card_id"] != "phrase:greeting" for card in queue["cards"])


def test_mixed_mode_avoids_repeating_base_card_before_ten_others_when_pool_allows() -> None:
    cards = _repeat_gap_cards(11)

    queue = build_practice_queue(cards=cards, events=[], now=NOW, limit=22, mode="mixed")

    base_card_ids = [card["base_card_id"] for card in queue["cards"]]
    first_base_ids = base_card_ids[:11]

    assert queue["mode"] == "mixed"
    assert queue["repeat_gap"] == 10
    assert queue["repeat_gap_satisfied"] is True
    assert len(first_base_ids) == 11
    assert len(set(first_base_ids)) == 11
    for index, base_card_id in enumerate(base_card_ids):
        later_positions = [later for later in range(index + 1, len(base_card_ids)) if base_card_ids[later] == base_card_id]
        if later_positions:
            assert later_positions[0] - index > 10


def test_empty_pool_in_mode_reports_repeat_gap_fallback_without_crashing() -> None:
    queue = build_practice_queue(cards=[], events=[], now=NOW, limit=5, mode="revision")

    assert queue == {
        "ok": True,
        "phase": "practice_queue",
        "mode": "revision",
        "mode_detail": "empty_pool",
        "repeat_gap": 10,
        "repeat_gap_satisfied": False,
        "card_count": 0,
        "base_card_count": 0,
        "event_count": 0,
        "limit": 0,
        "cards": [],
    }


def test_small_pool_reports_repeat_gap_unsatisfied_but_still_returns_queue() -> None:
    cards = _repeat_gap_cards(3)

    queue = build_practice_queue(cards=cards, events=[], now=NOW, limit=6, mode="mixed")

    assert queue["mode"] == "mixed"
    assert queue["mode_detail"] == "default_mixed"
    assert queue["repeat_gap"] == 10
    assert queue["repeat_gap_satisfied"] is False
    assert queue["cards"]
    assert [card["base_card_id"] for card in queue["cards"][:3]] == ["word:01", "word:02", "word:03"]
