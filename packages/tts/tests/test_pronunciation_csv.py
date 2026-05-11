"""CSV-driven pronunciation validation tests.

Each row in data/pronunciation_tests.csv is a grammar-anchored pronunciation
anchor.  Tests verify that ``syllabify_word`` produces the syllable count
declared in the CSV and that ``assign_stress`` marks the correct syllable as
stressed.

When the ``ipa`` module is implemented, ``test_ipa_conversion`` should be
un-commented to validate IPA output.  When ``espeak_backend`` is implemented,
``test_espeak_phoneme_input`` should be un-commented.

CSV schema
----------
input,syllable_count,stress_position,expected_ipa,expected_espeak,notes

The espeak column stores the inner phoneme string (without the [[...]] wrapper);
the test reconstructs the full expected return value before comparing so the
double-bracket wrapper is always verified once the backend is available.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest


def _load_anchor_rows() -> list[dict[str, str]]:
    """Load all rows from the pronunciation anchor CSV."""
    data_csv = Path(__file__).parent.parent / "data" / "pronunciation_tests.csv"
    if not data_csv.exists():
        pytest.fail(f"Pronunciation anchor CSV not found: {data_csv}")

    rows: list[dict[str, str]] = []
    with data_csv.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for i, raw in enumerate(reader, start=2):
            if not raw.get("input", "").strip():
                pytest.fail(f"Row {i} in {data_csv} has an empty input field.")
            rows.append(dict(raw))

    if len(rows) < 30:
        pytest.fail(
            f"Expected at least 30 anchor rows, found {len(rows)} in {data_csv}."
        )
    return rows


_ANCHOR_ROWS = _load_anchor_rows()

# Convenience list of single-word input strings (excluding multi-word/sentence
# rows) for use in test_pipeline.py so both modules reference the same anchor set.
_CSV_ANCHOR_WORDS = [r["input"] for r in _ANCHOR_ROWS]


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Parametrize syllable-count and stress-position tests from the anchor CSV."""
    if metafunc.definition.name in (
        "test_syllable_count_from_csv",
        "test_stress_position_from_csv",
    ):
        metafunc.parametrize(
            "anchor",
            _ANCHOR_ROWS,
            ids=[r["input"] for r in _ANCHOR_ROWS],
        )


# ---------------------------------------------------------------------------
# IPA and espeak tests are commented out because the ipa and espeak_backend
# modules have not yet been implemented.  Un-comment when those modules exist.
# ---------------------------------------------------------------------------

# def test_ipa_conversion(anchor: dict[str, str]) -> None:
#     """Verify text_to_ipa produces the expected IPA string for every anchor row."""
#     from mirad_tts import text_to_ipa
#
#     raw_input = anchor["input"]
#     expected_ipa = anchor["expected_ipa"]
#     actual = text_to_ipa(raw_input)
#     stripped_actual = actual.replace(" ", "")
#     stripped_expected = expected_ipa.replace(" ", "")
#     if stripped_actual != stripped_expected:
#         pytest.fail(
#             f"IPA mismatch for input {raw_input!r}\n"
#             f"  expected (stripped): {stripped_expected!r}\n"
#             f"  actual   (stripped): {stripped_actual!r}\n"
#             f"  raw IPA output:      {actual!r}"
#         )


# def test_espeak_phoneme_input(anchor: dict[str, str]) -> None:
#     """Verify text_to_espeak_phoneme_input returns a non-empty [[...]]-wrapped string."""
#     from mirad_tts.espeak_backend import text_to_espeak_phoneme_input
#
#     raw_input = anchor["input"]
#     inner_phoneme = anchor["expected_espeak"]
#     actual = text_to_espeak_phoneme_input(raw_input)
#     expected_full = f"[[{inner_phoneme}]]"
#     if not actual:
#         pytest.fail(f"espeak returned empty string for input {raw_input!r}.")
#     if actual != expected_full:
#         pytest.fail(
#             f"espeak mismatch for input {raw_input!r}\n"
#             f"  expected: {expected_full!r}\n"
#             f"  actual:   {actual!r}"
#         )


def test_syllable_count_from_csv(anchor: dict[str, str]) -> None:
    """Verify syllabify_word returns the syllable_count declared in the CSV.

    This confirms that the CSV anchors accurately reflect pipeline behavior
    and serves as a regression test when syllable-boundary rules change.
    """
    from mirad_tts import assign_stress, syllabify_word

    word = anchor["input"]
    expected_count = int(anchor["syllable_count"])

    syllables = syllabify_word(word)
    if len(syllables) != expected_count:
        pytest.fail(
            f"Syllable count mismatch for '{word}': "
            f"syllabify_word returned {len(syllables)} syllables, "
            f"CSV declares {expected_count}."
        )

    # Also ensure assign_stress does not alter syllable count
    if len(syllables) > 0:
        stressed = assign_stress(syllables)
        assert len(stressed) == len(syllables), (
            f"assign_stress changed syllable count for '{word}'"
        )


def test_stress_position_from_csv(anchor: dict[str, str]) -> None:
    """Verify assign_stress marks the syllable at the stress_position declared in CSV.

    stress_position=0 means single-syllable / no stress.
    stress_position>=1 means multi-syllable; stress is 1-indexed from left.
    """
    from mirad_tts import assign_stress, syllabify_word

    word = anchor["input"]
    stress_position = int(anchor["stress_position"])

    syllables = syllabify_word(word)
    assert syllables, f"syllabify_word returned empty for '{word}'"

    stressed = assign_stress(syllables)
    stressed_indices = [i for i, s in enumerate(stressed) if s.stressed]

    if stress_position == 0:
        assert stressed_indices == [], (
            f"'{word}': stress_position=0 but stressed syllable(s) found at "
            f"indices {stressed_indices}."
        )
    else:
        assert len(stressed_indices) == 1, (
            f"'{word}': expected 1 stressed syllable, got {len(stressed_indices)} "
            f"at indices {stressed_indices}."
        )
        assert stressed_indices[0] == stress_position - 1, (
            f"'{word}': stressed at index {stressed_indices[0]}, "
            f"expected {stress_position - 1} (stress_position={stress_position})."
        )