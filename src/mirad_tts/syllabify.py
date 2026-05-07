"""Mirad syllabification engine.

Syllabifies a Mirad orthographic word into a list of `Syllable` objects.

Grammar anchor examples (from Mirad Grammar "Syllabification" chart):
    ama    → a-ma
    ayma   → ay-ma
    aymsea → aym-se-a
    pixwa  → pix-wa
    upayo  → u-pa-yo
    vyaa   → vya-a
    vyaay  → vya-ay
    vay    → vay
    tambwa → tam-bwa

Plus roadmap cases:
    booka  → bo-o-ka
"""

from __future__ import annotations

from dataclasses import dataclass

from mirad_tts.phonology import COMPLEX_VOWELS, COMPLEX_VOWEL_STARTS, SIMPLE_VOWELS

# ── Complex vowel lookup sets ───────────────────────────────────────────────────
_C3: frozenset[str] = frozenset(k for k in COMPLEX_VOWELS if len(k) == 3)
_C2: frozenset[str] = frozenset(k for k in COMPLEX_VOWELS if len(k) == 2)


def _find_nuclei(word: str) -> list[tuple[int, int]]:
    """Return list of (start, end_exclusive) for each vowel nucleus in word.

    Matches 3-char circum-glided vowels first (yay, way, ...), then 2-char
    complex vowels (ay, ya, aw, ...), then simple vowels (a e i o u).
    Two adjacent simple vowels produce two separate nuclei (grammar case 3).
    """
    nuclei: list[tuple[int, int]] = []
    i = 0
    while i < len(word):
        ch = word[i]
        if ch not in COMPLEX_VOWEL_STARTS:
            i += 1
            continue
        # 3-char circum-glided vowel: yay, way, etc.
        if i + 3 <= len(word) and word[i : i + 3] in _C3:
            nuclei.append((i, i + 3)); i += 3
        # 2-char complex vowel: ay, ya, aw, wa, etc.
        elif i + 2 <= len(word) and word[i : i + 2] in _C2:
            nuclei.append((i, i + 2)); i += 2
        # Simple vowel: a, e, i, o, u.
        elif ch in SIMPLE_VOWELS:
            nuclei.append((i, i + 1)); i += 1
        else:
            i += 1
    return nuclei


# ── Syllable dataclass ─────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class Syllable:
    """A single syllabified syllable from a Mirad word."""

    text: str     # onset + nucleus + coda
    onset: str    # leading consonants
    nucleus: str  # simple or complex vowel
    coda: str     # trailing consonants (only r or l per grammar rule 6)
    stressed: bool = False  # stress marker (Mirad: stress on last non-final syllable)

    def __repr__(self) -> str:
        return (f"Syllable(text={self.text!r}, onset={self.onset!r}, "
                f"nucleus={self.nucleus!r}, coda={self.coda!r}, "
                f"stressed={self.stressed!r})")


# ── Core syllabification ───────────────────────────────────────────────────────


def _is_complex_vowel_at(word: str, pos: int) -> bool:
    """True when word[pos:pos+2] is a valid 2-char complex vowel."""
    return pos + 1 < len(word) and word[pos : pos + 2] in _C2


def syllabify_word(word: str) -> list[Syllable]:
    """Split a Mirad word into syllables.

    Algorithm: left-to-right over nuclei.
      - Onset = everything from current pointer to nucleus start.
      - Nucleus = the vowel (simple or complex).
      - Coda = consonants after the nucleus until hitting a character that
        would start the onset of the next syllable. w or y stops coda ONLY
        when it forms the start of a 2-char complex vowel (wa, ya, ay, etc.)
      - Next syllable starts after the coda.

    Rules (per Mirad Grammar "Syllabification" chart):
      1. Every syllable contains exactly one vowel (simple or complex).
      2. Complex vowels (ay, ya, aw, wa) are single nuclei.
      3. Adjacent simple vowels → two nuclei (aymsea → aym-se-a; booka → bo-o-ka).
      4. Consonants after a nucleus form coda unless the first such consonant
         would start a complex vowel — then that consonant (and any preceding
         non-nucleus consonants) join the onset of the next syllable.
         pixwa → pix-wa; tambwa → tam-bwa; upayo → u-pa-yo

    Parameters
    ----------
    word : str
        A single Mirad word (no spaces).

    Returns
    -------
    list[Syllable]
        Ordered list from left to right.
    """
    if not word:
        return []

    nuclei = _find_nuclei(word)
    if not nuclei:
        return [Syllable(text=word, onset=word, nucleus="", coda="")]

    syllables: list[Syllable] = []
    pos = 0

    for n_start, n_end in nuclei:
        nucleus_text = word[n_start:n_end]
        onset_text = word[pos:n_start]

        # Coda: collect consonants after the nucleus. Stop when we hit a
        # character that starts a complex vowel (e.g. w in 'wa', y in 'ya').
        # Those characters join the ON-SET of the next syllable.
        coda_text = ""
        coda_end = n_end
        while (coda_end < len(word)
               and not _is_complex_vowel_at(word, coda_end)
               and word[coda_end] not in SIMPLE_VOWELS):
            coda_text += word[coda_end]
            coda_end += 1

        syllables.append(
            Syllable(
                text=onset_text + nucleus_text + coda_text,
                onset=onset_text,
                nucleus=nucleus_text,
                coda=coda_text,
            )
        )
        pos = coda_end

    return syllables


def syllabify(word: str) -> list[str]:
    """Syllabify a word, returning a list of orthographic syllable strings.

    >>> syllabify("aymsea")
    ['aym', 'se', 'a']
    >>> syllabify("booka")
    ['bo', 'o', 'ka']
    """
    return [s.text for s in syllabify_word(word)]


# ── Stress assignment ─────────────────────────────────────────────────────────


def assign_stress(syllables: list[Syllable]) -> list[Syllable]:
    """Assign stress to syllables per Mirad Grammar.

    Rule: stress falls on the last non-final syllable.
    - Single-syllable words: no stress.
    - Multi-syllable words: stress the syllable at index len(syllables) - 2.

    Parameters
    ----------
    syllables : list[Syllable]
        Syllables produced by syllabify_word().

    Returns
    -------
    list[Syllable]
        Same syllables with stressed=True on the stressed syllable.

    Examples
    --------
    >>> igay = syllabify_word("igay")   # ["i", "gay"]
    >>> stressed = assign_stress(igay)
    >>> [s.stressed for s in stressed]
    [True, False]

    >>> mirad = syllabify_word("Mirad")  # ["Mi", "rad"]
    >>> stressed = assign_stress(mirad)
    >>> [s.stressed for s in stressed]
    [True, False]
    """
    if len(syllables) <= 1:
        return [
            Syllable(text=s.text, onset=s.onset, nucleus=s.nucleus,
                     coda=s.coda, stressed=False)
            for s in syllables
        ]

    stress_idx = len(syllables) - 2
    result: list[Syllable] = []
    for i, s in enumerate(syllables):
        result.append(
            Syllable(text=s.text, onset=s.onset, nucleus=s.nucleus,
                     coda=s.coda, stressed=(i == stress_idx))
        )
    return result