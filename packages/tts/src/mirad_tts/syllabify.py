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

# Onset cluster sets: [bcdfgjknpstvz] + [lrwyn]
_OF: frozenset[str] = frozenset("bcdfgjknpstvz")
_OS: frozenset[str] = frozenset("lrwyn")


def _is_valid_onset(a: str, b: str) -> bool:
    """True if a+b is a valid 2-char onset cluster."""
    return a in _OF and b in _OS


def _starts_vowel(word: str, pos: int) -> bool:
    """True when word[pos] starts a vowel (simple vowel or y/w glide)."""
    if pos >= len(word):
        return False
    c = word[pos]
    if c in SIMPLE_VOWELS:
        return True
    return c in ("y", "w")



def _find_nuclei(word: str) -> list[tuple[int, int]]:
    """Return list of (start, end_exclusive) for each vowel nucleus in word.

    Matches 3-char circum-glided vowels first (yay, way, ...), then 2-char
    complex vowels (ay, ya, aw, ...), then simple vowels (a e i o u).

    When a potential 2-char vowel match would consume a character that is itself
    the start of a different valid nucleus, the later match takes priority.
    This correctly handles overlapping cases like upayo where 'ay' at (2,4)
    should not block 'yo' at (3,5).
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
            nuclei.append((i, i + 3)); i += 3; continue
        # 2-char complex vowel: ay, ya, aw, wa, etc.
        elif i + 2 <= len(word) and word[i : i + 2] in _C2:
            # If the second character itself starts a valid 2-char or 3-char nucleus
            # on its own, skip this match so the later (more specific) one wins.
            # E.g., in 'upayo' we match 'yo' at (3,5) not 'ay' at (2,4).
            second = word[i + 1]
            second_starts_2char = (i + 1 + 2 <= len(word) and
                                  word[i + 1 : i + 3] in _C2)
            second_starts_3char = (i + 1 + 3 <= len(word) and
                                  word[i + 1 : i + 4] in _C3)
            if second_starts_2char or second_starts_3char:
                # Second char starts its own nucleus — skip this one
                pass
            else:
                nuclei.append((i, i + 2)); i += 2; continue
        # Simple vowel: a, e, i, o, u.
        if ch in SIMPLE_VOWELS:
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
      - Coda = consonants after the nucleus, determined by:
          1. Adjacent nuclei (no gap) → no coda (booka: bo-o-ka)
          2. r/l: coda when followed by consonant or word-final;
             onset when followed by a vowel (Mi-rad, a-layn)
          3. Other consonants: coda when followed by consonant;
             onset when followed by a simple vowel starting the
             next nucleus (aym-se-a, pix-wa, tam-bwa)
      - Next syllable starts after the coda.

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

    for nidx, (n_start, n_end) in enumerate(nuclei):
        nucleus_text = word[n_start:n_end]
        onset_text = word[pos:n_start]

        # Coda accumulation: loop collecting chars after nucleus
        # RULES (from Mirad Grammar):
        #   Adjacent nuclei (e.g. booka "oo"): no gap -> no coda
        #   r/l: coda UNLESS followed by standalone simple vowel
        #        that does NOT start a complex vowel (Mi-rad vs al-ayn)
        #   Other consonants: coda UNLESS next char starts a vowel
        #        or this char forms valid onset cluster with next char (te-jna)
        coda_text = ""
        coda_end = n_end
        if coda_end < len(word):
            peek_nidx = nidx + 1
            next_nucleus_start = nuclei[peek_nidx][0] if peek_nidx < len(nuclei) else None
            # Guard: adjacent nuclei means no gap for coda
            if next_nucleus_start is not None and coda_end >= next_nucleus_start:
                pass  # no gap; next onset starts at next_nucleus_start
            else:
                # Loop accumulating zero or more coda chars
                while coda_end < len(word) and (next_nucleus_start is None or coda_end < next_nucleus_start):
                    ch = word[coda_end]
                    # Simple vowel after nucleus? Not coda, it starts next syllable
                    if ch in SIMPLE_VOWELS:
                        break
                    # r/l handling: coda unless followed by standalone simple vowel
                    if ch in ("r", "l"):
                        if next_nucleus_start is not None:
                            follower = word[coda_end + 1] if coda_end + 1 < len(word) else ""
                            if (follower in SIMPLE_VOWELS
                                    and coda_end + 2 <= len(word)
                                    and word[coda_end + 1 : coda_end + 3] not in _C2):
                                break  # r/l joins next onset (Mi-rad)
                        coda_text += ch
                        coda_end += 1
                    # y/w: coda unless next char is a simple vowel
                    elif ch in ("y", "w"):
                        if next_nucleus_start is not None:
                            follower = word[coda_end + 1] if coda_end + 1 < len(word) else ""
                            if follower in SIMPLE_VOWELS:
                                break
                        coda_text += ch
                        coda_end += 1
                    # Other consonants: coda unless next char starts vowel
                    # or this+next form valid onset cluster
                    else:
                        if next_nucleus_start is not None:
                            follower = word[coda_end + 1] if coda_end + 1 < len(word) else ""
                            if follower in SIMPLE_VOWELS:
                                break  # consonant joins next onset
                            if coda_end + 1 < len(word) and _is_valid_onset(ch, word[coda_end + 1]):
                                break  # valid onset cluster (te-jna)
                        coda_text += ch
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