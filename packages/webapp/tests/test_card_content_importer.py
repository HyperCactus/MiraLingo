from __future__ import annotations

from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

import pytest

from mirad_webapp.card_content import import_card_content


Card = dict[str, Any]
Lookup = Callable[[str], str | None]


def _write_phrase_csv(path: Path, rows: Iterable[str]) -> Path:
    path.write_text("english,mirad\n" + "\n".join(rows) + "\n", encoding="utf-8")
    return path


def _cards_of_type(result: Any, card_type: str) -> list[Card]:
    cards = result["cards"] if isinstance(result, dict) else result.cards
    return [card for card in cards if card["type"] == card_type]


def _count(result: Any, card_type: str, outcome: str, reason: str | None = None) -> int:
    counts = result["counts"] if isinstance(result, dict) else result.counts
    bucket = counts[card_type][outcome]
    if reason is None:
        return bucket
    return bucket[reason]


def _import(
    phrase_csv: Path,
    *,
    word_candidates: Iterable[str] = (),
    lexicon: dict[str, str] | None = None,
) -> Any:
    lookup_table = lexicon or {}

    def lookup(english: str) -> str | None:
        return lookup_table.get(english)

    return import_card_content(
        phrase_csv_path=phrase_csv,
        beginner_json_path=None,
        numbers_json_path=None,
        word_candidates=word_candidates,
        lexicon_lookup=lookup,
    )


def test_beginner_module_pairs_import_first_with_order_metadata(tmp_path: Path) -> None:
    phrase_csv = _write_phrase_csv(tmp_path / "phrases.csv", ["hello world,ha world"])
    beginner_json = tmp_path / "beginner.json"
    beginner_json.write_text(
        '{"pairs":[{"english":"hello","mirad":"hay"},{"english":"good morning","mirad":"gud morgen"}]}',
        encoding="utf-8",
    )

    result = import_card_content(
        phrase_csv_path=phrase_csv,
        beginner_json_path=beginner_json,
        word_candidates=[],
        lexicon_lookup={}.get,
    )

    assert result.cards[:2] == [
        {"type": "word", "english": "hello", "mirad": "hay", "beginner_order": "0"},
        {"type": "phrase", "english": "good morning", "mirad": "gud morgen", "beginner_order": "1"},
    ]
    assert result.counts["beginner"]["imported"] == 2
    assert result.sources["beginner_json"] == str(beginner_json)


def test_module_comma_separated_english_expands_prompts_but_keeps_one_reverse_answer_card(tmp_path: Path) -> None:
    phrase_csv = _write_phrase_csv(tmp_path / "phrases.csv", [])
    beginner_json = tmp_path / "beginner.json"
    beginner_json.write_text('{"pairs":[{"english":"is,are","mirad":"se"}]}', encoding="utf-8")

    result = import_card_content(
        phrase_csv_path=phrase_csv,
        beginner_json_path=beginner_json,
        numbers_json_path=None,
        word_candidates=[],
        lexicon_lookup={}.get,
    )

    assert result.cards == [
        {
            "type": "word",
            "english": "is",
            "mirad": "se",
            "id": "word:is-se",
            "follow_up_english": "is, are",
            "beginner_order": "0",
        },
        {
            "type": "word",
            "english": "are",
            "mirad": "se",
            "beginner_order": "0",
            "english_to_mirad_only": True,
        },
    ]
    assert result.counts["beginner"]["imported"] == 2


def test_module_card_id_does_not_collide_with_general_word_card(tmp_path: Path) -> None:
    phrase_csv = _write_phrase_csv(tmp_path / "phrases.csv", [])
    beginner_json = tmp_path / "beginner.json"
    beginner_json.write_text('{"pairs":[{"english":"is,are","mirad":"se"}]}', encoding="utf-8")

    result = import_card_content(
        phrase_csv_path=phrase_csv,
        beginner_json_path=beginner_json,
        numbers_json_path=None,
        word_candidates=["am"],
        lexicon_lookup={"am": "amilk"}.get,
    )

    module_se = next(card for card in result.cards if card.get("id") == "word:is-se")
    general_am = next(card for card in result.cards if card.get("english") == "am" and card.get("mirad") == "amilk")

    assert module_se["follow_up_english"] == "is, are"
    assert general_am.get("id") is None
    assert {card.get("id") or f"word:{card['english']}" for card in result.cards if card["english"] == "am"} == {"word:am"}
    assert {card.get("id") or f"word:{card['english']}" for card in result.cards if card["mirad"] == "se"} == {"word:is-se", "word:are"}


