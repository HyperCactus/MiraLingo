from __future__ import annotations

from datetime import datetime, timedelta, timezone

from mirad_webapp.practice import MAX_EVENTS
from mirad_webapp.practice_engine import _achievement_milestones_up_to, _expected_answer_alternatives, _mastered_card_probability_weights, _mastered_item_ids_from_lifecycle, _new_card_weight, build_practice_achievements, build_practice_progress, build_practice_queue, record_practice_answer


NOW = datetime(2026, 5, 23, 12, 0, tzinfo=timezone.utc)


CARDS = [
    {"id": "phrase:hello-world", "type": "phrase", "english": "hello world", "mirad": "ha world"},
    {"id": "phrase:good-morning", "type": "phrase", "english": "good morning", "mirad": "gud morgen"},
    {"id": "word:the", "type": "word", "english": "the", "mirad": "te"},
    {"id": "word:be", "type": "word", "english": "be", "mirad": "bi"},
]


def test_build_practice_queue_selects_one_direction_per_base_pair() -> None:
    queue = build_practice_queue(cards=CARDS, events=[], now=NOW, limit=5)

    assert queue["ok"] is True
    assert queue["phase"] == "practice_queue"
    assert queue["mode"] == "mixed"
    assert queue["mode_detail"] == "default_mixed"
    assert queue["repeat_gap"] == 3
    assert queue["repeat_gap_satisfied"] is True
    assert queue["card_count"] == 4
    assert queue["base_card_count"] == 4
    assert queue["event_count"] == 0
    assert queue["limit"] == 4
    assert len(queue["cards"]) == 4
    assert len({card["base_card_id"] for card in queue["cards"][:4]}) == 4
    assert all(card["scheduler_reason"] == "new_item" for card in queue["cards"])

    e2m_card = next(card for card in queue["cards"] if card["direction"] == "english_to_mirad")
    assert e2m_card["audio_card_id"] == e2m_card["base_card_id"]
    assert e2m_card["prompt_language"] == "english"
    assert e2m_card["answer_language"] == "mirad"
    assert e2m_card["mastery"] == {"attempts": 0, "correct": 0, "incorrect": 0, "accuracy": None, "consecutive_correct": 0, "streak_required": 3, "mastered": False}
    assert e2m_card["recency"] == {"last_seen_at": None, "age_seconds": None}

    m2e_card = next(card for card in queue["cards"] if card["direction"] == "mirad_to_english")
    assert m2e_card["prompt_language"] == "mirad"
    assert m2e_card["answer_language"] == "english"


def test_incorrect_answer_records_direction_event_and_prioritizes_base_pair_with_opposite_direction_bias() -> None:
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

    assert queue["cards"][0]["base_card_id"] == "word:the"
    assert queue["cards"][0]["id"] == "word:the#english-to-mirad"
    assert cards["word:the#english-to-mirad"]["scheduler_reason"] == "weak_recent_performance"
    assert cards["word:the#english-to-mirad"]["mastery"] == {
        "attempts": 0,
        "correct": 0,
        "incorrect": 0,
        "accuracy": None,
        "consecutive_correct": 0,
        "streak_required": 3,
        "mastered": False,
    }
    assert all(card["scheduler_reason"] in {"new_item", "new_item_gated_by_weak_recent_performance"} for card in queue["cards"][1:])


def test_word_prompt_uses_single_random_variant_from_comma_separated_options() -> None:
    cards = [{"id": "word:but", "type": "word", "english": "but", "mirad": "boy, oy"}]

    queue = build_practice_queue(cards=cards, events=[], now=NOW, limit=1)

    assert queue["cards"]
    card = queue["cards"][0]
    assert card["prompt"] in {"but", "boy", "oy"}
    assert "," not in card["prompt"]
    if card["direction"] == "english_to_mirad":
        assert card["prompt"] == "but"
        assert card["answer"] == "boy, oy"
    else:
        assert card["prompt"] in {"boy", "oy"}
        assert card["answer"] == "but"
def test_mirad_to_english_word_answers_require_exact_card_translation_not_lexicon_union(monkeypatch) -> None:
    monkeypatch.setitem(
        record_practice_answer.__globals__,
        "lookup_mirad_word_candidates",
        lambda *, mirad_word=None, db_path=None: ["am", "are", "is"] if mirad_word == "se" else [],
    )

    result = record_practice_answer(
        cards=[{"id": "word:are", "type": "word", "english": "are", "mirad": "se"}],
        events=[],
        card_id="word:are#mirad-to-english",
        submitted_answer="is",
        now=NOW,
    )

    assert isinstance(result, list)
    assert result[-1]["expected_answer"] == "are"
    assert result[-1]["correct"] is False


