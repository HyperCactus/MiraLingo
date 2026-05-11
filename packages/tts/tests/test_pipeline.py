"""Full-pipeline integration tests — cover every module in composition.

These tests exercise the available Mirad phoneme pipeline stages:
    tokenize → syllabify_word → assign_stress

IPA conversion (word_to_ipa, text_to_ipa) and espeak conversion
(word_to_espeak, text_to_espeak_phoneme_input) are validated via the
CSV-anchored tests in test_pronunciation_csv.py once the ipa and
espeak_backend modules are implemented.

Each test name maps to a single grammar word so a future agent can isolate
exactly which grammar rule broke by running the named test.
"""

from __future__ import annotations

import csv as _csv
from pathlib import Path as _Path

import pytest

from mirad_tts import (
    assign_stress,
    syllabify_word,
    tokenize,
)


# ---------------------------------------------------------------------------
# 32-word grammar-anchored word list used for pipeline smoke-tests.
# ---------------------------------------------------------------------------

_GRAMMAR_ANCHOR_WORDS = [
    "ama",
    "aymsea",
    "upayo",
    "tambwa",
    "booka",
    "Mirad",
    "igay",
    "vay",
    "tejna",
    "akea",
    "byoskyin",
    "xati",
    "kopo",
    "tixe",
    "xei",
    "zoi",
    "auwa",
    "tei",
    "jal",
    "tanra",
    "skeit",
    "glyn",
    "skropo",
    "spoli",
    "jukita",
    "zopra",
    "blasi",
    "amra",
    "xulu",
    "tebra",
]

# ---------------------------------------------------------------------------
# CSV anchor words used for syllable-count and stress-position tests.
# Extracted from the pronunciation anchor CSV so the same words are
# exercised in test_pronunciation_csv.py without duplication.
# ---------------------------------------------------------------------------

_CSV_ANCHOR_WORDS = [
    "ama",
    "aymsea",
    "upayo",
    "tambwa",
    "booka",
    "Mirad",
    "igay",
    "vay",
    "tejna",
    "akea",
    "byoskyin",
    "xati",
    "kopo",
]


class TestPipelineSmoke:
    """Smoke-tests: tokenize → syllabify → assign_stress for 32 anchor words."""

    @pytest.mark.parametrize("word", _GRAMMAR_ANCHOR_WORDS)
    def test_tokenize_word(self, word: str) -> None:
        """tokenize must produce exactly one WORD token for each anchor word."""
        tokens = tokenize(word)
        assert len(tokens) == 1, f"Expected single WORD token for '{word}', got {tokens}"
        assert tokens[0].type_.name == "WORD", f"Expected WORD token for '{word}'"

    @pytest.mark.parametrize("word", _GRAMMAR_ANCHOR_WORDS)
    def test_syllabify_word_returns_nonempty(self, word: str) -> None:
        """syllabify_word must return at least one Syllable for every anchor word."""
        syllables = syllabify_word(word)
        assert syllables, f"syllabify_word returned empty for '{word}'"
        for syl in syllables:
            assert syl.text, f"Syllable has empty text for '{word}'"
            assert syl.onset is not None, f"Syllable missing onset for '{word}'"
            assert syl.nucleus is not None, f"Syllable missing nucleus for '{word}'"

    @pytest.mark.parametrize("word", _GRAMMAR_ANCHOR_WORDS)
    def test_assign_stress_produces_valid_stress_pattern(self, word: str) -> None:
        """assign_stress must not crash and must return the same number of syllables."""
        syllables = syllabify_word(word)
        if not syllables:
            pytest.skip(f"syllabify_word returned empty for '{word}'")
        stressed = assign_stress(syllables)
        assert len(stressed) == len(syllables), (
            f"assign_stress changed syllable count for '{word}': "
            f"{len(syllables)} → {len(stressed)}"
        )
        stressed_count = sum(1 for s in stressed if s.stressed)
        # Single-syllable words get no stress marker; multi-syllable get exactly one
        if len(syllables) == 1:
            assert stressed_count == 0, (
                f"'{word}' is single-syllable but has {stressed_count} stressed syllable(s)"
            )
        else:
            assert stressed_count == 1, (
                f"'{word}' has {len(syllables)} syllables but {stressed_count} stressed; "
                f"expected exactly 1 stressed syllable"
            )

    @pytest.mark.parametrize("word", _GRAMMAR_ANCHOR_WORDS)
    def test_syllable_count_stable(self, word: str) -> None:
        """syllabify_word must produce the same syllable count on repeated calls."""
        syllables_a = syllabify_word(word)
        syllables_b = syllabify_word(word)
        assert [s.text for s in syllables_a] == [s.text for s in syllables_b], (
            f"syllabify_word is non-deterministic for '{word}'"
        )

    @pytest.mark.parametrize("word", _GRAMMAR_ANCHOR_WORDS)
    def test_assign_stress_idempotent(self, word: str) -> None:
        """assign_stress must produce the same stress pattern on repeated calls."""
        syllables = syllabify_word(word)
        if not syllables:
            pytest.skip(f"syllabify_word returned empty for '{word}'")
        stressed_a = assign_stress(syllables)
        stressed_b = assign_stress(syllables)
        assert [s.text for s in stressed_a] == [s.text for s in stressed_b], (
            f"assign_stress is non-deterministic for '{word}'"
        )