def test_beginner_and_numbers_modules_import_with_independent_order_metadata(tmp_path: Path) -> None:
    phrase_csv = _write_phrase_csv(tmp_path / "phrases.csv", [])
    beginner_json = tmp_path / "beginner.json"
    beginner_json.write_text('{"pairs":[{"english":"hello","mirad":"hay"}]}', encoding="utf-8")
    numbers_json = tmp_path / "numbers.json"
    numbers_json.write_text(
        '{"pairs":[{"english":"zero","mirad":"o"},{"english":"one","mirad":"a"}]}',
        encoding="utf-8",
    )

    result = import_card_content(
        phrase_csv_path=phrase_csv,
        beginner_json_path=beginner_json,
        numbers_json_path=numbers_json,
        word_candidates=[],
        lexicon_lookup={}.get,
    )

    assert result.cards == [
        {"type": "word", "english": "hello", "mirad": "hay", "beginner_order": "0"},
        {"type": "word", "english": "zero", "mirad": "o", "numbers_order": "0"},
        {"type": "word", "english": "one", "mirad": "a", "numbers_order": "1"},
    ]
    assert result.counts["beginner"]["imported"] == 1
    assert result.counts["numbers"]["imported"] == 2
    assert result.sources["numbers_json"] == str(numbers_json)


def test_multi_word_english_rows_become_phrase_cards(tmp_path: Path) -> None:
    phrase_csv = _write_phrase_csv(
        tmp_path / "phrases.csv",
        [
            "hello world,ha world",
            "good morning,ha morning",
        ],
    )

    result = _import(phrase_csv)

    assert _cards_of_type(result, "phrase") == [
        {"type": "phrase", "english": "hello world", "mirad": "ha world"},
        {"type": "phrase", "english": "good morning", "mirad": "ha morning"},
    ]
    assert _count(result, "phrase", "imported") == 2
    assert _count(result, "phrase", "skipped", "one_word_english") == 0


def test_one_word_and_blank_or_malformed_phrase_rows_are_skipped_with_reasons(tmp_path: Path) -> None:
    phrase_csv = _write_phrase_csv(
        tmp_path / "phrases.csv",
        [
            "hello,hola",
            ",has no english",
            "has no mirad,",
            "too,many,columns",
            "two words,ha wo",
        ],
    )

    result = _import(phrase_csv)

    assert _cards_of_type(result, "phrase") == [
        {"type": "phrase", "english": "two words", "mirad": "ha wo"},
    ]
    assert _count(result, "phrase", "imported") == 1
    assert _count(result, "phrase", "skipped", "one_word_english") == 1
    assert _count(result, "phrase", "skipped", "blank_english") == 1
    assert _count(result, "phrase", "skipped", "blank_mirad") == 1
    assert _count(result, "phrase", "skipped", "malformed_row") == 1


def test_word_candidates_are_looked_up_and_imported_in_deterministic_input_order(tmp_path: Path) -> None:
    phrase_csv = _write_phrase_csv(tmp_path / "phrases.csv", [])

    result = _import(
        phrase_csv,
        word_candidates=["zebra", "apple", "brisk"],
        lexicon={"zebra": "zeb", "apple": "apil", "brisk": "briskad"},
    )

    assert _cards_of_type(result, "word") == [
        {"type": "word", "english": "zebra", "mirad": "zeb"},
        {"type": "word", "english": "apple", "mirad": "apil"},
        {"type": "word", "english": "brisk", "mirad": "briskad"},
    ]
    assert _count(result, "word", "imported") == 3