def test_mirad_to_english_word_accepts_peer_cards_with_same_mirad_as_alternatives() -> None:
    cards = [
        {"id": "word:is", "type": "word", "english": "is", "mirad": "se"},
        {"id": "word:are", "type": "word", "english": "are", "mirad": "se"},
    ]

    progress = build_practice_progress(cards=cards, events=[], now=NOW)
    mirad_to_english = [card for card in progress["per_card"] if card["direction"] == "mirad_to_english"]
    assert {card["answer"] for card in mirad_to_english} == {"is, are"}

    for card_id in ["word:is#mirad-to-english", "word:are#mirad-to-english"]:
        for submitted in ["is", "are"]:
            result = record_practice_answer(
                cards=cards,
                events=[],
                card_id=card_id,
                submitted_answer=submitted,
                now=NOW,
            )

            assert isinstance(result, list)
            assert result[-1]["expected_answer"] == "is, are"
            assert result[-1]["correct"] is True


def test_word_practice_items_expose_multiple_inverse_ids_for_same_mirad() -> None:
    cards = [
        {"id": "word:is", "type": "word", "english": "is", "mirad": "se"},
        {"id": "word:are", "type": "word", "english": "are", "mirad": "se"},
    ]

    progress = build_practice_progress(cards=cards, events=[], now=NOW)
    by_id = {card["id"]: card for card in progress["per_card"]}

    assert by_id["word:is#mirad-to-english"]["inverse_item_ids"] == [
        "word:are#english-to-mirad",
        "word:is#english-to-mirad",
    ]
    assert by_id["word:are#english-to-mirad"]["inverse_item_ids"] == [
        "word:are#mirad-to-english",
        "word:is#mirad-to-english",
    ]


def test_new_card_weight_triples_when_inverse_is_active_or_mastered() -> None:
    item = {
        "id": "word:are#english-to-mirad",
        "english_text": "are",
        "inverse_item_ids": ["word:are#mirad-to-english", "word:is#mirad-to-english"],
    }
    card = {"id": "word:are", "english": "are", "mirad": "se"}

    base_weight = _new_card_weight(item, card, related_bases=set(), related_item_ids=set())
    inverse_weight = _new_card_weight(item, card, related_bases=set(), related_item_ids={"word:is#mirad-to-english"})

    assert inverse_weight == base_weight * 3


def test_mirad_to_english_word_accepts_same_row_follow_up_english_alternatives() -> None:
    cards = [
        {
            "id": "word:are-se",
            "type": "word",
            "english": "are",
            "mirad": "se",
            "follow_up_english": "am, are, is",
            "follow_up_mirad": "se",
        }
    ]

    progress = build_practice_progress(cards=cards, events=[], now=NOW)
    mirad_to_english = next(card for card in progress["per_card"] if card["direction"] == "mirad_to_english")
    assert mirad_to_english["prompt"] == "se"
    assert mirad_to_english["answer"] == "am, are, is"

    for submitted in ["am", "are", "is"]:
        result = record_practice_answer(
            cards=cards,
            events=[],
            card_id="word:are-se#mirad-to-english",
            submitted_answer=submitted,
            now=NOW,
        )

        assert isinstance(result, list)
        assert result[-1]["expected_answer"] == "am, are, is"
        assert result[-1]["correct"] is True


def test_imported_module_reverse_card_accepts_all_follow_up_english_without_hijacking_general_am() -> None:
    cards = [
        {
            "id": "word:is-se",
            "type": "word",
            "english": "is",
            "mirad": "se",
            "follow_up_english": "is, are",
            "beginner_order": "6",
        },
        {"id": "word:is", "type": "word", "english": "is", "mirad": "se", "beginner_order": "6", "english_to_mirad_only": True},
        {"id": "word:are", "type": "word", "english": "are", "mirad": "se", "beginner_order": "6", "english_to_mirad_only": True},
        {"id": "word:am", "type": "word", "english": "am", "mirad": "amilk"},
    ]

    reverse = record_practice_answer(
        cards=cards,
        events=[],
        card_id="word:is-se#mirad-to-english",
        submitted_answer="is",
        now=NOW,
    )
    forward = record_practice_answer(
        cards=cards,
        events=[],
        card_id="word:am#english-to-mirad",
        submitted_answer="amilk",
        now=NOW,
    )
    progress = build_practice_progress(cards=cards, events=[], now=NOW)
    by_id = {item["id"]: item for item in progress["per_card"]}

    assert isinstance(reverse, list)
    assert reverse[-1]["expected_answer"] == "is, are"
    assert reverse[-1]["correct"] is True
    assert isinstance(forward, list)
    assert forward[-1]["expected_answer"] == "amilk"
    assert forward[-1]["correct"] is True
    assert by_id["word:am#english-to-mirad"]["answer"] == "amilk"
    assert by_id["word:is-se#english-to-mirad"]["answer"] == "se"


