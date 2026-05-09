<<<<<<< HEAD
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
=======
from mirad_tts.syllabify import assign_stress, syllabify_word


class TestNucleiExtraction:
    def test_simple_vowels(self):
        syllables = syllabify_word("ama")
        assert ["a", "ma"] == [s.text for s in syllables]

    def test_complex_vowel_single_nucleus(self):
        syllables = syllabify_word("ayma")
        assert ["ay", "ma"] == [s.text for s in syllables]

    def test_adjacent_simple_vowels_two_nuclei(self):
        syllables = syllabify_word("booka")
        assert ["bo", "o", "ka"] == [s.text for s in syllables]


class TestGrammarAnchors:
    def test_tejna(self):
        assert ["te", "jna"] == [s.text for s in syllabify_word("tejna")]

    def test_mirad(self):
        assert ["Mi", "rad"] == [s.text for s in syllabify_word("Mirad")]

    def test_igay(self):
        assert ["i", "gay"] == [s.text for s in syllabify_word("igay")]


class TestStressAssignment:
    def test_igay(self):
        stressed = assign_stress(syllabify_word("igay"))
        assert [True, False] == [s.stressed for s in stressed]

    def test_mirad(self):
        stressed = assign_stress(syllabify_word("Mirad"))
        assert [True, False] == [s.stressed for s in stressed]

    def test_booka(self):
        stressed = assign_stress(syllabify_word("booka"))
        assert [False, True, False] == [s.stressed for s in stressed]

    def test_akea(self):
        stressed = assign_stress(syllabify_word("akea"))
        assert [False, True, False] == [s.stressed for s in stressed]

    def test_byoskyin(self):
        stressed = assign_stress(syllabify_word("byoskyin"))
        assert [True, False] == [s.stressed for s in stressed]

    def test_single_syllable_has_no_stress(self):
        stressed = assign_stress(syllabify_word("vay"))
        assert [False] == [s.stressed for s in stressed]


# ---------------------------------------------------------------------------
# Edge-case tests for gap-based onset-first maximal onset principle.
# Covers: multi-character gaps, r/l liquid handling, nasal+sibilant patterns,
# complex vowel + consonant clusters, and adjacent nuclei per the Mirad
# phonotactic pattern (C)[LG]A(Y)(L)(C).
# ---------------------------------------------------------------------------


class TestMultiCharacterGaps:
    """Two-consonant gaps handled by gap[:-1]→coda, gap[-1]→carry_onset."""

    def test_two_char_gap_second_not_rl(self):
        # "eynx" — A(Y)N(C)[sx] pattern; nasal coda + sibilant carry to onset.
        # gap="nx" (len=2), last="x" not r/l → coda="n", carry_onset="x".
        syllables = syllabify_word("eynx")
        assert ["eyn", "x"] == [s.text for s in syllables]
        # Note: eynx has only 1 nucleus so only 1 syllable with stress=False
        stressed = assign_stress(syllables)
        assert [False] == [s.stressed for s in stressed]

    def test_two_char_gap_first_is_rl_second_is_consonant(self):
        # "valdna" — gap "ld" where first char is l (r/l liquid).
        # Per algorithm: last="d" not in r/l → carry_onset="d", coda="l".
        syllables = syllabify_word("valdna")
        assert ["val", "dna"] == [s.text for s in syllables]

    def test_two_char_gap_last_is_rl(self):
        # "ayndla" — gap "dl" where last char is l (r/l liquid).
        # Per algorithm: last="l" in r/l → coda="dl", no carry_onset.
        syllables = syllabify_word("ayndla")
        assert ["ayn", "dla"] == [s.text for s in syllables]
        assert [True, False] == [s.stressed for s in assign_stress(syllables)]

    def test_complex_vowel_then_two_char_gap(self):
        # "eynlax" — complex vowel "ey" then gap "nl" (n not r/l).
        # gap[:-1]="n"→coda, gap[-1]="l"→carry_onset.
        syllables = syllabify_word("eynlax")
        assert ["eyn", "lax"] == [s.text for s in syllables]
        assert [True, False] == [s.stressed for s in assign_stress(syllables)]


class TestAdjacentNucleiAndComplexVowel:
    """Adjacent nuclei and complex vowel + simple vowel edge cases."""

    def test_adjacent_simple_vowels(self):
        # "booka" — adjacent "oo" (nuclei at indices 1 and 2 with no gap).
        syllables = syllabify_word("booka")
        assert ["bo", "o", "ka"] == [s.text for s in syllables]
        assert [False, True, False] == [s.stressed for s in assign_stress(syllables)]

    def test_complex_vowel_adjacent_simple_vowel(self):
        # "vyaa" — complex vowel "vy" then adjacent simple vowel "a" then "a".
        # First gap empty (adjacent vy+a), second gap empty (adjacent a+a).
        syllables = syllabify_word("vyaa")
        assert ["vya", "a"] == [s.text for s in syllables]

    def test_complex_vowel_two_char_gap(self):
        # "byoskyin" — complex vowel "byo", then gap "sk" (s not r/l).
        syllables = syllabify_word("byoskyin")
        assert ["byos", "kyin"] == [s.text for s in syllables]

    def test_complex_vowel_one_char_gap(self):
        # "alayn" — complex vowel "ay", then single-char gap "l" → coda.
        syllables = syllabify_word("alayn")
        assert ["al", "ayn"] == [s.text for s in syllables]
        assert [True, False] == [s.stressed for s in assign_stress(syllables)]


class TestOnsetCodaStructure:
    """Verify onset/coda structure for multi-character-gap syllables."""

    def test_eynx_onset_coda(self):
        # "eyn" syllable: onset="" (empty), coda="n" (from gap[:-1]).
        # "x" syllable: onset="x" (carry_onset), coda="".
        syllables = syllabify_word("eynx")
        syl = syllables
        assert syl[0].onset == ""
        assert syl[0].coda == "n"
        assert syl[1].onset == "x"
        assert syl[1].coda == ""

    def test_ayndla_onset_coda(self):
        # "ayndla": gap="dl", last="l" in r/l → coda="dl", no carry.
        syllables = syllabify_word("ayndla")
        syl = syllables
        assert syl[0].coda == "n"
        assert syl[1].onset == ""

    def test_eynlax_onset_coda(self):
        # gap="nl", last="l" not r/l → coda="n", carry_onset="l".
        syllables = syllabify_word("eynlax")
        syl = syllables
        assert syl[0].coda == "n"
        assert syl[1].onset == "l"

    def test_valdna_onset_coda(self):
        # gap="ld", last="d" not r/l → coda="l", carry_onset="d".
        syllables = syllabify_word("valdna")
        syl = syllables
        assert syl[0].coda == "l"
        assert syl[1].onset == "d"
>>>>>>> milestone/M001
