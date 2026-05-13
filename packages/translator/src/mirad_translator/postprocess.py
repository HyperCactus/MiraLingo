"""
Deterministic Mirad post-processor for known systematic translation errors.

Applies high-precision particle corrections and structural cleanups derived from
the error taxonomy (17 miss examples from DeepSeek-V4-Flash LabeledFewShot k=5 eval).

Rules that are CONSERVATIVE (flagged only, not auto-corrected):
  - Progressive verb '-eye' suffix truncation
  - Lexicon substitution errors (wrong word entirely)
  - Structural/hallucination errors
"""

from __future__ import annotations

import re
from typing import List

# Words that can appear after 'ge' in non-comparative contexts.
# If the next word is in this set, the 'ge' is not a comparative 'ge'.
_ADJECTIVE_AFTER_GE_BLACKLIST: frozenset[str] = frozenset({
    "se", "voy", "ha", "at", "et", "it", "hus", "his",
    "hi", "hia", "hua", "huta", "hita", "hata",
    "bi", "be", "bu", "ba",
    "ni", "ne", "na",
    "ga", "gwa", "go", "gwo", "ge",
    "ay", "ey", "oy", "bayhus", "avhus",
    "vyel",
})

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _split_words(text: str) -> List[str]:
    """Split on whitespace, preserving empty tokens."""
    return text.split()


def _fix_comparative_ge(text: str) -> str:
    """
    A2 — Replace second 'ge' → 'vyel' in comparative constructions.

    The problematic pattern is:  ge + ADJECTIVE + ge + NOUN/PRONOUN
    where the second ge should be vyel (than), not the 'as' particle.

    The first 'ge' after 'se' (copula) is the 'as' particle (correct).
    The 'ge' AFTER the adjective starts the second half of the comparison.

    Example:
      "Hia tam voy se ge aga ge atas"  →  "Hia tam voy se ge aga vyel atas"
    """
    words = _split_words(text)
    parts: List[str] = []
    i = 0
    ge_replaced = False
    while i < len(words):
        token = words[i]
        stripped = re.sub(r"[.]", "", token)
        next_stripped = (
            re.sub(r"[.]", "", words[i + 1]).lower()
            if i + 1 < len(words)
            else ""
        )
        prev_stripped = (
            re.sub(r"[.]", "", words[i - 1]).lower()
            if i > 0
            else ""
        )
        # Detect "ge + ADJECTIVE + ge" where the second ge is wrong
        if (
            not ge_replaced
            and stripped.lower() == "ge"
            and i + 1 < len(words)
        ):
            next_word = words[i + 1]
            next_clean = re.sub(r"[.]", "", next_word).lower()
            # The next word should look like an adjective (alphabetic, not a
            # function word, and we know the one AFTER it is the ge to replace)
            if next_clean and next_clean not in _ADJECTIVE_AFTER_GE_BLACKLIST:
                # Look ahead: is the word AFTER the next one 'ge'?
                if i + 2 < len(words):
                    after_next_clean = (
                        re.sub(r"[.]", "", words[i + 2]).lower()
                    )
                    if after_next_clean == "ge":
                        # Replace the AFTER-next ge (i+2) with vyel
                        punct_after_next = words[i + 2][len(words[i + 2]) - 1] \
                            if words[i + 2][-1] == "." else ""
                        parts.append(token)  # current ge stays
                        parts.append(next_word)  # adjective stays
                        parts.append("vyel" + punct_after_next)  # replace next ge
                        ge_replaced = True
                        i += 3
                        continue
        parts.append(token)
        i += 1
    return " ".join(parts)


def _fix_possessive_be(text: str) -> str:
    """
    A1 — Replace 'be' → 'bi' in possessive constructions.

    Possessive constructions follow: noun + bi + determiner + noun
    The particle is 'bi' (associative/benefactive), not 'be' (copula).
    We apply this only when 'be' is between two content words (not at
    sentence boundaries where it acts as a copula).

    Example:
      "tam be yata yubem" (with determiner yata) → "tam bi yata yubem"
    """
    words = _split_words(text)
    parts: List[str] = []
    for i, token in enumerate(words):
        stripped = re.sub(r"[.]", "", token)
        if stripped.lower() == "be":
            prev_word = words[i - 1] if i > 0 else ""
            next_word = words[i + 1] if i + 1 < len(words) else ""
            prev_stripped = re.sub(r"[.]", "", prev_word).lower()
            next_stripped = re.sub(r"[.]", "", next_word).lower()
            # Possessive: be appears between a noun (prev) and a possessive
            # determiner (next) — possessive determiners end in -a in Mirad
            is_prev_noun = bool(prev_stripped and prev_stripped not in {
                "se", "voy", "ha", "at", "et", "it", "hus", "his",
                "ni", "ne", "na", "bi", "bu", "ba",
                "ga", "gwa", "go", "gwo",
            })
            is_next_determiner = next_stripped.endswith("a") or next_stripped in {
                "ha", "hi", "hua", "his", "eta", "ata", "ita",
                "yata", "hata", "hita", "huta",
            }
            if is_prev_noun and is_next_determiner:
                punct = token[len(stripped):]
                parts.append("bi" + punct)
                continue
        parts.append(token)
    return " ".join(parts)