def test_module_expanded_comma_english_cards_have_two_forward_prompts_and_one_reverse_prompt() -> None:
    cards = [
        {
            "id": "word:is-se",
            "type": "word",
            "english": "is",
            "mirad": "se",
            "follow_up_english": "is, are",
            "beginner_order": "0",
        },
        {"id": "word:are", "type": "word", "english": "are", "mirad": "se", "beginner_order": "0", "english_to_mirad_only": True},
    ]

    progress = build_practice_progress(cards=cards, events=[], now=NOW)
    items = progress["per_card"]

    english_to_mirad = [card for card in items if card["direction"] == "english_to_mirad"]
    mirad_to_english = [card for card in items if card["direction"] == "mirad_to_english"]
    assert {card["prompt"] for card in english_to_mirad} == {"is", "are"}
    assert {card["answer"] for card in english_to_mirad} == {"se"}
    assert len(mirad_to_english) == 1
    assert mirad_to_english[0]["prompt"] == "se"
    assert mirad_to_english[0]["answer"] == "is, are"

    for submitted in ["is", "are"]:
        result = record_practice_answer(
            cards=cards,
            events=[],
            card_id="word:is-se#mirad-to-english",
            submitted_answer=submitted,
            now=NOW,
        )
        assert isinstance(result, list)
        assert result[-1]["correct"] is True


def test_english_to_mirad_word_accepts_comma_separated_mirad_alternatives_from_beginner_module() -> None:
    cards = [
        {
            "id": "word:come",
            "type": "word",
            "english": "come",
            "mirad": "uper,upu,upya",
            "beginner_order": "35",
        },
        {
            "id": "word:come",
            "type": "word",
            "english": "come",
            "mirad": "upya",
        },
    ]

    progress = build_practice_progress(cards=cards, events=[], now=NOW)
    english_to_mirad = next(card for card in progress["per_card"] if card["direction"] == "english_to_mirad")
    assert english_to_mirad["prompt"] == "come"
    assert english_to_mirad["answer"] == "uper,upu,upya"

    for submitted in ["uper", "upu", "upya"]:
        result = record_practice_answer(
            cards=cards,
            events=[],
            card_id="word:come#english-to-mirad",
            submitted_answer=submitted,
            now=NOW,
        )

        assert isinstance(result, list)
        assert result[-1]["expected_answer"] == "uper,upu,upya"
        assert result[-1]["correct"] is True


def test_english_to_mirad_word_answers_require_exact_card_translation_not_lexicon_union(monkeypatch) -> None:
    monkeypatch.setitem(
        record_practice_answer.__globals__,
        "lookup_word_candidates",
        lambda *, english_word=None, db_path=None: ["hat", "hit", "hut", "hwat", "hwit", "hwut", "it", "wit"] if english_word == "he" else [],
    )

    result = record_practice_answer(
        cards=[{"id": "word:he", "type": "word", "english": "he", "mirad": "it"}],
        events=[],
        card_id="word:he#english-to-mirad",
        submitted_answer="wit",
        now=NOW,
    )

    assert isinstance(result, list)
    assert result[-1]["expected_answer"] == "it"
    assert result[-1]["correct"] is False


def test_scheduler_marks_card_mastered_after_three_streak_and_accuracy_at_threshold_despite_past_misses() -> None:
    events = [
        {
            "card_id": "word:the#english-to-mirad",
            "base_card_id": "word:the",
            "direction": "english_to_mirad",
            "card_type": "word",
            "submitted_answer": "wrong",
            "expected_answer": "te",
            "correct": False,
            "answered_at": (NOW + timedelta(minutes=0)).isoformat(),
        },
        {
            "card_id": "word:the#english-to-mirad",
            "base_card_id": "word:the",
            "direction": "english_to_mirad",
            "card_type": "word",
            "submitted_answer": "wrong",
            "expected_answer": "te",
            "correct": False,
            "answered_at": (NOW + timedelta(minutes=1)).isoformat(),
        },
        {
            "card_id": "word:the#english-to-mirad",
            "base_card_id": "word:the",
            "direction": "english_to_mirad",
            "card_type": "word",
            "submitted_answer": "te",
            "expected_answer": "te",
            "correct": True,
            "answered_at": (NOW + timedelta(minutes=2)).isoformat(),
        },
        {
            "card_id": "word:the#english-to-mirad",
            "base_card_id": "word:the",
            "direction": "english_to_mirad",
            "card_type": "word",
            "submitted_answer": "te",
            "expected_answer": "te",
            "correct": True,
            "answered_at": (NOW + timedelta(minutes=3)).isoformat(),
        },
        {
            "card_id": "word:the#english-to-mirad",
            "base_card_id": "word:the",
            "direction": "english_to_mirad",
            "card_type": "word",
            "submitted_answer": "te",
            "expected_answer": "te",
            "correct": True,
            "answered_at": (NOW + timedelta(minutes=4)).isoformat(),
        },
    ]

    progress = build_practice_progress(cards=CARDS, events=events, now=NOW + timedelta(minutes=5))
    card = next(item for item in progress["per_card"] if item["id"] == "word:the#english-to-mirad")

    assert card["mastery"] == {
        "attempts": 5,
        "correct": 3,
        "incorrect": 2,
        "accuracy": 0.6,
        "consecutive_correct": 3,
        "streak_required": 3,
        "mastered": True,
    }
    assert card["scheduler_reason"] == "mastered_recent"


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


