"""English word frequency analysis utilities using wordfreq.

Used by the flashcard module (M004) and translator evaluation to filter
and rank words/phrases by commonness.

Requires the ``wordfreq`` package (pip install wordfreq).
"""

import re
from typing import Sequence

import wordfreq


def _split_words(text: str) -> list[str]:
    """Split text into lowercase word tokens, stripping punctuation."""
    return [w.lower() for w in re.findall(r"[A-Za-z']+", text) if w]


def mean_word_frequency(sentence: str) -> float:
    """Return the mean Zipf frequency score of words in a sentence.

    Zipf scores range from ~0 (very rare) to ~7 (most common).
    On a per-word basis, the ``wordfreq`` Zipf score represents
    log10(frequency per billion words).  A score of 3 means roughly
    1-in-1M words; 5 means roughly 1-in-10K.

    Returns 0.0 for empty input or when no words have frequency data.
    """
    words = _split_words(sentence)
    if not words:
        return 0.0

    scores = [wordfreq.zipf_frequency(w, "en") for w in words]
    # wordfreq returns 0.0 for unknown words; include them in the mean
    return sum(scores) / len(scores)


def top_n_by_frequency(sentences: Sequence[str], n: int) -> list[str]:
    """Return the top *n* sentences ranked by mean word frequency (descending).

    Ties are broken by original order.  Returns fewer than *n* entries if
    the input is shorter.
    """
    scored = [(mean_word_frequency(s), i, s) for i, s in enumerate(sentences)]
    scored.sort(key=lambda t: (-t[0], t[1]))
    return [s for _, _, s in scored[:n]]


def is_common_word(word: str, threshold: float = 3.0) -> bool:
    """Return True if a single word has Zipf frequency >= *threshold*.

    Default threshold 3.0 means the word appears roughly once per million
    words of English text — a reasonable cutoff for "common" vocabulary.
    """
    return wordfreq.zipf_frequency(word.lower(), "en") >= threshold