def test_comma_separated_word_translations_import_as_exact_follow_up_cards(tmp_path: Path) -> None:
    phrase_csv = _write_phrase_csv(tmp_path / "phrases.csv", [])

    result = _import(
        phrase_csv,
        word_candidates=["keyboard"],
        lexicon={"keyboard": "buxnufsemes, byuxarsemes, raduzarfaof, sem raduzar"},
    )

    assert _cards_of_type(result, "word") == [
        {
            "id": "word:keyboard-buxnufsemes",
            "type": "word",
            "english": "keyboard",
            "mirad": "buxnufsemes",
            "follow_up_mirad": "buxnufsemes, byuxarsemes, raduzarfaof, sem raduzar",
        },
        {
            "id": "word:keyboard-byuxarsemes",
            "type": "word",
            "english": "keyboard",
            "mirad": "byuxarsemes",
            "follow_up_mirad": "buxnufsemes, byuxarsemes, raduzarfaof, sem raduzar",
        },
        {
            "id": "word:keyboard-raduzarfaof",
            "type": "word",
            "english": "keyboard",
            "mirad": "raduzarfaof",
            "follow_up_mirad": "buxnufsemes, byuxarsemes, raduzarfaof, sem raduzar",
        },
        {
            "id": "word:keyboard-sem-raduzar",
            "type": "word",
            "english": "keyboard",
            "mirad": "sem raduzar",
            "follow_up_mirad": "buxnufsemes, byuxarsemes, raduzarfaof, sem raduzar",
        },
    ]
    assert _count(result, "word", "imported") == 4


def test_missing_word_translations_are_counted_as_misses_not_blank_cards(tmp_path: Path) -> None:
    phrase_csv = _write_phrase_csv(tmp_path / "phrases.csv", [])

    result = _import(
        phrase_csv,
        word_candidates=["known", "absent"],
        lexicon={"known": "koni"},
    )

    assert _cards_of_type(result, "word") == [
        {"type": "word", "english": "known", "mirad": "koni"},
    ]
    assert _count(result, "word", "imported") == 1
    assert _count(result, "word", "missed", "lexicon_miss") == 1
    assert all(card["mirad"] for card in _cards_of_type(result, "word"))


def test_duplicate_english_mirad_pairs_are_not_imported_twice_across_sources(tmp_path: Path) -> None:
    phrase_csv = _write_phrase_csv(
        tmp_path / "phrases.csv",
        [
            "good day,bon dia",
            "good day,bon dia",
            "fresh phrase,fres fraz",
        ],
    )

    result = _import(
        phrase_csv,
        word_candidates=["word", "word", "fresh phrase"],
        lexicon={"word": "wurd", "fresh phrase": "fres fraz"},
    )

    assert _cards_of_type(result, "phrase") == [
        {"type": "phrase", "english": "good day", "mirad": "bon dia"},
        {"type": "phrase", "english": "fresh phrase", "mirad": "fres fraz"},
    ]
    assert _cards_of_type(result, "word") == [
        {"type": "word", "english": "word", "mirad": "wurd"},
    ]
    assert _count(result, "phrase", "duplicate") == 1
    assert _count(result, "word", "duplicate") == 2


def test_result_exposes_imported_skipped_missed_and_source_error_counts_by_card_type(tmp_path: Path) -> None:
    phrase_csv = _write_phrase_csv(
        tmp_path / "phrases.csv",
        [
            "one,uno",
            "two words,dos wurd",
        ],
    )

    result = _import(phrase_csv, word_candidates=["known", "missing"], lexicon={"known": "kon"})

    counts = result["counts"] if isinstance(result, dict) else result.counts
    assert counts["beginner"] == {
        "imported": 0,
        "skipped": {
            "blank_english": 0,
            "blank_mirad": 0,
            "malformed_item": 0,
        },
        "duplicate": 0,
        "source_error": 0,
    }
    assert counts["numbers"] == {
        "imported": 0,
        "skipped": {
            "blank_english": 0,
            "blank_mirad": 0,
            "malformed_item": 0,
        },
        "duplicate": 0,
        "source_error": 0,
    }
    assert counts["phrase"] == {
        "imported": 1,
        "skipped": {
            "blank_english": 0,
            "blank_mirad": 0,
            "malformed_row": 0,
            "one_word_english": 1,
        },
        "missed": {},
        "duplicate": 0,
        "source_error": 0,
    }
    assert counts["word"] == {
        "imported": 1,
        "skipped": {},
        "missed": {"lexicon_miss": 1},
        "duplicate": 0,
        "source_error": 0,
    }


def test_missing_phrase_source_returns_structured_source_missing_error(tmp_path: Path) -> None:
    missing_csv = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError) as exc_info:
        _import(missing_csv)

    error = exc_info.value
    assert getattr(error, "code") == "source_missing"
    assert getattr(error, "source_type") == "phrase_csv"
    assert str(missing_csv) in str(error)
