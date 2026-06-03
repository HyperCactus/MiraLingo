from __future__ import annotations

from datetime import datetime, timedelta, timezone

from mirad_webapp.practice import MAX_EVENTS
from mirad_webapp.practice_engine import _achievement_milestones_up_to, _expected_answer_alternatives, build_practice_achievements, build_practice_progress, build_practice_queue, record_practice_answer


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
    assert queue["repeat_gap"] == 10
    assert queue["repeat_gap_satisfied"] is False
    assert queue["card_count"] == 4
    assert queue["base_card_count"] == 4
    assert queue["event_count"] == 0
    assert queue["limit"] == 4
    assert len(queue["cards"]) == 4
    assert len({card["base_card_id"] for card in queue["cards"]}) == 4
    assert all(card["scheduler_reason"] == "new_item" for card in queue["cards"])

    e2m_card = next(card for card in queue["cards"] if card["direction"] == "english_to_mirad")
    assert e2m_card["audio_card_id"] == e2m_card["base_card_id"]
    assert e2m_card["prompt_language"] == "english"
    assert e2m_card["answer_language"] == "mirad"
    assert e2m_card["mastery"] == {"attempts": 0, "correct": 0, "incorrect": 0, "accuracy": None, "consecutive_correct": 0, "streak_required": 5, "mastered": False}
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
        "streak_required": 5,
        "mastered": False,
    }
    assert all(card["scheduler_reason"] == "new_item_gated_by_weak_recent_performance" for card in queue["cards"][1:])


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

    assert [card["scheduler_reason"] for card in queue["cards"]] == [
        "weak_recent_performance",
        "weak_recent_performance",
        "new_item_gated_by_weak_recent_performance",
    ]
    assert queue["cards"][2]["id"] not in {"phrase:hello-world#english-to-mirad", "word:the#mirad-to-english"}


def test_stale_mastered_item_resurfaces_before_new_cards() -> None:
    old = NOW - timedelta(days=15)
    events = _correct_streak(
        "word:the#english-to-mirad",
        start=old,
        expected_answer="te",
        submitted_answer="te",
    )

    queue = build_practice_queue(cards=CARDS, events=events, now=NOW, limit=2)

    assert queue["cards"][0]["base_card_id"] == "word:the"
    assert queue["cards"][0]["scheduler_reason"] == "stale_mastered_review"
    assert queue["cards"][0]["recency"] == {
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

    assert queue["card_count"] == 1
    assert len(queue["cards"]) == 1
    assert queue["cards"][0]["base_card_id"] == "word:ok"


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
    assert queue["repeat_gap"] == 10
    assert queue["repeat_gap_satisfied"] is False
    assert queue["base_card_count"] == 5
    assert queue["card_count"] == 5
    assert queue["event_count"] == 6
    assert queue["cards"][0]["base_card_id"] == "word:bravo"
    assert queue["cards"][0]["scheduler_reason"] == "weak_recent_performance"
    assert queue["cards"][1]["base_card_id"] == "word:alpha"
    assert queue["cards"][1]["scheduler_reason"] == "stale_mastered_review"


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
    assert {card["scheduler_reason"] for card in queue["cards"]}.issubset({"stale_mastered_review", "mastered_recent", "weak_recent_performance"})
    assert {card["base_card_id"] for card in queue["cards"]} == {"word:alpha", "word:bravo"}


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


def test_build_practice_achievements_unlocks_first_mastered_pair() -> None:
    before_events = _correct_streak(
        "word:the#english-to-mirad",
        start=NOW - timedelta(minutes=10),
        expected_answer="te",
        submitted_answer="te",
    )
    after_events = [
        *before_events,
        *_correct_streak(
            "word:the#mirad-to-english",
            start=NOW - timedelta(minutes=5),
            expected_answer="the",
            submitted_answer="the",
        ),
    ]

    achievements = build_practice_achievements(
        cards=CARDS,
        before_events=before_events,
        after_events=after_events,
        username="mira",
        latest_card_id="word:the#mirad-to-english",
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


def test_build_practice_achievements_unlocks_repeating_milestones_after_100() -> None:
    assert _achievement_milestones_up_to(149) == [1, 10, 20, 50, 80, 100]
    assert _achievement_milestones_up_to(150) == [1, 10, 20, 50, 80, 100, 150]
    assert _achievement_milestones_up_to(249) == [1, 10, 20, 50, 80, 100, 150, 200]
    assert _achievement_milestones_up_to(250) == [1, 10, 20, 50, 80, 100, 150, 200, 250]
