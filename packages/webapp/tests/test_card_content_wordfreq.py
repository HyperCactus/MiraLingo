from __future__ import annotations

import builtins
import sys
import types
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import pytest

from mirad_webapp.card_content import CardContentImportError, import_card_content


Card = dict[str, Any]


def _write_phrase_csv(path: Path, rows: Iterable[str] = ()) -> Path:
    path.write_text("english,mirad\n" + "\n".join(rows) + "\n", encoding="utf-8")
    return path


def _install_fake_wordfreq(monkeypatch: pytest.MonkeyPatch, words: list[object], calls: list[tuple[str, int]] | None = None) -> None:
    module = types.ModuleType("wordfreq")

    def top_n_list(lang: str, n: int) -> list[object]:
        if calls is not None:
            calls.append((lang, n))
        return words[:n]

    module.top_n_list = top_n_list  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "wordfreq", module)


def _word_cards(result: Any) -> list[Card]:
    return [card for card in result.cards if card["type"] == "word"]


def test_default_wordfreq_provider_preserves_ranked_order_and_requested_limit(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    calls: list[tuple[str, int]] = []
    _install_fake_wordfreq(monkeypatch, ["banana", "apple", "cherry", "date"], calls)
    phrase_csv = _write_phrase_csv(tmp_path / "phrases.csv")

    result = import_card_content(
        phrase_csv_path=phrase_csv,
        word_limit=3,
        lexicon_lookup={"banana": "ban", "apple": "apil", "cherry": "cher"}.get,
    )

    assert calls == [("en", 3)]
    assert result.sources["word_candidates"] == "wordfreq:en"
    assert _word_cards(result) == [
        {"type": "word", "english": "banana", "mirad": "ban"},
        {"type": "word", "english": "apple", "mirad": "apil"},
        {"type": "word", "english": "cherry", "mirad": "cher"},
    ]


def test_default_wordfreq_provider_counts_duplicates_and_lexicon_misses(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _install_fake_wordfreq(monkeypatch, ["shared", "shared", "missing", 123, "blank"])
    phrase_csv = _write_phrase_csv(tmp_path / "phrases.csv", ["shared phrase,shar fraz"])

    result = import_card_content(
        phrase_csv_path=phrase_csv,
        word_limit=5,
        lexicon_lookup={"shared": "sha", "123": "num", "blank": ""}.get,
    )

    assert _word_cards(result) == [
        {"type": "word", "english": "shared", "mirad": "sha"},
        {"type": "word", "english": "123", "mirad": "num"},
    ]
    assert result.counts["word"]["duplicate"] == 1
    assert result.counts["word"]["missed"]["lexicon_miss"] == 2


def test_duplicate_word_phrase_pair_is_suppressed_across_sources(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _install_fake_wordfreq(monkeypatch, ["fresh phrase", "solo"])
    phrase_csv = _write_phrase_csv(tmp_path / "phrases.csv", ["fresh phrase,fres fraz"])

    result = import_card_content(
        phrase_csv_path=phrase_csv,
        word_limit=2,
        lexicon_lookup={"fresh phrase": "fres fraz", "solo": "sol"}.get,
    )

    assert _word_cards(result) == [{"type": "word", "english": "solo", "mirad": "sol"}]
    assert result.counts["word"]["duplicate"] == 1


def test_zero_word_limit_requests_no_candidates_and_imports_no_word_cards(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    calls: list[tuple[str, int]] = []
    _install_fake_wordfreq(monkeypatch, ["the"], calls)
    phrase_csv = _write_phrase_csv(tmp_path / "phrases.csv")

    result = import_card_content(phrase_csv_path=phrase_csv, word_limit=0, lexicon_lookup={}.get)

    assert calls == [("en", 0)]
    assert _word_cards(result) == []
    assert result.counts["word"]["imported"] == 0


def test_missing_wordfreq_module_raises_provider_unavailable_diagnostic(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    phrase_csv = _write_phrase_csv(tmp_path / "phrases.csv")
    real_import = builtins.__import__

    def fake_import(name: str, *args: object, **kwargs: object) -> object:
        if name == "wordfreq":
            raise ModuleNotFoundError("No module named 'wordfreq'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    monkeypatch.delitem(sys.modules, "wordfreq", raising=False)

    with pytest.raises(CardContentImportError) as exc_info:
        import_card_content(phrase_csv_path=phrase_csv, word_limit=3, lexicon_lookup={}.get)

    error = exc_info.value
    assert error.code == "provider_unavailable"
    assert error.phase == "word_candidates"
    assert error.source_type == "wordfreq"


def test_malformed_wordfreq_api_raises_provider_unavailable_diagnostic(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    module = types.ModuleType("wordfreq")
    module.top_n_list = None  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "wordfreq", module)
    phrase_csv = _write_phrase_csv(tmp_path / "phrases.csv")

    with pytest.raises(CardContentImportError) as exc_info:
        import_card_content(phrase_csv_path=phrase_csv, word_limit=3, lexicon_lookup={}.get)

    error = exc_info.value
    assert error.code == "provider_unavailable"
    assert error.phase == "word_candidates"
    assert error.source_type == "wordfreq"


def test_injected_provider_exception_keeps_provider_error_contract(tmp_path: Path) -> None:
    phrase_csv = _write_phrase_csv(tmp_path / "phrases.csv")

    def broken_provider() -> list[str]:
        raise RuntimeError("boom")

    with pytest.raises(CardContentImportError) as exc_info:
        import_card_content(
            phrase_csv_path=phrase_csv,
            word_candidate_provider=broken_provider,
            lexicon_lookup={}.get,
        )

    error = exc_info.value
    assert error.code == "provider_error"
    assert error.phase == "word_candidates"
    assert error.source_type == "word_candidates"