def test_mirad_to_english_prompt_variant_answers_do_not_accept_reverse_lexicon_union(monkeypatch) -> None:
    monkeypatch.setitem(
        record_practice_answer.__globals__,
        "lookup_mirad_word_candidates",
        lambda *, mirad_word=None, db_path=None: ["that", "who", "whom"] if mirad_word == "ho" else [],
    )

    alternatives = _expected_answer_alternatives(
        {
            "type": "word",
            "direction": "mirad_to_english",
            "prompt": "ho",
            "answer": "who",
            "english_text": "who",
            "mirad_text": "hati, ho, hoti, hwot",
        }
    )

    assert alternatives == {"who"}


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

    assert any(card["scheduler_reason"] == "weak_recent_performance" for card in queue["cards"])
    assert any(card["scheduler_reason"] in {"new_item", "new_item_gated_by_weak_recent_performance"} for card in queue["cards"])
    assert queue["cards"][2]["id"] not in {"phrase:hello-world#english-to-mirad", "word:the#mirad-to-english"}


def test_stale_mastered_item_resurfaces_before_new_cards() -> None:
    old = NOW - timedelta(days=15)
    events = _correct_streak(
        "word:the#english-to-mirad",
        start=old,
        expected_answer="te",
        submitted_answer="te",
    )

    queue = build_practice_queue(cards=CARDS, events=events, now=NOW, limit=5)

    assert any(card["base_card_id"] == "word:the" and card["scheduler_reason"] == "stale_mastered_review" for card in queue["cards"])
    stale = next(card for card in queue["cards"] if card["base_card_id"] == "word:the")
    assert stale["recency"] == {
        "last_seen_at": None,
        "age_seconds": None,
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
        "repeat_gap": 3,
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

    assert queue["card_count"] == 1
    assert len(queue["cards"]) == 1
    assert {card["base_card_id"] for card in queue["cards"]} == {"word:ok"}


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
    card = next(item for item in queue["cards"] if item["base_card_id"] == "word:be")

    assert card["scheduler_reason"] == "new_item"
    assert card["direction"] == "mirad_to_english"


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


def _correct_streak(card_id: str, *, count: int = 5, start: datetime, expected_answer: str, submitted_answer: str) -> list[dict[str, object]]:
    return [
        _event(
            card_id,
            correct=True,
            answered_at=start + timedelta(minutes=index),
            expected_answer=expected_answer,
            submitted_answer=submitted_answer,
        )
        for index in range(count)
    ]


def test_build_practice_queue_default_mode_reports_mode_and_repeat_gap_diagnostics() -> None:
    cards = _mode_cards()
    events = [
        *_correct_streak(
            "word:alpha#english-to-mirad",
            start=NOW - timedelta(days=20),
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
    assert queue["repeat_gap"] == 3
    assert queue["repeat_gap_satisfied"] is True

    assert queue["card_count"] == 5
    assert queue["event_count"] == 6
    reasons_by_base = {card["base_card_id"]: card["scheduler_reason"] for card in queue["cards"]}
    assert reasons_by_base["word:bravo"] == "weak_recent_performance"
    assert reasons_by_base["word:alpha"] == "stale_mastered_review"


def test_revision_mode_returns_only_stale_mastered_review_items() -> None:
    cards = _mode_cards()
    events = [
        *_correct_streak(
            "word:alpha#english-to-mirad",
            start=NOW - timedelta(days=20),
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
    assert queue["mode_detail"] == "seen_only"
    assert queue["event_count"] == 6
    assert queue["cards"]
    assert {card["scheduler_reason"] for card in queue["cards"]}.issubset({"stale_mastered_review", "mastered_recent"})
    assert {card["base_card_id"] for card in queue["cards"]} == {"word:alpha"}


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
    assert {card["scheduler_reason"] for card in queue["cards"]}.issubset({"new_item", "new_item_gated_by_weak_recent_performance"})
    assert {card["base_card_id"] for card in queue["cards"]}.issubset({"word:alpha", "word:bravo", "word:charlie", "word:delta"})
    assert all(card["base_card_id"] != "phrase:greeting" for card in queue["cards"])


def test_mixed_mode_fills_active_deck_from_unseen_beginner_items_before_general_unseen_pool() -> None:
    cards = [
        {"id": "word:later-common", "type": "word", "english": "the", "mirad": "te"},
        {"id": "word:beginner-first", "type": "word", "english": "hello", "mirad": "hay", "beginner_order": "0"},
        {"id": "phrase:beginner-second", "type": "phrase", "english": "good morning", "mirad": "gud morgen", "beginner_order": "1"},
        {"id": "word:beginner-third", "type": "word", "english": "yes", "mirad": "va", "beginner_order": "2"},
    ]

    queue = build_practice_queue(cards=cards, events=[], now=NOW, limit=5, mode="mixed")

    assert queue["cards"]
    assert all(card.get("beginner_order") is not None for card in queue["cards"][:5])
    assert all(card["base_card_id"] != "word:later-common" for card in queue["cards"][:5])
    assert len({card["id"] for card in queue["cards"][:5]}) >= 3


def test_mixed_mode_caps_unmastered_active_rotation_without_backfilling_mastered_slots() -> None:
    cards = [
        {"id": f"word:card-{index}", "type": "word", "english": f"word{index}", "mirad": f"mir{index}", "beginner_order": str(index)}
        for index in range(10)
    ]

    queue = build_practice_queue(cards=cards, events=[], now=NOW, limit=10, mode="mixed")

    assert queue["limit"] == 10
    assert len(queue["cards"]) == 10
    assert len({card["id"] for card in queue["cards"]}) == 10
    assert {card["scheduler_reason"] for card in queue["cards"]} == {"new_item"}


def test_mixed_mode_uses_eighty_twenty_active_mastered_split_when_both_pools_exist() -> None:
    cards = [
        {"id": f"word:active-{index}", "type": "word", "english": f"active {index}", "mirad": f"aktiva {index}"}
        for index in range(8)
    ] + [
        {"id": f"word:mastered-{index}", "type": "word", "english": f"mastered {index}", "mirad": f"mastra {index}"}
        for index in range(5)
    ]
    events: list[dict[str, object]] = []
    for index in range(8):
        events.append(
            _event(
                f"word:active-{index}#english-to-mirad",
                correct=True,
                answered_at=NOW - timedelta(hours=2, minutes=index),
                expected_answer=f"aktiva {index}",
                submitted_answer=f"aktiva {index}",
            )
        )
    for index in range(5):
        events.extend(
            _correct_streak(
                f"word:mastered-{index}#english-to-mirad",
                count=3,
                start=NOW - timedelta(days=1, minutes=index * 6),
                expected_answer=f"mastra {index}",
                submitted_answer=f"mastra {index}",
            )
        )
        events.extend(
            _correct_streak(
                f"word:mastered-{index}#mirad-to-english",
                count=3,
                start=NOW - timedelta(days=1, minutes=index * 6 + 3),
                expected_answer=f"mastered {index}",
                submitted_answer=f"mastered {index}",
            )
        )

    queue = build_practice_queue(cards=cards, events=events, now=NOW, limit=10, mode="mixed")

    active_cards = [card for card in queue["cards"] if card["scheduler_reason"] not in {"mastered_recent", "stale_mastered_review"}]
    mastered_cards = [card for card in queue["cards"] if card["scheduler_reason"] in {"mastered_recent", "stale_mastered_review"}]
    assert len(active_cards) == 8
    assert len(mastered_cards) == 2


def test_mastered_card_probability_weights_keep_floor_and_bias_low_accuracy_low_seen() -> None:
    items = [
        {"id": "word:low-accuracy#english-to-mirad", "base_card_id": "word:low-accuracy"},
        {"id": "word:high-accuracy#english-to-mirad", "base_card_id": "word:high-accuracy"},
        {"id": "word:few-seen#english-to-mirad", "base_card_id": "word:few-seen"},
        {"id": "word:many-seen#english-to-mirad", "base_card_id": "word:many-seen"},
    ]
    weights = _mastered_card_probability_weights(
        items,
        {
            "word:low-accuracy": {"attempts": 10, "correct": 6},
            "word:high-accuracy": {"attempts": 10, "correct": 10},
            "word:few-seen": {"attempts": 3, "correct": 3},
            "word:many-seen": {"attempts": 20, "correct": 20},
        },
    )

    minimum_probability = 1 / (2 * len(items))
    assert abs(sum(weights.values()) - 1.0) < 1e-12
    assert all(weight >= minimum_probability for weight in weights.values())
    assert weights["word:low-accuracy#english-to-mirad"] > weights["word:high-accuracy#english-to-mirad"]
    assert weights["word:few-seen#english-to-mirad"] > weights["word:many-seen#english-to-mirad"]


def test_mixed_mode_finishes_unseen_beginner_direction_before_general_pool() -> None:
    cards = [
        {"id": "word:general", "type": "word", "english": "the", "mirad": "te"},
        {"id": "word:beginner", "type": "word", "english": "hello", "mirad": "hay", "beginner_order": "0"},
    ]
    events = [
        _event("word:beginner#english-to-mirad", correct=True, answered_at=NOW - timedelta(minutes=1), expected_answer="hay", submitted_answer="hay"),
    ]

    queue = build_practice_queue(cards=cards, events=events, now=NOW, limit=2, mode="mixed")

    assert any(card["id"] == "word:beginner#mirad-to-english" for card in queue["cards"])


def test_mixed_mode_returns_to_existing_new_pool_after_all_beginner_direction_items_attempted() -> None:
    cards = [
        {"id": "word:general", "type": "word", "english": "the", "mirad": "te"},
        {"id": "word:beginner-first", "type": "word", "english": "hello", "mirad": "hay", "beginner_order": "0"},
        {"id": "word:beginner-second", "type": "word", "english": "yes", "mirad": "va", "beginner_order": "1"},
    ]
    events = [
        _event("word:beginner-first#english-to-mirad", correct=True, answered_at=NOW - timedelta(minutes=4), expected_answer="hay", submitted_answer="hay"),
        _event("word:beginner-first#mirad-to-english", correct=True, answered_at=NOW - timedelta(minutes=3), expected_answer="hello", submitted_answer="hello"),
        _event("word:beginner-second#english-to-mirad", correct=True, answered_at=NOW - timedelta(minutes=2), expected_answer="va", submitted_answer="va"),
        _event("word:beginner-second#mirad-to-english", correct=True, answered_at=NOW - timedelta(minutes=1), expected_answer="yes", submitted_answer="yes"),
    ]

    queue = build_practice_queue(cards=cards, events=events, now=NOW, limit=3, mode="mixed")

    assert any(card["base_card_id"] == "word:general" for card in queue["cards"])


def test_mixed_mode_keeps_numbers_out_until_beginner_cards_are_attempted(monkeypatch) -> None:
    monkeypatch.setattr("mirad_webapp.practice_engine._NUMBERS_NEW_CARD_PROBABILITY", 1.0)
    cards = [
        {"id": "word:general", "type": "word", "english": "the", "mirad": "te"},
        {"id": "word:beginner", "type": "word", "english": "hello", "mirad": "hay", "beginner_order": "0"},
        {"id": "word:number-zero", "type": "word", "english": "zero", "mirad": "o", "numbers_order": "0"},
    ]

    queue = build_practice_queue(cards=cards, events=[], now=NOW, limit=2, mode="mixed")

    assert queue["cards"]
    assert all(card.get("beginner_order") is not None for card in queue["cards"])
    assert all(card.get("numbers_order") is None for card in queue["cards"])


def test_mixed_mode_can_sample_numbers_after_beginner_cards_before_general_pool(monkeypatch) -> None:
    monkeypatch.setattr("mirad_webapp.practice_engine._NUMBERS_NEW_CARD_PROBABILITY", 1.0)
    cards = [
        {"id": "word:general", "type": "word", "english": "the", "mirad": "te"},
        {"id": "word:beginner", "type": "word", "english": "hello", "mirad": "hay", "beginner_order": "0"},
        {"id": "word:number-zero", "type": "word", "english": "zero", "mirad": "o", "numbers_order": "0"},
        {"id": "word:number-one", "type": "word", "english": "one", "mirad": "a", "numbers_order": "1"},
    ]
    events = [
        _event("word:beginner#english-to-mirad", correct=True, answered_at=NOW - timedelta(minutes=2), expected_answer="hay", submitted_answer="hay"),
        _event("word:beginner#mirad-to-english", correct=True, answered_at=NOW - timedelta(minutes=1), expected_answer="hello", submitted_answer="hello"),
    ]

    queue = build_practice_queue(cards=cards, events=events, now=NOW, limit=3, mode="mixed")

    assert any(card.get("numbers_order") is not None for card in queue["cards"])


def test_mixed_mode_avoids_repeating_base_card_before_ten_others_when_pool_allows() -> None:
    cards = _repeat_gap_cards(11)

    queue = build_practice_queue(cards=cards, events=[], now=NOW, limit=22, mode="mixed")

    base_card_ids = [card["base_card_id"] for card in queue["cards"]]
    first_base_ids = base_card_ids[:5]

    assert queue["mode"] == "mixed"
    assert queue["repeat_gap"] == 3
    assert queue["repeat_gap_satisfied"] is True
    assert len(first_base_ids) == 5
    assert len(set(first_base_ids[:4])) == 4
    for index, base_card_id in enumerate(base_card_ids):
        later_positions = [later for later in range(index + 1, len(base_card_ids)) if base_card_ids[later] == base_card_id]
        if later_positions:
            assert later_positions[0] - index > 3


def test_empty_pool_in_mode_reports_repeat_gap_fallback_without_crashing() -> None:
    queue = build_practice_queue(cards=[], events=[], now=NOW, limit=5, mode="revision")

    assert queue == {
        "ok": True,
        "phase": "practice_queue",
        "mode": "revision",
        "mode_detail": "empty_pool",
        "repeat_gap": 3,
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
    assert queue["repeat_gap"] == 3
    assert queue["repeat_gap_satisfied"] is False
    assert queue["cards"]
    assert len(queue["cards"]) == 3
    first_three_bases = {card["base_card_id"] for card in queue["cards"][:3]}
    assert first_three_bases == {"word:01", "word:02", "word:03"}


def test_direction_choice_biases_toward_less_seen_direction_proportionally() -> None:
    cards = [{"id": "word:skew", "type": "word", "english": "skew", "mirad": "skewa"}]
    events = [
        _event(
            "word:skew#mirad-to-english",
            correct=True,
            answered_at=NOW - timedelta(days=21 - i),
            expected_answer="skew",
            submitted_answer="skew",
        )
        for i in range(8)
    ] + [
        _event(
            "word:skew#english-to-mirad",
            correct=True,
            answered_at=NOW - timedelta(days=2),
            expected_answer="skewa",
            submitted_answer="skewa",
        )
    ]

    queue = build_practice_queue(cards=cards, events=events, now=NOW, limit=1)

    assert queue["cards"]
    assert queue["cards"][0]["base_card_id"] == "word:skew"
    assert queue["cards"][0]["id"] == "word:skew#english-to-mirad"
def test_adaptive_session_struggling_biases_mastered_recent_toward_more_recent_cards() -> None:
    cards = [
        {"id": "word:recent", "type": "word", "english": "recent", "mirad": "recent"},
        {"id": "word:old", "type": "word", "english": "old", "mirad": "old"},
        {"id": "word:newbie", "type": "word", "english": "newbie", "mirad": "newbie"},
    ]
    events = [
        _event("word:recent#english-to-mirad", correct=True, answered_at=NOW - timedelta(hours=2), expected_answer="recent", submitted_answer="recent"),
        _event("word:old#english-to-mirad", correct=True, answered_at=NOW - timedelta(days=7), expected_answer="old", submitted_answer="old"),
        _event("word:recent#mirad-to-english", correct=False, answered_at=NOW - timedelta(minutes=50), expected_answer="recent", submitted_answer="x"),
        _event("word:old#mirad-to-english", correct=False, answered_at=NOW - timedelta(minutes=40), expected_answer="old", submitted_answer="x"),
        _event("word:recent#mirad-to-english", correct=False, answered_at=NOW - timedelta(minutes=30), expected_answer="recent", submitted_answer="x"),
        _event("word:old#mirad-to-english", correct=False, answered_at=NOW - timedelta(minutes=20), expected_answer="old", submitted_answer="x"),
    ]

    queue = build_practice_queue(cards=cards, events=events, now=NOW, limit=4, mode="mixed")

    assert queue["cards"]
    assert queue["cards"][0]["base_card_id"] in {"word:recent", "word:old"}
    assert queue["cards"][0]["scheduler_reason"] == "weak_recent_performance"
    new_indexes = [
        i for i, c in enumerate(queue["cards"])
        if c["scheduler_reason"] in {"new_item", "new_item_gated_by_weak_recent_performance"}
    ]
    if new_indexes:
        first_new_index = new_indexes[0]
        first_weak_index = next(i for i, c in enumerate(queue["cards"]) if c["scheduler_reason"] == "weak_recent_performance")
        assert first_weak_index < first_new_index


def test_adaptive_session_strong_biases_mastered_recent_toward_less_recent_cards() -> None:
    cards = [
        {"id": "word:recent", "type": "word", "english": "recent", "mirad": "recent"},
        {"id": "word:old", "type": "word", "english": "old", "mirad": "old"},
    ]
    events = [
        *_correct_streak("word:recent#english-to-mirad", start=NOW - timedelta(hours=2), expected_answer="recent", submitted_answer="recent"),
        *_correct_streak("word:old#english-to-mirad", start=NOW - timedelta(days=7), expected_answer="old", submitted_answer="old"),
        *_correct_streak("word:recent#mirad-to-english", start=NOW - timedelta(minutes=50), expected_answer="recent", submitted_answer="recent"),
        *_correct_streak("word:old#mirad-to-english", start=NOW - timedelta(minutes=40), expected_answer="old", submitted_answer="old"),
    ]

    queue = build_practice_queue(cards=cards, events=events, now=NOW, limit=4, mode="mixed")
    mastered = [c for c in queue["cards"] if c["scheduler_reason"] == "mastered_recent"]

    assert mastered
    assert {card["base_card_id"] for card in mastered} == {"word:recent", "word:old"}


def test_build_practice_achievements_unlocks_five_day_streak() -> None:
    before_events = [
        {
            "card_id": "word:the#english-to-mirad",
            "base_card_id": "word:the",
            "direction": "english_to_mirad",
            "card_type": "word",
            "submitted_answer": "te",
            "expected_answer": "te",
            "correct": True,
            "answered_at": (NOW - timedelta(days=offset)).isoformat(),
        }
        for offset in range(1, 5)
    ]
    after_events = [
        *before_events,
        {
            "card_id": "word:be#english-to-mirad",
            "base_card_id": "word:be",
            "direction": "english_to_mirad",
            "card_type": "word",
            "submitted_answer": "bi",
            "expected_answer": "bi",
            "correct": True,
            "answered_at": NOW.isoformat(),
        },
    ]

    achievements = build_practice_achievements(
        cards=CARDS,
        before_events=before_events,
        after_events=after_events,
        username="mira",
        latest_card_id="word:be#english-to-mirad",
        now=NOW,
    )

    assert any(achievement["id"] == "practice-streak-5" for achievement in achievements)


def test_build_practice_achievements_unlocks_first_mastered_direction_card() -> None:
    before_events: list[dict[str, object]] = []
    after_events = _correct_streak(
        "word:the#english-to-mirad",
        start=NOW - timedelta(minutes=5),
        expected_answer="te",
        submitted_answer="te",
    )

    achievements = build_practice_achievements(
        cards=CARDS,
        before_events=before_events,
        after_events=after_events,
        username="mira",
        latest_card_id="word:the#english-to-mirad",
        now=NOW,
    )

    assert achievements == [
        {
            "id": "mastered-cards-1",
            "kind": "mastered_cards",
            "threshold": 1,
            "title": "🏆 First card mastered!",
            "message": "Congratulations mira! 🎉\nYou have mastered your first card: the ↔ te\nKeep up the good work! 🚀",
            "highlighted_base_card_id": "word:the",
            "highlighted_pair": {"english": "the", "mirad": "te"},
            "sound": "achievement",
        }
    ]


def test_build_practice_achievements_unlocks_ten_mastered_direction_cards() -> None:
    cards = [
        {"id": f"word:w{i}", "type": "word", "english": f"w{i}", "mirad": f"m{i}"}
        for i in range(10)
    ]
    before_events: list[dict[str, object]] = []
    for i in range(9):
        before_events.extend(
            _correct_streak(
                f"word:w{i}#english-to-mirad",
                start=NOW + timedelta(minutes=i * 10),
                expected_answer=f"m{i}",
                submitted_answer=f"m{i}",
            )
        )
    after_events = [
        *before_events,
        *_correct_streak(
            "word:w9#english-to-mirad",
            start=NOW + timedelta(minutes=100),
            expected_answer="m9",
            submitted_answer="m9",
        ),
    ]

    achievements = build_practice_achievements(
        cards=cards,
        before_events=before_events,
        after_events=after_events,
        username="mira",
        latest_card_id="word:w9#english-to-mirad",
        now=NOW,
        lifecycle_rows=[
            {
                "base_card_id": "word:w9",
                "direction": "english_to_mirad",
                "lifecycle": "revision",
                "correct_streak": 3,
            }
        ],
    )

    assert [achievement["threshold"] for achievement in achievements] == [10]
    assert achievements[0]["id"] == "mastered-cards-10"
    assert achievements[0]["highlighted_base_card_id"] == "word:w9"


def test_build_practice_achievements_unlocks_twenty_mastered_direction_cards_with_lifecycle_rows() -> None:
    cards = [
        {"id": f"word:w{i}", "type": "word", "english": f"w{i}", "mirad": f"m{i}"}
        for i in range(20)
    ]
    before_events: list[dict[str, object]] = []
    for i in range(19):
        before_events.extend(
            _correct_streak(
                f"word:w{i}#english-to-mirad",
                start=NOW + timedelta(minutes=i * 10),
                expected_answer=f"m{i}",
                submitted_answer=f"m{i}",
            )
        )
    after_events = [
        *before_events,
        *_correct_streak(
            "word:w19#english-to-mirad",
            start=NOW + timedelta(minutes=200),
            expected_answer="m19",
            submitted_answer="m19",
        ),
    ]

    achievements = build_practice_achievements(
        cards=cards,
        before_events=before_events,
        after_events=after_events,
        username="mira",
        latest_card_id="word:w19#english-to-mirad",
        now=NOW,
        lifecycle_rows=[
            {
                "base_card_id": "word:w19",
                "direction": "english_to_mirad",
                "lifecycle": "revision",
                "correct_streak": 3,
            }
        ],
    )

    assert [achievement["threshold"] for achievement in achievements] == [20]
    assert achievements[0]["id"] == "mastered-cards-20"
    assert achievements[0]["highlighted_base_card_id"] == "word:w19"


def test_lifecycle_mastery_counts_only_exact_direction_not_entire_base() -> None:
    cards = [{"id": "word:one", "type": "word", "english": "one", "mirad": "un"}]
    after_events = _correct_streak(
        "word:one#english-to-mirad",
        start=NOW,
        expected_answer="un",
        submitted_answer="un",
    )

    progress = build_practice_progress(cards=cards, events=after_events, now=NOW)
    achievements = build_practice_achievements(
        cards=cards,
        before_events=[],
        after_events=after_events,
        username="mira",
        latest_card_id="word:one#english-to-mirad",
        now=NOW,
        lifecycle_rows=[
            {
                "base_card_id": "word:one",
                "direction": "english_to_mirad",
                "lifecycle": "revision",
                "correct_streak": 3,
            }
        ],
    )

    mastered = _mastered_item_ids_from_lifecycle(
        progress,
        [
            {
                "base_card_id": "word:one",
                "direction": "english_to_mirad",
                "lifecycle": "revision",
                "correct_streak": 3,
            }
        ],
    )

    assert mastered == {"word:one#english-to-mirad"}
    assert progress["mastered_cards"] == ["word:one#english-to-mirad"]
    assert achievements[0]["threshold"] == 1


def test_build_practice_achievements_unlocks_repeating_milestones_after_100() -> None:
    assert _achievement_milestones_up_to(149) == [1, 10, 20, 50, 80, 100]
    assert _achievement_milestones_up_to(150) == [1, 10, 20, 50, 80, 100, 150]
    assert _achievement_milestones_up_to(249) == [1, 10, 20, 50, 80, 100, 150, 200]
    assert _achievement_milestones_up_to(250) == [1, 10, 20, 50, 80, 100, 150, 200, 250]
