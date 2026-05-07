"""mirad_tts — Mirad TTS text-to-speech preparation library.

Public API
----------
Token        : token dataclass (text, type_)
TokenType    : WORD / NUMBER / PUNCT / SPACE
tokenize()   : str → List[Token], raises UnsupportedLegacyOrthographyError on accented vowels
UnsupportedLegacyOrthographyError : raised when input contains diacritic marks
syllabify()  : str → List[str], orthographic syllable text segments
syllabify_word() : str → List[Syllable], full syllable objects with onset/nucleus/coda
Syllable     : frozen/slots dataclass (text, onset, nucleus, coda)
"""

from __future__ import annotations

from mirad_tts.phonology import (
    COMPLEX_VOWELS,
    COMPLEX_VOWEL_STARTS,
    GLOTTAL,
    SIMPLE_VOWELS,
)
from mirad_tts.syllabify import Syllable, assign_stress, syllabify, syllabify_word
from mirad_tts.tokenizer import (
    UnsupportedLegacyOrthographyError,
    tokenize,
)
from mirad_tts.types import Token, TokenType

__all__ = [
    "Syllable",
    "Token",
    "TokenType",
    "UnsupportedLegacyOrthographyError",
    "assign_stress",
    "syllabify",
    "syllabify_word",
    "tokenize",
]