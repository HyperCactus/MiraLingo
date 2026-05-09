<<<<<<< HEAD
"""Phonology constants for Mirad TTS, derived from the Mirad Grammar specification.

This module encodes the one-to-one grapheme-to-phoneme correspondences defined
in the Mirad Grammar (Wikibooks print version, Agopoff 1966).

Consonants use direct IPA symbols except:
  - r → ɾ  (alveolar flap, not trill; per spec: "The consonant r should be
    a flap or trill like the r in Brit. Eng. very or the single, intervocalic
    r in Spanish pero.")
  - x → ʃ  (unvoiced post-alveolar fricative, not /ks/; per spec.)
  - c → t͡ʃ  (unvoiced palato-alveolar affricate, used only in foreign words)
  - j → ʒ  (voiced palatal fricative; not to be confused with English j)
  - ' (glottal stop) is a word-boundary phoneme used in glottal-stop rules.

Simple vowels are a, e, i, o, u.
Complex vowels are two-character units (or circumfixed three-character units)
that count as a single phonemic vowel for the purposes of stress and syllabification.
"""

# ── Consonants ────────────────────────────────────────────────────────────────

CONSONANT_IPA: dict[str, str] = {
    "p": "p",
    "b": "b",
    "t": "t",
    "d": "d",
    "k": "k",
    "g": "g",
    "f": "f",
    "v": "v",
    "s": "s",
    "z": "z",
    "h": "h",
    "m": "m",
    "n": "n",
    # r is alveolar flap ɾ, not alveolar trill [r] or approximant [ɹ]
    "r": "ɾ",
    "l": "l",
    "w": "w",
    # y acts as glide [j] before vowels (pre-y-glided) or after vowels
    # (post-y-glided); maps to IPA [j]
    "y": "j",
    "x": "ʃ",
    "j": "ʒ",
    "c": "t͡ʃ",
}

# The glottal-stop character is used as a word-boundary phoneme, e.g. to
# realise a vowel-initial word after a preceding vowel (the "glottal-stop rule").
GLOTTAL: str = "'"

# ── Simple vowels ─────────────────────────────────────────────────────────────

# These are the five canonical vowel letters, each mapping to a single phoneme.
SIMPLE_VOWELS: frozenset[str] = frozenset("aeiou")

# ── Complex vowels ────────────────────────────────────────────────────────────
#
# Complex vowels are pre-glided, post-glided, or circumfixed vowel units that
# count as a single nucleus for stress and syllabification.  They are always
# exactly 2 characters (e.g. ay, ew) or 3 characters (e.g. yay, way).
#
# IPA values follow the Mirad Grammar complex-vowel chart exactly.
#   - Post-y-glided: ay [aɪ], ey [eɪ], iy [iɪ], oy [oɪ], uy [uɪ]
#   - Pre-y-glided:  ya [ja], ye [je], yi [ji], yo [jo], yu [ju]
#   - Post-w-glided: aw [ɔ],  ew [ɛʊ], iw [iʊ], ow [oʊ], uw [uʊ]
#   - Pre-w-glided:  wa [wa], we [we], wi [wi], wo [wo], wu [wu]
#   - Circum-y-glided (w+V+y):  yay [jaɪ], yey [jeɪ], yiy [jiɪ],
#                                yoy [joɪ], yuy [juɪ]
#   - Pre-w-post-y-glided (w+V+y): way [waɪ], wey [weɪ], wiy [wiɪ],
#                                   woy [woɪ], wuy [wuɪ]

COMPLEX_VOWELS: dict[str, str] = {
    # post-y-glided
=======
"""Phonology constants and IPA mappings for Mirad."""

COMPLEX_VOWELS: tuple[str, ...] = (
    "ay",
    "ey",
    "iy",
    "oy",
    "uy",
    "aw",
    "ew",
    "iw",
    "ow",
    "uw",
    "yo",
    "yi",
)

SIMPLE_VOWELS: tuple[str, ...] = ("a", "e", "i", "o", "u")

CONSONANT_IPA: dict[str, str] = {
    "b": "b",
    "c": "t͡ʃ",
    "d": "d",
    "f": "f",
    "g": "g",
    "h": "h",
    "j": "ʒ",
    "k": "k",
    "l": "l",
    "m": "m",
    "n": "n",
    "p": "p",
    "q": "k",
    "r": "ɾ",
    "s": "s",
    "t": "t",
    "v": "v",
    "w": "w",
    "x": "ʃ",
    "y": "j",
    "z": "z",
}

SIMPLE_VOWEL_IPA: dict[str, str] = {
    "a": "a",
    "e": "e",
    "i": "i",
    "o": "o",
    "u": "u",
    "y": "ɨ",
}

COMPLEX_VOWEL_IPA: dict[str, str] = {
>>>>>>> milestone/M001
    "ay": "aɪ",
    "ey": "eɪ",
    "iy": "iɪ",
    "oy": "oɪ",
    "uy": "uɪ",
<<<<<<< HEAD
    # pre-y-glided
    "ya": "ja",
    "ye": "je",
    "yi": "ji",
    "yo": "jo",
    "yu": "ju",
    # post-w-glided
    "aw": "ɔ",
    "ew": "ɛʊ",
    "iw": "iʊ",
    "ow": "oʊ",
    "uw": "uʊ",
    # pre-w-glided
    "wa": "wa",
    "we": "we",
    "wi": "wi",
    "wo": "wo",
    "wu": "wu",
    # circum-y-glided (w+V+y)
    "yay": "jaɪ",
    "yey": "jeɪ",
    "yiy": "jiɪ",
    "yoy": "joɪ",
    "yuy": "juɪ",
    # pre-w-post-y-glided (w+V+y)
    "way": "waɪ",
    "wey": "weɪ",
    "wiy": "wiɪ",
    "woy": "woɪ",
    "wuy": "wuɪ",
}

# Characters that can begin a complex vowel.  Used by the tokenizer to know
# when to attempt a two- or three-character match before falling back to the
# single-character simple vowel.
COMPLEX_VOWEL_STARTS: frozenset[str] = frozenset("aeiouwy")
=======
    "aw": "aʊ",
    "ew": "eʊ",
    "iw": "iʊ",
    "ow": "oʊ",
    "uw": "uʊ",
    "yo": "jo",
    "yi": "ji",
}
>>>>>>> milestone/M001
