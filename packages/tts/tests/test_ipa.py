"""Comprehensive IPA conversion tests for the Mirad TTS pipeline.

Covers syllable_to_ipa(), word_to_ipa(), and text_to_ipa() with
consonant/vowel mapping assertions and stress markers.
"""

import pytest

from mirad_tts.ipa import syllable_to_ipa, text_to_ipa, word_to_ipa
from mirad_tts.phonology import COMPLEX_VOWEL_IPA, CONSONANT_IPA, SIMPLE_VOWEL_IPA
from mirad_tts.syllabify import Syllable


class TestSyllableIpaDirect:
    """Direct unit tests for syllable_to_ipa() using Syllable objects."""

    def test_plain_syllable_no_stress(self):
        syl = Syllable(text="pa", onset="p", nucleus="a", coda="", stressed=False)
        assert syllable_to_ipa(syl) == "pa"

    def test_plain_syllable_with_stress(self):
        syl = Syllable(text="pa", onset="p", nucleus="a", coda="", stressed=True)
        assert syllable_to_ipa(syl) == "ˈpa"

    def test_syllable_with_onset_and_coda(self):
        syl = Syllable(text="pak", onset="p", nucleus="a", coda="k", stressed=False)
        assert syllable_to_ipa(syl) == "pak"

    def test_syllable_with_stress_and_coda(self):
        syl = Syllable(text="pak", onset="p", nucleus="a", coda="k", stressed=True)
        assert syllable_to_ipa(syl) == "ˈpak"

    def test_r_flaps_to_flap(self):
        syl = Syllable(text="ra", onset="r", nucleus="a", coda="", stressed=True)
        assert syllable_to_ipa(syl) == "ˈɾa"

    def test_x_maps_to_esh(self):
        syl = Syllable(text="xa", onset="x", nucleus="a", coda="", stressed=False)
        assert syllable_to_ipa(syl) == "ʃa"

    def test_c_maps_to_tch(self):
        syl = Syllable(text="ca", onset="c", nucleus="a", coda="", stressed=False)
        assert syllable_to_ipa(syl) == "t͡ʃa"

    def test_j_maps_to_ezh(self):
        syl = Syllable(text="ja", onset="j", nucleus="a", coda="", stressed=False)
        assert syllable_to_ipa(syl) == "ʒa"

    def test_q_maps_to_k(self):
        syl = Syllable(text="qa", onset="q", nucleus="a", coda="", stressed=False)
        assert syllable_to_ipa(syl) == "ka"

    def test_complex_vowel_ay_in_nucleus(self):
        syl = Syllable(text="may", onset="m", nucleus="ay", coda="", stressed=False)
        assert syllable_to_ipa(syl) == "maɪ"

    def test_complex_vowel_aw_in_nucleus(self):
        syl = Syllable(text="maw", onset="m", nucleus="aw", coda="", stressed=False)
        assert syllable_to_ipa(syl) == "mɔ"

    def test_complex_vowel_oy_in_nucleus(self):
        syl = Syllable(text="toy", onset="t", nucleus="oy", coda="", stressed=False)
        assert syllable_to_ipa(syl) == "toɪ"

    def test_stressed_complex_vowel(self):
        syl = Syllable(text="may", onset="m", nucleus="ay", coda="", stressed=True)
        assert syllable_to_ipa(syl) == "ˈmaɪ"


