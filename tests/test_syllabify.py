"""Tests for the syllabification engine.

Grammar anchor examples from the Mirad Grammar "Syllabification" chart:
    ama, ayma, aymsea, pixwa, upayo, vyaa, vyaay, vay, tambwa

Roadmap case: booka → bo-o-ka
"""

from __future__ import annotations

import pytest

from mirad_tts.syllabify import (
    Syllable,
    _find_nuclei,
    assign_stress,
    syllabify,
    syllabify_word,
)


# ── Grammar anchor examples ───────────────────────────────────────────────────

GRAMMAR_CASES: list[tuple[str, list[str]]] = [
    # From the "Syllabification" chart (9 cases):
    ("ama",    ["a", "ma"]),
    ("ayma",   ["ay", "ma"]),
    ("aymsea", ["aym", "se", "a"]),
    ("pixwa",  ["pix", "wa"]),
    ("upayo",  ["u", "pa", "yo"]),
    ("vyaa",   ["vya", "a"]),
    ("vyaay",  ["vya", "ay"]),
    ("vay",    ["vay"]),
    ("tambwa", ["tam", "bwa"]),
    # Roadmap case:
    ("booka",  ["bo", "o", "ka"]),
]


class TestGrammarAnchorExamples:
    """All 9 grammar anchor cases from Mirad_grammer.md 'Syllabification' chart."""

    @pytest.mark.parametrize("word,expected", GRAMMAR_CASES)
    def test_syllabify_exact_match(self, word: str, expected: list[str]) -> None:
        assert syllabify(word) == expected

    @pytest.mark.parametrize("word,expected", GRAMMAR_CASES)
    def test_syllabify_word_exact_match(self, word: str, expected: list[str]) -> None:
        syllables = syllabify_word(word)
        assert [s.text for s in syllables] == expected

    @pytest.mark.parametrize("word,expected", GRAMMAR_CASES)
    def test_count(self, word: str, expected: list[str]) -> None:
        assert len(syllabify(word)) == len(expected)


class TestSyllableDataclass:
    """Syllable objects are frozen/slots and expose correct fields."""

    def test_frozen(self) -> None:
        syl = Syllable(text="aym", onset="", nucleus="aym", coda="")
        with pytest.raises(AttributeError):
            syl.text = "other"  # type: ignore[assignment]

    def test_slots(self) -> None:
        syl = Syllable(text="aym", onset="", nucleus="aym", coda="")
        # If slots=True, __dict__ is absent.
        assert not hasattr(syl, "__dict__")

    def test_fields(self) -> None:
        syl = Syllable(text="pix", onset="p", nucleus="i", coda="x")
        assert syl.text == "pix"
        assert syl.onset == "p"
        assert syl.nucleus == "i"
        assert syl.coda == "x"

    def test_repr(self) -> None:
        syl = Syllable(text="pix", onset="p", nucleus="i", coda="x")
        r = repr(syl)
        assert "text='pix'" in r
        assert "onset='p'" in r
        assert "nucleus='i'" in r
        assert "coda='x'" in r
        assert "stressed=" in r

    def test_stressed_field_default_false(self) -> None:
        syl = Syllable(text="pix", onset="p", nucleus="i", coda="x")
        assert syl.stressed is False


class TestNucleusDetection:
    """Complex vowels are matched as single nuclei; adjacent simple vowels split."""

    def test_simple_vowels(self) -> None:
        # ama: nuclei at positions 0 and 2 ('a' at idx 0, 'a' at idx 2)
        assert _find_nuclei("ama") == [(0, 1), (2, 3)]

    def test_complex_vowel_single_nucleus(self) -> None:
        # ayma: "ay" at (0,2), 'a' at (3,4)
        assert _find_nuclei("ayma") == [(0, 2), (3, 4)]

    def test_three_char_circumglided(self) -> None:
        # yay is one nucleus.
        assert _find_nuclei("yay") == [(0, 3)]

    def test_adjacent_simple_vowels_two_nuclei(self) -> None:
        # ay + m + a → nuclei at "ay" and "a" only.
        assert _find_nuclei("ayma") == [(0, 2), (3, 4)]


