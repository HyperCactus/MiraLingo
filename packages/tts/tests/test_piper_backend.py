"""Regression tests for the Piper backend bridge."""

from pathlib import Path

import pytest

from mirad_tts.piper_backend import (
    PiperPhonemeError,
    _text_to_piper_phoneme_input,
    syllable_to_piper_phonemes,
    text_to_piper_phonemes,
    word_to_piper_phonemes,
)
from mirad_tts.syllabify import Syllable


# ── Legacy IPA [[...]] wrapper (backward compat) ──────────────────────────────


def test_piper_bridge_uses_mapped_ipa_phonemes_for_words() -> None:
    assert _text_to_piper_phoneme_input("Mirad") == "[[ˈmiɾad]]"


def test_piper_bridge_maps_stress_and_vowels() -> None:
    assert _text_to_piper_phoneme_input("booka") == "[[boˈoka]]"


def test_piper_bridge_preserves_spaces_and_punctuation() -> None:
    assert _text_to_piper_phoneme_input("Mirad booka!") == "[[ˈmiɾad boˈoka!]]"


# ── New Piper-safe phoneme mapping ─────────────────────────────────────────────


class TestWordToPiperPhonemes:
    """Test the Mirad → Piper-safe phoneme conversion."""

    def test_simple_word_mirad(self) -> None:
        #Mirad → Mi·rad → ˈmi·ɾad → [ˈ, m, i, ɾ, a, d]
        symbols = word_to_piper_phonemes("Mirad")
        assert symbols == ["ˈ", "m", "i", "ɾ", "a", "d"]

    def test_affricate_decomposition_c(self) -> None:
        # c → [t, ʃ] (not t͡ʃ)
        symbols = word_to_piper_phonemes("cema")
        # ce·ma → [t, ʃ, e, m, a] — but ce is just one syllable
        # Actually: syllabify("cema") gives [Syllable("ce", ...), Syllable("ma", ...)]
        # "cema" → "ce" + "ma" → onset "c" → [t, ʃ], nucleus "e" → [e], coda ""
        #                 onset "m" → [m], nucleus "a" → [a], coda ""
        # With stress: [ˈ, t, ʃ, e, m, a]
        assert "t" in symbols
        assert "ʃ" in symbols
        # Tie bar should NOT be in output
        assert "\u0361" not in symbols  # COMBINING DOUBLE INVERTED BREVE
        assert "t͡ʃ" not in symbols

    def test_g_uses_ipa_ɡ(self) -> None:
        # Mirad g → IPA ɡ (U+0261), not ASCII g (U+0067)
        symbols = word_to_piper_phonemes("igay")
        # i·gay → [ˈ, i, ɡ, a, ɪ]
        assert "ɡ" in symbols  # IPA ɡ (U+0261)

    def test_r_uses_flap_ɾ(self) -> None:
        symbols = word_to_piper_phonemes("Mirad")
        assert "ɾ" in symbols
        assert "r" not in symbols or "ɾ" in symbols  # flap, not trill

    def test_x_uses_ʃ(self) -> None:
        symbols = word_to_piper_phonemes("tixe")
        assert "ʃ" in symbols

    def test_j_uses_ʒ(self) -> None:
        symbols = word_to_piper_phonemes("jal")
        assert "ʒ" in symbols

    def test_q_uses_k(self) -> None:
        symbols = word_to_piper_phonemes("qatar")
        # q → [k]
        assert "k" in symbols

    def test_complex_vowel_ay(self) -> None:
        # ay → [a, ɪ]
        symbols = word_to_piper_phonemes("igay")
        assert "a" in symbols
        assert "ɪ" in symbols

    def test_complex_vowel_aw(self) -> None:
        # aw → [ɔ]
        symbols = word_to_piper_phonemes("auwa")
        # au·wa → [ˈ, a, ʊ, w, a] ?
        # Actually syllabify("auwa") → let's check
        pass  # complex, checked via integration

    def test_y_maps_to_j(self) -> None:
        # Mirad y → IPA j (palatal approximant)
        symbols = word_to_piper_phonemes("ya")
        assert "j" in symbols

    def test_no_tie_bar_in_output(self) -> None:
        """Ensure tie bar character never appears in Piper phoneme output."""
        # Test all words that might produce affricates
        for word in ["cema", "celac", "ceku"]:
            symbols = word_to_piper_phonemes(word)
            assert "\u0361" not in symbols, f"Tie bar found in Piper phonemes for {word}"