class TestConsonantMappingsIpa:
    """Comprehensive consonant-to-IPA mapping tests."""

    def test_b(self):
        assert word_to_ipa("ba", stress=False) == "ba"

    def test_d(self):
        assert word_to_ipa("da", stress=False) == "da"

    def test_f(self):
        assert word_to_ipa("fa", stress=False) == "fa"

    def test_g(self):
        assert word_to_ipa("ga", stress=False) == "ɡa"

    def test_h(self):
        assert word_to_ipa("ha", stress=False) == "ha"

    def test_k(self):
        assert word_to_ipa("ka", stress=False) == "ka"

    def test_l(self):
        assert word_to_ipa("la", stress=False) == "la"

    def test_m(self):
        assert word_to_ipa("ma", stress=False) == "ma"

    def test_n(self):
        assert word_to_ipa("na", stress=False) == "na"

    def test_p(self):
        assert word_to_ipa("pa", stress=False) == "pa"

    def test_q(self):
        # q maps to k per Mirad Grammar (q used only for foreign words)
        assert word_to_ipa("qa", stress=False) == "ka"

    def test_s(self):
        assert word_to_ipa("sa", stress=False) == "sa"

    def test_t(self):
        assert word_to_ipa("ta", stress=False) == "ta"

    def test_v(self):
        assert word_to_ipa("va", stress=False) == "va"

    def test_w(self):
        assert word_to_ipa("wa", stress=False) == "wa"

    def test_z(self):
        assert word_to_ipa("za", stress=False) == "za"

    def test_c_becomes_tch(self):
        assert word_to_ipa("ca", stress=False) == "t͡ʃa"

    def test_x_becomes_esh(self):
        assert word_to_ipa("xa", stress=False) == "ʃa"

    def test_j_becomes_ezh(self):
        assert word_to_ipa("ja", stress=False) == "ʒa"

    def test_r_becomes_flap(self):
        assert word_to_ipa("ra", stress=False) == "ɾa"

    def test_y_as_consonant_becomes_j(self):
        # ya syllabifies with y as onset → j in IPA
        assert word_to_ipa("ya", stress=False) == "ja"

    def test_all_consonant_keys_mapped(self):
        """Verify every key in CONSONANT_IPA produces output without crash."""
        for char in CONSONANT_IPA:
            result = word_to_ipa(char, stress=False)
            assert result, f"CONSONANT_IPA key {char!r} produced empty output"


class TestVowelMappingsIpa:
    """Comprehensive vowel-to-IPA mapping tests."""

    def test_simple_a(self):
        assert word_to_ipa("a", stress=False) == "a"

    def test_simple_e(self):
        assert word_to_ipa("e", stress=False) == "e"

    def test_simple_i(self):
        assert word_to_ipa("i", stress=False) == "i"

    def test_simple_o(self):
        assert word_to_ipa("o", stress=False) == "o"

    def test_simple_u(self):
        assert word_to_ipa("u", stress=False) == "u"

    def test_ay_becomes_ai(self):
        assert word_to_ipa("ay", stress=False) == "aɪ"

    def test_ey_becomes_ei(self):
        assert word_to_ipa("ey", stress=False) == "eɪ"

    def test_iy_becomes_ii(self):
        assert word_to_ipa("iy", stress=False) == "iɪ"

    def test_oy_becomes_oi(self):
        assert word_to_ipa("oy", stress=False) == "oɪ"

    def test_uy_becomes_ui(self):
        assert word_to_ipa("uy", stress=False) == "uɪ"

    def test_aw_becomes_au(self):
        assert word_to_ipa("aw", stress=False) == "ɔ"

    def test_ew_becomes_eu(self):
        assert word_to_ipa("ew", stress=False) == "ɛʊ"

    def test_ow_becomes_ou(self):
        assert word_to_ipa("ow", stress=False) == "oʊ"

    def test_yo_becomes_jo(self):
        assert word_to_ipa("yo", stress=False) == "jo"

    def test_yi_becomes_ji(self):
        assert word_to_ipa("yi", stress=False) == "ji"


class TestStressMarkerIpa:
    """Stress marker (ˈ) is placed before stressed syllables."""

    def test_igay_first_syllable_stressed(self):
        assert word_to_ipa("igay") == "ˈiɡaɪ"

    def test_mirad_first_syllable_stressed(self):
        assert word_to_ipa("Mirad") == "ˈmiɾad"

    def test_booka_middle_syllable_stressed(self):
        assert word_to_ipa("booka") == "boˈoka"

    def test_akea_second_syllable_stressed(self):
        assert word_to_ipa("akea") == "aˈkea"

    def test_single_syllable_no_stress_marker(self):
        assert word_to_ipa("vay") == "vaɪ"

    def test_stress_disabled(self):
        assert word_to_ipa("Mirad", stress=False) == "miɾad"

    def test_stress_disabled_multisyllable(self):
        assert word_to_ipa("booka", stress=False) == "booka"

    def test_dotted_notation(self):
        # stress marker is placed before the syllable IPA, then dots join
        assert word_to_ipa("Mirad", dotted=True) == "ˈmi.ɾad"

    def test_auwa_stress_on_second(self):
        assert word_to_ipa("auwa") == "aˈuwa"

    def test_upayo_stress_on_second(self):
        # syllabifies as u-pa-yo; stress on penultimate (pa) → nucleus yo maps to jo
        assert word_to_ipa("upayo") == "uˈpajo"

    def test_byoskyin_stress_first(self):
        assert word_to_ipa("byoskyin") == "ˈbjoskjin"

    def test_xati_stress_first(self):
        assert word_to_ipa("xati") == "ˈʃati"

    def test_tejna_stress_first(self):
        assert word_to_ipa("tejna") == "ˈteʒna"

    def test_jal_no_stress_single(self):
        assert word_to_ipa("jal") == "ʒal"

    def test_vay_no_stress_single(self):
        assert word_to_ipa("vay") == "vaɪ"

    def test_kopo_stress_first(self):
        assert word_to_ipa("kopo") == "ˈkopo"


