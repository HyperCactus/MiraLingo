<<<<<<< HEAD
"""Tokenizer for Mirad text — splits raw strings into typed tokens."""

from __future__ import annotations

import re
from typing import List

from mirad_tts.types import Token, TokenType


class UnsupportedLegacyOrthographyError(Exception):
    """Raised when input contains legacy Mirad/Unilingua diacritics.

    Use newer Mirad Grammar orthography (plain Latin letters only).
    """

    pass


# Matches accented vowel letters used in the legacy (pre-revision) orthography.
# Covers both cases so we reject 'café' and 'CAFÉ' equally.
LEGACY_DIACRITICS_REGEX = re.compile(r"[áàâéèêíìîóòôúùûÁÀÂÉÈÊÍÌÎÓÒÔÚÙÛ]")


def tokenize(text: str) -> List[Token]:
    """Split a Mirad text string into tokens.

    Parameters
    ----------
    text
        Raw input string.

    Returns
    -------
    List[Token]
        Tokens in left-to-right order.

    Raises
    ------
    UnsupportedLegacyOrthographyError
        If any legacy diacritic character (accented vowel) is found.
    """
    if LEGACY_DIACRITICS_REGEX.search(text):
        raise UnsupportedLegacyOrthographyError(
            "Legacy diacritic character found. "
            "Mirad orthography uses plain Latin letters only."
        )

    tokens: List[Token] = []

    # Find all tokens in a single left-to-right pass.
    # Re Pattern is sorted by start position; finditer returns in order.
    for match in _TOKEN_RE.finditer(text):
        kind = match.lastgroup
        assert kind is not None
        if kind == "SPACE":
            continue  # skip whitespace tokens
        elif kind == "NUMBER":
            token_type = TokenType.NUMBER
        elif kind == "WORD":
            token_type = TokenType.WORD
        else:
            token_type = TokenType.PUNCT
        tokens.append(Token(text=match.group(), type_=token_type))

    return tokens


# Compiled once at module load; used by tokenize() above.
_TOKEN_RE = re.compile(
    r"(?P<SPACE>\s+)"
    r"|(?P<NUMBER>\d+)"
    r"|(?P<WORD>[A-Za-z]+)"
    r"|(?P<PUNCT>[^A-Za-z\d\s])"
)
=======
"""Tokenizer for Mirad IPA text conversion."""

from __future__ import annotations

import enum
from dataclasses import dataclass


class TokenType(enum.Enum):
    WORD = "WORD"
    SPACE = "SPACE"
    PUNCT = "PUNCT"


@dataclass(frozen=True, slots=True)
class Token:
    type_: TokenType
    value: str


def tokenize(text: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch.isspace():
            start = i
            while i < len(text) and text[i].isspace():
                i += 1
            tokens.append(Token(type_=TokenType.SPACE, value=text[start:i]))
            continue

        if ch.isalpha() or ch == "'":
            start = i
            while i < len(text) and (text[i].isalpha() or text[i] == "'"):
                i += 1
            tokens.append(Token(type_=TokenType.WORD, value=text[start:i]))
            continue

        tokens.append(Token(type_=TokenType.PUNCT, value=ch))
        i += 1

    return tokens
>>>>>>> milestone/M001
