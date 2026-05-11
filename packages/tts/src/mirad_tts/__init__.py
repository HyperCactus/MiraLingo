"""mirad_tts — Mirad TTS text-to-speech preparation library.

Public API
----------
Token        : token dataclass (text, type_)
TokenType    : WORD / NUMBER / PUNCT / SPACE
tokenize()   : str → List[Token], raises UnsupportedLegacyOrthographyError on accented vowels
syllabify()  : str → List[str], orthographic syllable text segments
syllabify_word() : str → List[Syllable], full syllable objects with onset/nucleus/coda
Syllable     : frozen/slots dataclass (text, onset, nucleus, coda)
"""

from __future__ import annotations

from .espeak_backend import (
    EspeakBinaryNotFoundError,
    EspeakConversionError,
    EspeakSynthesisError,
    EspeakSynthesisTimeoutError,
    syllable_to_espeak,
    synthesize_to_wav as espeak_synthesize_to_wav,
    text_to_espeak_phoneme_input,
    word_to_espeak,
)
from .ipa import syllable_to_ipa, text_to_ipa, word_to_ipa
from .phonology import (
    COMPLEX_VOWEL_STARTS,
    COMPLEX_VOWELS,
    GLOTTAL,
    PIPER_COMPLEX_VOWELS,
    PIPER_CONSONANTS,
    PIPER_SIMPLE_VOWELS,
    SIMPLE_VOWELS,
)
from .syllabify import Syllable, assign_stress, syllabify, syllabify_word
from .tokenizer import (
    UnsupportedLegacyOrthographyError,
    tokenize,
)
from .types import Token, TokenType


def __getattr__(name: str):  # type: ignore[no-untyped-def]
    """Lazy-import piper and mbrola backends only when accessed."""
    _piper_names = {
        "PiperModelNotFoundError",
        "PiperPhonemeDebug",
        "PiperPhonemeError",
        "PiperSynthesisError",
        "diagnose_text",
        "piper_diagnose_text",
        "piper_get_available_voices",
        "piper_phonemes_to_ids",
        "piper_word_to_ids",
        "syllable_to_piper_phonemes",
        "piper_synthesize_to_wav",
        "text_to_piper_phonemes",
        "word_to_piper_phonemes",
        "piper_backend",
    }
    _mbrola_names = {
        "MbrolaError",
        "MbrolaNotFoundError",
        "MbrolaVoiceNotFoundError",
        "MbrolaSynthesisError",
        "PhoLine",
        "diagnose_mbrola",
        "generate_pho",
        "mbrola_synthesize_to_wav",
        "pho_to_string",
        "syllable_to_mbrola",
        "text_to_mbrola_phones",
        "word_to_mbrola",
        "word_to_mbrola_phones",
        "write_pho",
        "mbrola_backend",
    }

    if name in _piper_names:
        from . import piper_backend as _pb

        value = getattr(_pb, name.replace("piper_diagnose_text", "diagnose_text"), None)
        if value is None:
            value = getattr(_pb, name)
        globals()[name] = value
        return value

    if name in _mbrola_names:
        from . import mbrola_backend as _mb

        value = globals()[name] = getattr(_mb, name)
        return value

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# Explicitly list all public names so `from mirad_tts import *` works
# including the lazy-loaded ones (they'll resolve via __getattr__)
__all__ = [
    "COMPLEX_VOWEL_STARTS",
    "COMPLEX_VOWELS",
    "EspeakBinaryNotFoundError",
    "EspeakConversionError",
    "EspeakSynthesisError",
    "EspeakSynthesisTimeoutError",
    "GLOTTAL",
    "MbrolaError",
    "MbrolaNotFoundError",
    "MbrolaSynthesisError",
    "MbrolaVoiceNotFoundError",
    "PiperModelNotFoundError",
    "PiperPhonemeError",
    "PiperSynthesisError",
    "PiperPhonemeDebug",
    "PhoLine",
    "Syllable",
    "Token",
    "TokenType",
    "UnsupportedLegacyOrthographyError",
    "assign_stress",
    "diagnose_mbrola",
    "espeak_backend",
    "espeak_synthesize_to_wav",
    "generate_pho",
    "ipa",
    "mbrola_backend",
    "mbrola_synthesize_to_wav",
    "piper_diagnose_text",
    "piper_get_available_voices",
    "piper_phonemes_to_ids",
    "piper_synthesize_to_wav",
    "piper_word_to_ids",
    "pho_to_string",
    "syllabify",
    "syllabify_to_piper_phonemes",
    "syllable_to_espeak",
    "syllable_to_ipa",
    "syllable_to_mbrola",
    "syllable_to_piper_phonemes",
    "syllabify_word",
    "synthesize_to_wav",
    "text_to_espeak_phoneme_input",
    "text_to_ipa",
    "text_to_mbrola_phones",
    "text_to_piper_phonemes",
    "tokenize",
    "word_to_espeak",
    "word_to_ipa",
    "word_to_mbrola",
    "word_to_mbrola_phones",
    "word_to_piper_phonemes",
    "write_pho",
]