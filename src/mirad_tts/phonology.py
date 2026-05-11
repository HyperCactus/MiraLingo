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
    "g": "ɡ",  # voiced velar plosive (IPA symbol ɡ, not Latin g)
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
    "q": "k",
    "c": "t͡ʃ",  # unvoiced palato-alveolar affricate (tie bar may not be supported by all TTS engines)
}

# ── Piper-specific phoneme mapping ────────────────────────────────────────────
#
# Piper's neural TTS models learn phoneme-to-acoustic mappings from a fixed
# phoneme_id_map defined in their JSON config.  Each key is a single Unicode
# codepoint; multi-character IPA like "t͡ʃ" decomposes into codepoints that
# may not exist in the map (notably the tie bar U+0361), which causes Piper
# to silently skip those phonemes — the root cause of "missing letters".
#
# This mapping emits *only* chars that exist in common Piper voice configs.
# It keeps pretty IPA (CONSONANT_IPA) separate from Piper-safe phonemes.
# Affricates are decomposed: c → ["t", "ʃ"] instead of "t͡ʃ".

PIPER_CONSONANTS: dict[str, list[str]] = {
    "b": ["b"],
    "d": ["d"],
    "f": ["f"],
    "g": ["ɡ"],   # IPA ɡ (U+0261), not ASCII g — both exist but ɡ matches eSpeak training data
    "h": ["h"],
    "j": ["ʒ"],
    "k": ["k"],
    "l": ["l"],
    "m": ["m"],
    "n": ["n"],
    "p": ["p"],
    "r": ["ɾ"],   # alveolar flap — present in both tested voice configs
    "s": ["s"],
    "t": ["t"],
    "v": ["v"],
    "w": ["w"],
    "x": ["ʃ"],
    "y": ["j"],    # glide [j] — IPA j, same as eSpeak
    "z": ["z"],
    # Mirad c = /t͡ʃ/ decomposed for Piper
    "c": ["t", "ʃ"],
    # Mirad q = /k/
    "q": ["k"],
}

PIPER_SIMPLE_VOWELS: dict[str, list[str]] = {
    "a": ["a"],
    "e": ["e"],
    "i": ["i"],
    "o": ["o"],
    "u": ["u"],
}

PIPER_COMPLEX_VOWELS: dict[str, list[str]] = {
    # Post-y-glided (ay, ey, iy, oy, uy)
    "ay": ["a", "ɪ"],
    "ey": ["e", "ɪ"],
    "iy": ["i", "ɪ"],
    "oy": ["o", "ɪ"],
    "uy": ["u", "ɪ"],
    # Post-w-glided (aw, ew, iw, ow, uw)
    "aw": ["ɔ"],
    "ew": ["ɛ", "ʊ"],
    "iw": ["i", "ʊ"],
    "ow": ["o", "ʊ"],
    "uw": ["u", "ʊ"],
    # Pre-y-glided (ya, ye, yi, yo, yu)
    "ya": ["j", "a"],
    "ye": ["j", "e"],
    "yi": ["j", "i"],
    "yo": ["j", "o"],
    "yu": ["j", "u"],
    # Pre-w-glided (wa, we, wi, wo, wu)
    "wa": ["w", "a"],
    "we": ["w", "e"],
    "wi": ["w", "i"],
    "wo": ["w", "o"],
    "wu": ["w", "u"],
    # Circum-y-glided (yay, yey, yiy, yoy, yuy)
    "yay": ["j", "a", "ɪ"],
    "yey": ["j", "e", "ɪ"],
    "yiy": ["j", "i", "ɪ"],
    "yoy": ["j", "o", "ɪ"],
    "yuy": ["j", "u", "ɪ"],
    # Pre-w-post-y-glided (way, wey, wiy, woy, wuy)
    "way": ["w", "a", "ɪ"],
    "wey": ["w", "e", "ɪ"],
    "wiy": ["w", "i", "ɪ"],
    "woy": ["w", "o", "ɪ"],
    "wuy": ["w", "u", "ɪ"],
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
    "ay": "aɪ",
    "ey": "eɪ",
    "iy": "iɪ",
    "oy": "oɪ",
    "uy": "uɪ",
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
# IPA mappings for vowels (used by ipa.py)
COMPLEX_VOWEL_IPA: dict[str, str] = dict(COMPLEX_VOWELS)

SIMPLE_VOWEL_IPA: dict[str, str] = {
    "a": "a",
    "e": "e",
    "i": "i",
    "o": "o",
    "u": "u",
}
