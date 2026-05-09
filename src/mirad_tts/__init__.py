<<<<<<< HEAD
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
=======
"""Public API for Mirad TTS phoneme pipeline."""

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
from .phonology import COMPLEX_VOWELS, SIMPLE_VOWELS
from .syllabify import Syllable, assign_stress, syllabify, syllabify_word
from .tokenizer import tokenize

__all__ = [
    "COMPLEX_VOWELS",
    "cli",
    "SIMPLE_VOWELS",
    "Syllable",
    "syllabify_word",
    "syllabify",
    "assign_stress",
    "syllable_to_ipa",
    "word_to_ipa",
    "text_to_ipa",
    "EspeakConversionError",
    "EspeakSynthesisError",
    "EspeakBinaryNotFoundError",
    "EspeakSynthesisTimeoutError",
    "syllable_to_espeak",
    "word_to_espeak",
    "text_to_espeak_phoneme_input",
    "synthesize_to_wav",
    "tokenize",
]
from .tokenizer import Token, TokenType
>>>>>>> milestone/M001