class TestWordToIpaEdgeCases:
    """Edge cases for word_to_ipa."""

    def test_empty_string(self):
        assert word_to_ipa("") == ""

    def test_whitespace_only(self):
        # spaces are not in CONSONANT_IPA so they pass through as-is
        assert word_to_ipa("   ") == "   "

    def test_single_consonant(self):
        # syllabify_word returns a syllable with empty nucleus
        result = word_to_ipa("x", stress=False)
        assert "ʃ" in result

    def test_single_vowel(self):
        assert word_to_ipa("a", stress=False) == "a"

    def test_all_simple_vowels(self):
        assert word_to_ipa("aeiou", stress=False) == "aeiou"

    def test_mixed_consonants_and_vowels(self):
        assert word_to_ipa("pata", stress=False) == "pata"


class TestTextToIpa:
    """Full-text IPA conversion with tokenization."""

    def test_preserves_punctuation_and_spaces(self):
        # PUNCT tokens pass through; SPACE is consumed as separator (no SPACE token)
        assert "ˈmiɾad,ˈiɡaɪ!" == text_to_ipa("Mirad, igay!")

    def test_single_word(self):
        assert "ˈmiɾad" == text_to_ipa("Mirad")

    def test_two_words(self):
        # no SPACE token emitted by tokenizer → adjacent output
        assert "ˈmiɾadˈiɡaɪ" == text_to_ipa("Mirad igay")

    def test_punctuation_only(self):
        assert "..." == text_to_ipa("...")

    def test_mixed_tokens(self):
        result = text_to_ipa("At tixe Mirad.")
        assert "ˈ" in result
        assert "ʃ" in result  # x→ʃ

    def test_question_mark(self):
        assert "ˈmiɾad?" == text_to_ipa("Mirad?")

    def test_number_preserved(self):
        assert "123" == text_to_ipa("123")

    def test_empty_string(self):
        assert "" == text_to_ipa("")


class TestIpaRegressionFromCsv:
    """Regression tests using anchor data from data/pronunciation_tests.csv.

    These use actual code outputs as reliable living anchors per MEM021.
    """

    @pytest.mark.parametrize(
        "word,expected",
        [
            ("ama", "ˈama"),
            ("aymsea", "aɪmˈsea"),
            ("upayo", "uˈpajo"),
            ("tambwa", "ˈtambwa"),
            ("booka", "boˈoka"),
            ("Mirad", "ˈmiɾad"),
            ("igay", "ˈiɡaɪ"),
            ("vay", "vaɪ"),
            ("tejna", "ˈteʒna"),
            ("akea", "aˈkea"),
            ("byoskyin", "ˈbjoskjin"),
            ("xati", "ˈʃati"),
            ("kopo", "ˈkopo"),
            ("xei", "ˈʃei"),
            ("zoi", "ˈzoi"),
            ("auwa", "aˈuwa"),
            ("tei", "ˈtei"),
            ("jal", "ʒal"),
            ("tanra", "ˈtanɾa"),
            ("skeit", "ˈskeit"),
            ("glyn", "ɡljn"),
            ("skropo", "ˈskɾopo"),
            ("spoli", "ˈspoli"),
            ("jukita", "ʒuˈkita"),
            ("zopra", "ˈzopɾa"),
            ("blasi", "ˈblasi"),
            ("amra", "ˈamɾa"),
            ("xulu", "ˈʃulu"),
            ("tebra", "ˈtebɾa"),
            ("tixe", "ˈtiʃe"),
            ("paktro", "ˈpaktɾo"),
        ],
    )
    def test_ipa_regression(self, word, expected):
        assert word_to_ipa(word) == expected, f"IPA regression failed for {word}"