def _strip_meta_commentary(text: str) -> str:
    """
    Strip leading/trailing commentary that is meta-linguistic text the model
    sometimes wraps around translations.

    Heuristics for leading commentary:
      - Lines containing "mirad", "translation", "english", "→" before the
        actual sentence.
      - Content in quotes or brackets that doesn't look like the sentence itself.
    """
    original = text
    text = text.strip()

    # Strip leading markers like "Mirad: ...", "Translation: ...", "→ ..."
    # These are common meta-commentary prefixes from LM output.
    text = re.sub(
        r"^(mirad[:\s]*|translation[:\s]*|→\s*|\.\.\.\s*|output[:\s]*)",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Strip trailing meta commentary — trailing text after the last punctuation
    # that looks like commentary (starts with parentheses, or is just a single
    # bracketed note).
    text = re.sub(r"\s*\(.*\)\s*$", "", text)
    text = re.sub(r"\s*\[.*\]\s*$", "", text)

    return text.strip() or original


def _normalize_whitespace_and_punctuation(text: str) -> str:
    """
    Normalize whitespace and punctuation.
    Always-safe structural cleanup.
    """
    # Collapse multiple spaces
    text = re.sub(r" {2,}", " ", text)
    # Collapse internal newlines into single spaces
    text = re.sub(r"\s*\n\s*", " ", text)
    text = re.sub(r" {2,}", " ", text)
    # Fix "!." or "?." at end of string — Mirad never uses both
    text = re.sub(r"([!?])\.+$", r"\1", text)
    # Remove trailing periods before other sentence-end punctuation
    # e.g. "word.!" → "word!" — but only when followed by another punct char
    text = re.sub(r"\.([!?])", r"\1", text)
    text = text.strip()
    return text


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def postprocess_mirad(text: str) -> str:
    """
    Apply deterministic post-processing to a raw Mirad translation from the LM.

    Steps (in order):
      1. Strip meta-commentary wrappers
      2. Normalize whitespace and punctuation
      3. Particle correction: be → bi in possessive constructions
      4. Particle correction: ge → vyel in comparative constructions

    Parameters
    ----------
    text : str
        Raw translation output from the LM.

    Returns
    -------
    str
        Cleaned translation with systematic errors corrected.

    Notes
    -----
    - This is a pure function; no LM calls.
    - Lexicon substitution errors (wrong word entirely) and structural
      hallucinations are NOT auto-corrected; they require model improvement.
    - Progressive '-eye' suffix truncation is flagged but not auto-corrected
      due to ambiguity with legitimate -ie endings.
    """
    if not text:
        return text

    text = text.strip()
    if not text:
        return text

    text = _strip_meta_commentary(text)
    text = _normalize_whitespace_and_punctuation(text)
    text = _fix_possessive_be(text)
    text = _fix_comparative_ge(text)

    return text


def flag_conservative_errors(text: str) -> List[str]:
    """
    Return a list of human-readable flags for errors that should NOT be
    auto-corrected (lexicon errors, structural hallucinations).

    Parameters
    ----------
    text : str
        The (possibly erroneous) translation.

    Returns
    -------
    List[str]
        List of flag messages for errors requiring review.

    Notes
    -----
    These categories are flagged for review because auto-correction risks
    false positives:
      - Progressive verb '-eye' suffix truncation (e.g. "mamilie" → "mamili-eye")
      - Object-verb order inversion
      - Hallucinated vocabulary (completely wrong word)
    """
    flags: List[str] = []

    # B2: -ie ending that might be a truncated -eye progressive
    # Pattern: verb stem ending in vowel + "-ie" where -eye might be expected
    if re.search(r"[aeiouy][bcdfgklmprstvwxyz]*ie\b", text, re.IGNORECASE):
        flags.append(
            "possible_progressive_suffix_truncation: "
            "found -ie verb form that might be truncated -eye progressive"
        )

    # D5/D7 patterns: voy before the verb at start might indicate SVO inversion
    # (very conservative flag — do not fix without validation)
    if re.match(r"^\s*voy\s+\S+", text, re.IGNORECASE):
        flags.append(
            "possible_verb_subject_order_inversion: "
            "sentence starts with voy (negation) before verb"
        )

    return flags