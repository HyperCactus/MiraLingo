"""Tests for Token and TokenType types."""

import pytest

from mirad_tts.types import Token, TokenType


class TestTokenType:
    """Tests for the TokenType enum."""

    def test_all_variants_exist(self):
        """All four TokenType variants are defined and distinct."""
        assert hasattr(TokenType, "WORD")
        assert hasattr(TokenType, "NUMBER")
        assert hasattr(TokenType, "PUNCT")
        assert hasattr(TokenType, "SPACE")

    def test_values_are_distinct(self):
        """Each TokenType variant has a unique value."""
        values = {t.value for t in TokenType}
        assert len(values) == len(TokenType)


class TestToken:
    """Tests for the Token dataclass."""

    def test_text_attribute(self):
        """Token.text returns the original character sequence."""
        tok = Token("hello", TokenType.WORD)
        assert tok.text == "hello"

    def test_type_attribute(self):
        """Token.type_ returns the token category."""
        tok = Token("hello", TokenType.WORD)
        assert tok.type_ == TokenType.WORD

    def test_token_with_number_type(self):
        """Token correctly stores a NUMBER type."""
        tok = Token("42", TokenType.NUMBER)
        assert tok.text == "42"
        assert tok.type_ == TokenType.NUMBER

    def test_token_with_punct_type(self):
        """Token correctly stores a PUNCT type."""
        tok = Token(".", TokenType.PUNCT)
        assert tok.text == "."
        assert tok.type_ == TokenType.PUNCT

    def test_token_with_space_type(self):
        """Token correctly stores a SPACE type."""
        tok = Token("   ", TokenType.SPACE)
        assert tok.text == "   "
        assert tok.type_ == TokenType.SPACE

    def test_frozen_immutability(self):
        """Token is frozen: attributes cannot be changed after creation."""
        tok = Token("abc", TokenType.WORD)
        with pytest.raises(AttributeError):
            tok.text = "xyz"  # type: ignore[indexblank]

    def test_slots_memory_efficiency(self):
        """Token uses __slots__ for memory efficiency."""
        # If __slots__ is properly set, the class should have a __slots__ attribute
        assert hasattr(Token, "__slots__")

    def test_repr(self):
        """Token.__repr__ is human-readable."""
        tok = Token("hello", TokenType.WORD)
        assert "hello" in repr(tok)
        assert "WORD" in repr(tok)

    def test_equality(self):
        """Two tokens with the same fields are equal."""
        a = Token("hello", TokenType.WORD)
        b = Token("hello", TokenType.WORD)
        assert a == b

    def test_inequality_by_text(self):
        """Tokens with different text are not equal."""
        a = Token("hello", TokenType.WORD)
        b = Token("world", TokenType.WORD)
        assert a != b

    def test_inequality_by_type(self):
        """Tokens with different types are not equal."""
        a = Token("42", TokenType.NUMBER)
        b = Token("42", TokenType.WORD)
        assert a != b