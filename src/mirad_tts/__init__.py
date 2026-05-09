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

from . import cli
from .espeak_backend import (
    EspeakBinaryNotFoundError,
    EspeakConversionError,
    EspeakSynthesisError,
    EspeakSynthesisTimeoutError,
    syllable_to_espeak,
    synthesize_to_wav,
    text_to_espeak_phoneme_input,
    word_to_espeak,
)
from .ipa import syllable_to_ipa, text_to_ipa, word_to_ipa
from mirad_tts.phonology import (
    COMPLEX_VOWEL_STARTS,
    COMPLEX_VOWELS,
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
    "COMPLEX_VOWEL_STARTS",
    "COMPLEX_VOWELS",
    "EspeakBinaryNotFoundError",
    "EspeakConversionError",
    "EspeakSynthesisError",
    "EspeakSynthesisTimeoutError",
    "GLOTTAL",
    "Syllable",
    "Token",
    "TokenType",
    "UnsupportedLegacyOrthographyError",
    "assign_stress",
    "cli",
    "espeak_backend",
    "ipa",
    "syllabify",
    "syllabify_word",
    "syllable_to_espeak",
    "syllable_to_ipa",
    "synthesize_to_wav",
    "text_to_espeak_phoneme_input",
    "text_to_ipa",
    "tokenize",
    "word_to_espeak",
    "word_to_ipa",
]