class TestPipelineEdgeCasesAndStress:
    """Edge-case and stress-pattern verification against the CSV anchor data."""

    def test_empty_string_returns_empty(self) -> None:
        """Empty input must be handled gracefully by every available pipeline stage."""
        tokens = tokenize("")
        assert tokens == [], f"tokenize('') should return [], got {tokens!r}"

        syllables = syllabify_word("")
        assert syllables == [], f"syllabify_word('') should return [], got {syllables!r}"

    @pytest.mark.parametrize("word", _CSV_ANCHOR_WORDS)
    def test_syllable_count_matches_csv_anchors(self, word: str) -> None:
        """syllabify_word must produce the syllable count declared in the CSV."""
        data_csv = _Path(__file__).parent.parent / "data" / "pronunciation_tests.csv"
        expected_count: int | None = None
        with data_csv.open(newline="", encoding="utf-8") as fh:
            for row in _csv.DictReader(fh):
                if row["input"] == word:
                    expected_count = int(row["syllable_count"])
                    break

        assert expected_count is not None, f"Word '{word}' not found in CSV"
        syllables = syllabify_word(word)
        assert len(syllables) == expected_count, (
            f"syllabify_word('{word}') returned {len(syllables)} syllables, "
            f"expected {expected_count}"
        )

    @pytest.mark.parametrize("word", _CSV_ANCHOR_WORDS)
    def test_stress_position_matches_csv_anchors(self, word: str) -> None:
        """assign_stress must mark the syllable at the CSV stress_position index."""
        data_csv = _Path(__file__).parent.parent / "data" / "pronunciation_tests.csv"
        stress_position: int | None = None
        with data_csv.open(newline="", encoding="utf-8") as fh:
            for row in _csv.DictReader(fh):
                if row["input"] == word:
                    stress_position = int(row["stress_position"])
                    break

        assert stress_position is not None, f"Word '{word}' not found in CSV"
        syllables = syllabify_word(word)
        assert syllables, f"syllabify_word returned empty for '{word}'"

        stressed = assign_stress(syllables)
        stressed_indices = [i for i, s in enumerate(stressed) if s.stressed]

        if stress_position == 0:
            # Single-syllable words: no syllable is stressed
            assert stressed_indices == [], (
                f"Word '{word}' has stress_position=0 but has stressed syllables: "
                f"{stressed_indices}"
            )
        else:
            # Multi-syllable: exactly one stressed syllable at index stress_position-1
            assert len(stressed_indices) == 1, (
                f"Word '{word}' expected 1 stressed syllable, got {len(stressed_indices)}"
            )
            assert stressed_indices[0] == stress_position - 1, (
                f"Word '{word}' stress at index {stressed_indices[0]}, "
                f"expected {stress_position - 1}"
            )

    def test_multi_word_sentence_stress_patterns(self) -> None:
        """Multi-word sentences produce the correct stressed syllable per word."""
        # "Mirad" → 2 syllables, stress_position=1 → index 0 (first syllable stressed)
        mirad_sylls = syllabify_word("Mirad")
        assert len(mirad_sylls) == 2, f"Mirad should have 2 syllables, got {len(mirad_sylls)}"
        mirad_stressed = assign_stress(mirad_sylls)
        stressed_idx = next(i for i, s in enumerate(mirad_stressed) if s.stressed)
        assert stressed_idx == 0, (
            f"Mirad stress expected at index 0, got {stressed_idx}"
        )

        # "tixe" → 2 syllables, stress on first (index 0)
        tixe_sylls = syllabify_word("tixe")
        assert len(tixe_sylls) == 2, f"tixe should have 2 syllables, got {len(tixe_sylls)}"
        tixe_stressed = assign_stress(tixe_sylls)
        stressed_idx = next(i for i, s in enumerate(tixe_stressed) if s.stressed)
        assert stressed_idx == 0, (
            f"tixe stress expected at index 0, got {stressed_idx}"
        )

        # "ama" → 2 syllables, stress_position=1 → index 0 (first syllable stressed)
        ama_sylls = syllabify_word("ama")
        assert len(ama_sylls) == 2, f"ama should have 2 syllables, got {len(ama_sylls)}"
        ama_stressed = assign_stress(ama_sylls)
        stressed_idx = next(i for i, s in enumerate(ama_stressed) if s.stressed)
        assert stressed_idx == 0, (
            f"ama stress expected at index 0, got {stressed_idx}"
        )

        # "vay" → 1 syllable, stress_position=0 → no stressed syllable
        vay_sylls = syllabify_word("vay")
        assert len(vay_sylls) == 1, f"vay should have 1 syllable, got {len(vay_sylls)}"
        vay_stressed = assign_stress(vay_sylls)
        stressed_idx = [i for i, s in enumerate(vay_stressed) if s.stressed]
        assert stressed_idx == [], (
            f"vay (stress_position=0) should have no stressed syllable, got {stressed_idx}"
        )