"""Tests for mirad_tts.tokenize()."""

from __future__ import annotations

import pytest

from mirad_tts.tokenizer import (
    UnsupportedLegacyOrthographyError,
    tokenize,
)
from mirad_tts.types import Token, TokenType


class TestTokenize:
    def test_tokenize_words_only(self) -> None:
        result = tokenize("At")
        assert result == [Token("At", TokenType.WORD)]

    def test_tokenize_demo(self) -> None:
        """Slice demo: 'At tixe Mirad.' → 4 tokens."""
        result = tokenize("At tixe Mirad.")
        assert result == [
            Token("At", TokenType.WORD),
            Token("tixe", TokenType.WORD),
            Token("Mirad", TokenType.WORD),
            Token(".", TokenType.PUNCT),
        ]

    def test_tokenize_numbers(self) -> None:
        result = tokenize("123")
        assert result == [Token("123", TokenType.NUMBER)]

    def test_tokenize_mixed(self) -> None:
        """'hello 123 !' → WORD, NUMBER, PUNCT (spaces skipped)."""
        result = tokenize("hello 123 !")
        assert len(result) == 3
        assert result[0] == Token("hello", TokenType.WORD)
        assert result[1] == Token("123", TokenType.NUMBER)
        assert result[2] == Token("!", TokenType.PUNCT)

    def test_tokenize_empty(self) -> None:
        result = tokenize("")
        assert result == []

    def test_tokenize_legacy_error(self) -> None:
        with pytest.raises(UnsupportedLegacyOrthographyError):
            tokenize("café")

    def test_tokenize_legacy_message(self) -> None:
        with pytest.raises(UnsupportedLegacyOrthographyError) as exc_info:
            tokenize("à test")
        assert "legacy" in str(exc_info.value).lower()

    def test_tokenize_legacy_uppercase(self) -> None:
        with pytest.raises(UnsupportedLegacyOrthographyError):
            tokenize("CAFÉ")

    def test_tokenize_original_casing(self) -> None:
        """Token.text preserves original case, not uppercased."""
        result = tokenize("Mirad")
        assert result[0].text == "Mirad"
        assert result[0].text != "MIRAD"

    def test_tokenize_punctuation_preserved(self) -> None:
        """'a. b' → three non-space tokens: WORD, PUNCT, WORD."""
        result = tokenize("a. b")
        assert len(result) == 3
        texts = [t.text for t in result]
        assert texts == ["a", ".", "b"]