class TestStressSectionCrossCheck:
    """Stress-section examples are also valid syllabifications."""

    def test_igay(self) -> None:
        # ay is one complex vowel, not two nuclei.
        assert syllabify("igay") == ["i", "gay"]

    def test_alayn(self) -> None:
        # layn: l is codaable → a-layn (l closes first syllable)
        assert syllabify("alayn") == ["al", "ayn"]

    def test_tejna(self) -> None:
        # j is onset (not r/l), not coda → te-jna
        assert syllabify("tejna") == ["te", "jna"]

    def test_akea(self) -> None:
        assert syllabify("akea") == ["a", "ke", "a"]

    def test_oyse(self) -> None:
        # oy is one nucleus.
        assert syllabify("oyse") == ["oy", "se"]

    def test_bookan(self) -> None:
        # bookan → bo-o-kan
        assert syllabify("bookan") == ["bo", "o", "kan"]


class TestStressAssignment:
    """Stress falls on the last non-final syllable per Mirad Grammar."""

    def test_two_syllables_igay(self) -> None:
        # igay → i-gay, stress on first (index 0)
        syllables = syllabify_word("igay")
        stressed = assign_stress(syllables)
        assert [s.stressed for s in stressed] == [True, False]

    def test_two_syllables_mirad(self) -> None:
        # Mirad → Mi-rad, stress on first (index 0)
        syllables = syllabify_word("Mirad")
        stressed = assign_stress(syllables)
        assert [s.stressed for s in stressed] == [True, False]
        assert [s.text for s in stressed] == ["Mi", "rad"]

    def test_three_syllables_booka(self) -> None:
        # booka → bo-o-ka, stress on middle (index 1)
        syllables = syllabify_word("booka")
        stressed = assign_stress(syllables)
        assert [s.stressed for s in stressed] == [False, True, False]

    def test_three_syllables_akea(self) -> None:
        # akea → a-ke-a, stress on middle (index 1)
        syllables = syllabify_word("akea")
        stressed = assign_stress(syllables)
        assert [s.stressed for s in stressed] == [False, True, False]

    def test_two_syllables_byoskyin(self) -> None:
        # byoskyin → byos-kyin, stress on first (index 0)
        syllables = syllabify_word("byoskyin")
        stressed = assign_stress(syllables)
        assert [s.stressed for s in stressed] == [True, False]
        assert [s.text for s in stressed] == ["byos", "kyin"]

    def test_single_syllable_vay(self) -> None:
        # vay → single syllable, no stress
        syllables = syllabify_word("vay")
        stressed = assign_stress(syllables)
        assert [s.stressed for s in stressed] == [False]

    def test_stress_preserves_other_fields(self) -> None:
        syllables = syllabify_word("Mirad")
        stressed = assign_stress(syllables)
        # Check that onset/nucleus/coda are preserved
        assert stressed[0].text == "Mi"
        assert stressed[0].onset == "M"
        assert stressed[0].nucleus == "i"
        assert stressed[0].coda == ""
        assert stressed[0].stressed is True


class TestEdgeCases:
    """Empty input and single-syllable words."""

    def test_empty_string(self) -> None:
        assert syllabify("") == []
        assert syllabify_word("") == []

    def test_single_syllable(self) -> None:
        assert syllabify("vay") == ["vay"]

    def test_single_syllable_word(self) -> None:
        syl = syllabify_word("vay")[0]
        assert syl.text == "vay"
        assert syl.onset == "v"
        assert syl.nucleus == "ay"
        assert syl.coda == ""

    def test_consonant_only_word_no_vowels(self) -> None:
        # Shouldn't occur in Mirad but must not crash.
        result = syllabify_word("xyz")
        assert len(result) == 1
        assert result[0].text == "xyz"