"""Type definitions for Mirad TTS tokens."""

from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    """Broad category of a token."""

    WORD = "WORD"      # alphabetic word
    NUMBER = "NUMBER"  # numeric literal
    PUNCT = "PUNCT"    # punctuation mark
    SPACE = "SPACE"    # whitespace run


@dataclass(frozen=True, slots=True)
class Token:
    """A single token produced by the Mirad tokenizer.

    Attributes
    ----------
    text : str
        The original character sequence from the input.
    type_ : TokenType
        The semantic category of this token.
    """

    text: str
    type_: TokenType

    def __repr__(self) -> str:
        return f"Token({self.text!r}, {self.type_.name})"