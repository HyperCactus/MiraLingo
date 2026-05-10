"""Regression tests for the Piper backend bridge."""

from mirad_tts.piper_backend import _text_to_piper_phoneme_input


def test_piper_bridge_uses_mapped_ipa_phonemes_for_words() -> None:
    assert _text_to_piper_phoneme_input("Mirad") == "[[ˈmiɾad]]"


def test_piper_bridge_maps_stress_and_vowels() -> None:
    assert _text_to_piper_phoneme_input("booka") == "[[boˈoka]]"


def test_piper_bridge_preserves_spaces_and_punctuation() -> None:
    assert _text_to_piper_phoneme_input("Mirad booka!") == "[[ˈmiɾad boˈoka!]]"