"""Tests for phonology constants."""

import pytest

from mirad_tts.phonology import (
    COMPLEX_VOWEL_STARTS,
    COMPLEX_VOWELS,
    CONSONANT_IPA,
    SIMPLE_VOWELS,
)


class TestCONSONANT_IPA:
    """Tests for the CONSONANT_IPA mapping."""

    def test_r_maps_to_alveolar_flap(self):
        """r → ɾ (alveolar flap, not trill) per Mirad Grammar spec."""
        assert CONSONANT_IPA["r"] == "ɾ"

    def test_x_maps_to_postalveolar_fricative(self):
        """x → ʃ (post-alveolar fricative, not /ks/) per spec."""
        assert CONSONANT_IPA["x"] == "ʃ"

    def test_j_maps_to_voiced_palatal_fricative(self):
        """j → ʒ (voiced palatal fricative, not English j)."""
        assert CONSONANT_IPA["j"] == "ʒ"

    def test_c_maps_to_affricate(self):
        """c → t͡ʃ (unvoiced palato-alveolar affricate, used in foreign words)."""
        assert CONSONANT_IPA["c"] == "t͡ʃ"

    def test_bilabial_plosives(self):
        assert CONSONANT_IPA["p"] == "p"
        assert CONSONANT_IPA["b"] == "b"

    def test_alveolar_plosives(self):
        assert CONSONANT_IPA["t"] == "t"
        assert CONSONANT_IPA["d"] == "d"

    def test_velar_plosives(self):
        assert CONSONANT_IPA["k"] == "k"
        assert CONSONANT_IPA["g"] == "ɡ"

    def test_glottals(self):
        assert CONSONANT_IPA["h"] == "h"

    def test_nasals(self):
        assert CONSONANT_IPA["m"] == "m"
        assert CONSONANT_IPA["n"] == "n"

    def test_lateral(self):
        assert CONSONANT_IPA["l"] == "l"

    def test_glides(self):
        assert CONSONANT_IPA["w"] == "w"
        assert CONSONANT_IPA["y"] == "j"

    def test_fricatives(self):
        assert CONSONANT_IPA["f"] == "f"
        assert CONSONANT_IPA["v"] == "v"
        assert CONSONANT_IPA["s"] == "s"
        assert CONSONANT_IPA["z"] == "z"


class TestSimpleVowels:
    """Tests for the SIMPLE_VOWELS set."""

    def test_contains_five_vowels(self):
        """Mirad's simple vowels are a, e, i, o, u (y is not a simple vowel)."""
        assert SIMPLE_VOWELS == frozenset("aeiou")

    def test_y_not_in_simple_vowels(self):
        """y acts as a glide, not a simple vowel, even though it can appear in vowel contexts."""
        assert "y" not in SIMPLE_VOWELS


class TestComplexVowels:
    """Tests for the COMPLEX_VOWELS mapping."""

    @pytest.fixture
    def required_vowels(self):
        """Core complex vowel pairs that must be present."""
        return ["ay", "ey", "aw", "ew", "iw", "ow"]

    def test_required_vowels_present(self, required_vowels):
        """At minimum, the six primary post-y-glided and post-w-glided vowels exist."""
        for vowel in required_vowels:
            assert vowel in COMPLEX_VOWELS, f"Required complex vowel {vowel!r} missing"

    def test_post_y_glided_ipa(self):
        """Post-y-glided vowels map to the IPA diphthongs from the grammar."""
        assert COMPLEX_VOWELS["ay"] == "aɪ"
        assert COMPLEX_VOWELS["ey"] == "eɪ"
        assert COMPLEX_VOWELS["oy"] == "oɪ"

    def test_post_w_glided_ipa(self):
        """Post-w-glided vowels map to their IPA values from the grammar."""
        assert COMPLEX_VOWELS["aw"] == "ɔ"
        assert COMPLEX_VOWELS["ew"] == "ɛʊ"
        assert COMPLEX_VOWELS["iw"] == "iʊ"
        assert COMPLEX_VOWELS["ow"] == "oʊ"

    def test_pre_y_glided_vowels(self):
        """Pre-y-glided (yi, ye, etc.) are all present."""
        pre_y = ["ya", "ye", "yi", "yo", "yu"]
        for v in pre_y:
            assert v in COMPLEX_VOWELS, f"Missing pre-y-glided vowel {v!r}"

    def test_pre_w_glided_vowels(self):
        """Pre-w-glided (wa, we, etc.) are all present."""
        pre_w = ["wa", "we", "wi", "wo", "wu"]
        for v in pre_w:
            assert v in COMPLEX_VOWELS, f"Missing pre-w-glided vowel {v!r}"

    def test_circum_y_glided_vowels(self):
        """Circum-y-glided (yay, yey, etc.) are all present."""
        circum = ["yay", "yey", "yiy", "yoy", "yuy"]
        for v in circum:
            assert v in COMPLEX_VOWELS, f"Missing circum-y-glided vowel {v!r}"

    def test_pre_w_post_y_glided_vowels(self):
        """Pre-w-post-y-glided (way, wey, etc.) are all present."""
        pre_w_y = ["way", "wey", "wiy", "woy", "wuy"]
        for v in pre_w_y:
            assert v in COMPLEX_VOWELS, f"Missing pre-w-post-y-glided vowel {v!r}"

    def test_all_two_or_three_chars(self):
        """Every complex vowel key is 2 or 3 characters long."""
        for key in COMPLEX_VOWELS:
            assert len(key) in (2, 3), f"Complex vowel {key!r} has unexpected length {len(key)}"


class TestComplexVowelStarts:
    """Tests for the COMPLEX_VOWEL_STARTS set."""

    def test_all_start_chars_valid(self):
        """Every COMPLEX_VOWEL_STARTS character is either a simple vowel or y/w."""
        valid_chars = SIMPLE_VOWELS | frozenset("wy")
        assert COMPLEX_VOWEL_STARTS <= valid_chars

    def test_covers_all_first_chars_of_complex_vowels(self):
        """The start set covers every first character of all complex vowel keys."""
        first_chars = frozenset(v[0] for v in COMPLEX_VOWELS)
        assert first_chars <= COMPLEX_VOWEL_STARTS

    def test_y_and_w_in_starts(self):
        """y and w (glide prefixes) are in the start set."""
        assert "y" in COMPLEX_VOWEL_STARTS
        assert "w" in COMPLEX_VOWEL_STARTS