"""Tests for wordfreq_utils — all wordfreq calls are mocked to avoid
data-file dependencies at test time."""

import pytest
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def make_zipf_side_effect(mapping: dict):
    """Return a side_effect function that looks up word→score in *mapping*.

    Falls back to 0.0 for unknown words (same as real wordfreq).
    """
    def _zipf(word, lang):
        return mapping.get(word.lower(), 0.0)
    return _zipf


# ---------------------------------------------------------------------------
# _split_words
# ---------------------------------------------------------------------------

from mirad_translator.wordfreq_utils import _split_words


def test_split_words_basic():
    assert _split_words("Hello, world!") == ["hello", "world"]


def test_split_words_contractions():
    assert _split_words("it's a test") == ["it's", "a", "test"]


def test_split_words_empty():
    assert _split_words("") == []


def test_split_words_punctuation_only():
    assert _split_words("... --- !!!") == []


# ---------------------------------------------------------------------------
# mean_word_frequency
# ---------------------------------------------------------------------------

from mirad_translator.wordfreq_utils import mean_word_frequency


def test_mean_word_frequency_empty():
    """Empty sentence returns 0.0."""
    assert mean_word_frequency("") == 0.0


def test_mean_word_frequency_mocked():
    """Mean of known words with mocked zipf_frequency."""
    mock_zipf = make_zipf_side_effect({
        "the": 6.5,
        "cat": 3.5,
        "sat": 3.0,
    })
    with patch("mirad_translator.wordfreq_utils.wordfreq.zipf_frequency", side_effect=mock_zipf):
        result = mean_word_frequency("The cat sat")
        # Expected: (6.5 + 3.5 + 3.0) / 3 = 4.333...
        assert abs(result - 4.333333) < 1e-4


def test_mean_word_frequency_unknown_words():
    """Unknown words contribute 0.0 to the mean."""
    mock_zipf = make_zipf_side_effect({
        "the": 6.5,
        "xyzzy": 0.0,  # unknown
    })
    with patch("mirad_translator.wordfreq_utils.wordfreq.zipf_frequency", side_effect=mock_zipf):
        result = mean_word_frequency("The xyzzy")
        # (6.5 + 0.0) / 2 = 3.25
        assert abs(result - 3.25) < 1e-4


def test_mean_word_frequency_single_known_word():
    mock_zipf = make_zipf_side_effect({"hello": 4.0})
    with patch("mirad_translator.wordfreq_utils.wordfreq.zipf_frequency", side_effect=mock_zipf):
        assert mean_word_frequency("Hello") == 4.0


# ---------------------------------------------------------------------------
# top_n_by_frequency
# ---------------------------------------------------------------------------

from mirad_translator.wordfreq_utils import top_n_by_frequency


def test_top_n_ranking():
    """Sentences are ranked by mean frequency, most common first."""
    mock_zipf = make_zipf_side_effect({
        "the": 6.5, "cat": 3.5, "a": 6.0,
        "rare": 1.0, "word": 4.0,
    })
    with patch("mirad_translator.wordfreq_utils.wordfreq.zipf_frequency", side_effect=mock_zipf):
        sentences = ["The cat", "a rare word", "the the"]
        result = top_n_by_frequency(sentences, 2)
        # "the the" → (6.5+6.5)/2 = 6.5
        # "the cat" → (6.5+3.5)/2 = 5.0
        # "a rare word" → (6.0+1.0+4.0)/3 = 3.67
        assert result == ["the the", "The cat"]


def test_top_n_fewer_than_n():
    """Returns all sentences when n > len(sentences)."""
    mock_zipf = make_zipf_side_effect({"hello": 4.0})
    with patch("mirad_translator.wordfreq_utils.wordfreq.zipf_frequency", side_effect=mock_zipf):
        result = top_n_by_frequency(["Hello world"], 5)
        assert len(result) == 1


def test_top_n_empty():
    assert top_n_by_frequency([], 5) == []


# ---------------------------------------------------------------------------
# is_common_word
# ---------------------------------------------------------------------------

from mirad_translator.wordfreq_utils import is_common_word


def test_is_common_word_above_threshold():
    mock_zipf = make_zipf_side_effect({"hello": 4.0})
    with patch("mirad_translator.wordfreq_utils.wordfreq.zipf_frequency", side_effect=mock_zipf):
        assert is_common_word("hello", threshold=3.0) is True


def test_is_common_word_below_threshold():
    mock_zipf = make_zipf_side_effect({"rare": 1.0})
    with patch("mirad_translator.wordfreq_utils.wordfreq.zipf_frequency", side_effect=mock_zipf):
        assert is_common_word("rare", threshold=3.0) is False


def test_is_common_word_at_threshold():
    """Score exactly at threshold returns True (>=)."""
    mock_zipf = make_zipf_side_effect({"word": 3.0})
    with patch("mirad_translator.wordfreq_utils.wordfreq.zipf_frequency", side_effect=mock_zipf):
        assert is_common_word("word", threshold=3.0) is True


def test_is_common_word_case_insensitive():
    mock_zipf = make_zipf_side_effect({"hello": 4.0})
    with patch("mirad_translator.wordfreq_utils.wordfreq.zipf_frequency", side_effect=mock_zipf):
        assert is_common_word("Hello", threshold=3.0) is True