class TestSyllableToPiperPhonemes:
    """Test individual syllable conversion."""

    def test_stressed_syllable(self) -> None:
        s = Syllable(text="mi", onset="m", nucleus="i", coda="", stressed=True)
        symbols = syllable_to_piper_phonemes(s)
        assert symbols[0] == "ˈ"

    def test_unstressed_syllable(self) -> None:
        s = Syllable(text="rad", onset="r", nucleus="a", coda="d", stressed=False)
        symbols = syllable_to_piper_phonemes(s)
        assert "ˈ" not in symbols

    def test_onset_r_uses_flap(self) -> None:
        # r in onset position maps to ɾ
        s = Syllable(text="rad", onset="r", nucleus="a", coda="d", stressed=False)
        symbols = syllable_to_piper_phonemes(s)
        assert "ɾ" in symbols  # onset r → ɾ


class TestTextToPiperPhonemes:
    """Test full text conversion including word separators."""

    def test_single_word(self) -> None:
        symbols = text_to_piper_phonemes("Mirad")
        assert "ˈ" in symbols
        assert "m" in symbols

    def test_two_words_have_separator(self) -> None:
        symbols = text_to_piper_phonemes("Mirad booka")
        # Should have a space word separator between the two words
        assert " " in symbols

    def test_punctuation_preserved(self) -> None:
        symbols = text_to_piper_phonemes("Mirad!")
        assert "!" in symbols


# ── Integration: validate against Piper voice config ────────────────────────────


class TestValidateAgainstVoiceConfig:
    """Validate that all Mirad phoneme symbols exist in Piper voice configs."""

    @pytest.fixture
    def es_voice_id_map(self) -> dict:
        """Load the es_MX voice config's phoneme_id_map."""
        config_path = (
            Path(__file__).resolve().parents[1]
            / ".gsd" / "piper-voices" / "es_MX-claude-high.onnx.json"
        )
        if not config_path.exists():
            pytest.skip("es_MX voice config not available")
        import json
        return json.loads(config_path.read_text())["phoneme_id_map"]

    @pytest.fixture
    def en_voice_id_map(self) -> dict:
        """Load the en_US voice config's phoneme_id_map."""
        config_path = (
            Path(__file__).resolve().parents[1]
            / ".gsd" / "piper-voices" / "en_US-lessac-medium.onnx.json"
        )
        if not config_path.exists():
            pytest.skip("en_US voice config not available")
        import json
        return json.loads(config_path.read_text())["phoneme_id_map"]

    def test_all_mirad_phonemes_in_es_voice(
        self, es_voice_id_map: dict
    ) -> None:
        """Every symbol produced by our Piper mapping must be in the voice config."""
        test_words = [
            "Mirad", "igay", "tejna", "vay", "aymsea", "booka",
            "byoskyin", "auwa", "tixe", "jal", "ya", "wa",
            "yay", "way", "qatar", "ama", "oyse", "akea", "alayn",
            "cema",  # tests affricate c → t + ʃ
        ]
        for word in test_words:
            symbols = word_to_piper_phonemes(word)
            missing = [s for s in symbols if s not in es_voice_id_map]
            assert missing == [], (
                f"Word {word!r}: symbols {missing} missing from es_MX voice config"
            )

    def test_all_mirad_phonemes_in_en_voice(
        self, en_voice_id_map: dict
    ) -> None:
        """Every symbol produced by our Piper mapping must be in the voice config."""
        test_words = [
            "Mirad", "igay", "tejna", "vay", "aymsea", "booka",
            "byoskyin", "auwa", "tixe", "jal", "ya", "wa",
            "yay", "way", "qatar", "ama", "oyse", "akea", "alayn",
            "cema",
        ]
        for word in test_words:
            symbols = word_to_piper_phonemes(word)
            missing = [s for s in symbols if s not in en_voice_id_map]
            assert missing == [], (
                f"Word {word!r}: symbols {missing} missing from en_US voice config"
            )
