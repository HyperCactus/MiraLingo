"""IPA conversion for Mirad words and text."""

from __future__ import annotations

from .phonology import COMPLEX_VOWEL_IPA, CONSONANT_IPA, SIMPLE_VOWEL_IPA
from .syllabify import Syllable, assign_stress, syllabify_word
from .tokenizer import tokenize
from .types import TokenType


def _consonants_to_ipa(chars: str) -> str:
    return "".join(CONSONANT_IPA.get(char.lower(), char) for char in chars)


def _nucleus_to_ipa(nucleus: str) -> str:
    lower_nucleus = nucleus.lower()
    if lower_nucleus in COMPLEX_VOWEL_IPA:
        return COMPLEX_VOWEL_IPA[lower_nucleus]
    return "".join(SIMPLE_VOWEL_IPA.get(ch, ch) for ch in lower_nucleus)


def syllable_to_ipa(syllable: Syllable) -> str:
    onset = _consonants_to_ipa(syllable.onset)
    nucleus = _nucleus_to_ipa(syllable.nucleus)
    coda = _consonants_to_ipa(syllable.coda)
    ipa = f"{onset}{nucleus}{coda}"
    if syllable.stressed:
        return f"ˈ{ipa}"
    return ipa


def word_to_ipa(word: str, stress: bool = True, dotted: bool = False) -> str:
    syllables = syllabify_word(word.lower())
    if not syllables:
        return ""

    if stress and len(syllables) > 1:
        syllables = assign_stress(syllables)

    separator = "." if dotted else ""
    return separator.join(syllable_to_ipa(syllable) for syllable in syllables)


def text_to_ipa(text: str) -> str:
    output: list[str] = []
    for token in tokenize(text):
        if token.type_ == TokenType.WORD:
            output.append(word_to_ipa(token.text))
        else:
            output.append(token.text)
    return "".join(output)
