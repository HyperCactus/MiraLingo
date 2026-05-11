"""Comprehensive eSpeak backend tests for the Mirad TTS pipeline.

Covers syllable_to_espeak(), word_to_espeak(),
text_to_espeak_phoneme_input(), error classes, and synthesize_to_wav().
"""

import shutil
import subprocess
from pathlib import Path

import pytest

from mirad_tts.espeak_backend import (
    EspeakBinaryNotFoundError,
    EspeakConversionError,
    EspeakSynthesisError,
    EspeakSynthesisTimeoutError,
    syllable_to_espeak,
    synthesize_to_wav,
    text_to_espeak_phoneme_input,
    word_to_espeak,
)
from mirad_tts.syllabify import Syllable


class TestEspeakConversion:
    """Basic word-level eSpeak conversion assertions."""

    def test_mirad_first_syllable_stressed(self):
        assert "'mirad" == word_to_espeak("Mirad")

    def test_igay_first_syllable_stressed(self):
        assert "'igai" == word_to_espeak("igay")

    def test_booka_middle_syllable_stressed(self):
        assert "bo'oka" == word_to_espeak("booka")

    def test_akea_second_syllable_stressed(self):
        # sylls=['a','ke','a'], stress=[F,T,F] → stress on 'ke', nucleus 'e' no diphthong
        assert "a'kea" == word_to_espeak("akea")

    def test_single_syllable_vay_no_stress(self):
        assert "vai" == word_to_espeak("vay")

    def test_single_syllable_tei(self):
        assert "'tei" == word_to_espeak("tei")

    def test_xati_x_to_S(self):
        assert "'Sati" == word_to_espeak("xati")

    def test_byoskyin(self):
        assert "'bjoskjin" == word_to_espeak("byoskyin")

    def test_kopo_first_stress(self):
        assert "'kopo" == word_to_espeak("kopo")

    def test_tejna_j_to_Z(self):
        assert "'teZna" == word_to_espeak("tejna")

    def test_tebra_r_coda(self):
        assert "'tebra" == word_to_espeak("tebra")

    def test_aymsea_complex_vowel_ay(self):
        assert "aim'sea" == word_to_espeak("aymsea")


class TestEspeakStress:
    """Stress marker behavior — ' prefix only from syllable.stressed flag."""

    def test_stressed_syllable_adds_apostrophe(self):
        stressed = Syllable(text="mi", onset="m", nucleus="i", coda="", stressed=True)
        assert "'mi" == syllable_to_espeak(stressed, source_word="mi")

    def test_unstressed_syllable_no_apostrophe(self):
        unstressed = Syllable(text="mi", onset="m", nucleus="i", coda="", stressed=False)
        assert "mi" == syllable_to_espeak(unstressed, source_word="mi")

    def test_word_stress_propagates_to_syllables(self):
        # booka: stress on second syllable → bo'oka
        assert "bo'oka" == word_to_espeak("booka")

    def test_first_syllable_stress(self):
        # ama: stress on first syllable
        assert "'ama" == word_to_espeak("ama")

    def test_single_syllable_word_has_no_stress(self):
        assert "vai" == word_to_espeak("vay")


class TestSyllableEspeakDirect:
    """Direct unit tests for syllable_to_espeak() using Syllable objects."""

    def test_plain_syllable_no_stress(self):
        syl = Syllable(text="pa", onset="p", nucleus="a", coda="", stressed=False)
        assert syllable_to_espeak(syl, source_word="pa") == "pa"

    def test_plain_syllable_stressed(self):
        syl = Syllable(text="pa", onset="p", nucleus="a", coda="", stressed=True)
        assert syllable_to_espeak(syl, source_word="pa") == "'pa"

    def test_syllable_with_onset_coda_no_stress(self):
        syl = Syllable(text="pak", onset="p", nucleus="a", coda="k", stressed=False)
        assert syllable_to_espeak(syl, source_word="pak") == "pak"

    def test_syllable_with_onset_coda_stressed(self):
        syl = Syllable(text="pak", onset="p", nucleus="a", coda="k", stressed=True)
        assert syllable_to_espeak(syl, source_word="pak") == "'pak"

    def test_x_to_S_in_onset(self):
        syl = Syllable(text="xa", onset="x", nucleus="a", coda="", stressed=False)
        assert syllable_to_espeak(syl, source_word="xa") == "Sa"

    def test_j_to_Z_in_onset(self):
        syl = Syllable(text="ja", onset="j", nucleus="a", coda="", stressed=False)
        assert syllable_to_espeak(syl, source_word="ja") == "Za"

    def test_complex_vowel_ay_maps_to_ai(self):
        syl = Syllable(text="may", onset="m", nucleus="ay", coda="", stressed=False)
        assert syllable_to_espeak(syl, source_word="may") == "mai"

    def test_complex_vowel_oy_maps_to_oi(self):
        syl = Syllable(text="toy", onset="t", nucleus="oy", coda="", stressed=False)
        assert syllable_to_espeak(syl, source_word="toy") == "toi"

    def test_complex_vowel_aw_maps_to_au(self):
        syl = Syllable(text="maw", onset="m", nucleus="aw", coda="", stressed=False)
        assert syllable_to_espeak(syl, source_word="maw") == "mau"

    def test_empty_body_no_apostrophe(self):
        # stressed but body is empty → no apostrophe
        syl = Syllable(text="", onset="", nucleus="", coda="", stressed=True)
        assert syllable_to_espeak(syl, source_word="") == ""


class TestEspeakConsonantMappings:
    """All consonants map correctly to eSpeak phoneme codes."""

    def test_b(self):
        assert syllable_to_espeak(
            Syllable(text="ba", onset="b", nucleus="a", coda="", stressed=False), source_word="ba"
        ) == "ba"

    def test_c(self):
        assert syllable_to_espeak(
            Syllable(text="ca", onset="c", nucleus="a", coda="", stressed=False), source_word="ca"
        ) == "tSa"

    def test_d(self):
        assert syllable_to_espeak(
            Syllable(text="da", onset="d", nucleus="a", coda="", stressed=False), source_word="da"
        ) == "da"

    def test_f(self):
        assert syllable_to_espeak(
            Syllable(text="fa", onset="f", nucleus="a", coda="", stressed=False), source_word="fa"
        ) == "fa"

    def test_g(self):
        assert syllable_to_espeak(
            Syllable(text="ga", onset="g", nucleus="a", coda="", stressed=False), source_word="ga"
        ) == "ga"

    def test_h(self):
        assert syllable_to_espeak(
            Syllable(text="ha", onset="h", nucleus="a", coda="", stressed=False), source_word="ha"
        ) == "ha"

    def test_j(self):
        assert syllable_to_espeak(
            Syllable(text="ja", onset="j", nucleus="a", coda="", stressed=False), source_word="ja"
        ) == "Za"

    def test_k(self):
        assert syllable_to_espeak(
            Syllable(text="ka", onset="k", nucleus="a", coda="", stressed=False), source_word="ka"
        ) == "ka"

    def test_l(self):
        assert syllable_to_espeak(
            Syllable(text="la", onset="l", nucleus="a", coda="", stressed=False), source_word="la"
        ) == "la"

    def test_m(self):
        assert syllable_to_espeak(
            Syllable(text="ma", onset="m", nucleus="a", coda="", stressed=False), source_word="ma"
        ) == "ma"

    def test_n(self):
        assert syllable_to_espeak(
            Syllable(text="na", onset="n", nucleus="a", coda="", stressed=False), source_word="na"
        ) == "na"

    def test_p(self):
        assert syllable_to_espeak(
            Syllable(text="pa", onset="p", nucleus="a", coda="", stressed=False), source_word="pa"
        ) == "pa"

    def test_q(self):
        assert syllable_to_espeak(
            Syllable(text="qa", onset="q", nucleus="a", coda="", stressed=False), source_word="qa"
        ) == "ka"

    def test_r(self):
        assert syllable_to_espeak(
            Syllable(text="ra", onset="r", nucleus="a", coda="", stressed=False), source_word="ra"
        ) == "ra"

    def test_s(self):
        assert syllable_to_espeak(
            Syllable(text="sa", onset="s", nucleus="a", coda="", stressed=False), source_word="sa"
        ) == "sa"

    def test_t(self):
        assert syllable_to_espeak(
            Syllable(text="ta", onset="t", nucleus="a", coda="", stressed=False), source_word="ta"
        ) == "ta"

    def test_v(self):
        assert syllable_to_espeak(
            Syllable(text="va", onset="v", nucleus="a", coda="", stressed=False), source_word="va"
        ) == "va"

    def test_w(self):
        assert syllable_to_espeak(
            Syllable(text="wa", onset="w", nucleus="a", coda="", stressed=False), source_word="wa"
        ) == "wa"

    def test_x(self):
        assert syllable_to_espeak(
            Syllable(text="xa", onset="x", nucleus="a", coda="", stressed=False), source_word="xa"
        ) == "Sa"

    def test_y(self):
        assert syllable_to_espeak(
            Syllable(text="ya", onset="y", nucleus="a", coda="", stressed=False), source_word="ya"
        ) == "ja"

    def test_z(self):
        assert syllable_to_espeak(
            Syllable(text="za", onset="z", nucleus="a", coda="", stressed=False), source_word="za"
        ) == "za"


class TestEspeakVowelMappings:
    """Simple and complex vowel mappings for eSpeak."""

    def test_simple_a(self):
        assert "a" == word_to_espeak("a", stress=False)

    def test_simple_e(self):
        assert "e" == word_to_espeak("e", stress=False)

    def test_simple_i(self):
        assert "i" == word_to_espeak("i", stress=False)

    def test_simple_o(self):
        assert "o" == word_to_espeak("o", stress=False)

    def test_simple_u(self):
        assert "u" == word_to_espeak("u", stress=False)

    def test_ay_becomes_ai(self):
        assert "ai" == word_to_espeak("ay", stress=False)

    def test_ey_becomes_ei(self):
        assert "ei" == word_to_espeak("ey", stress=False)

    def test_oy_becomes_oi(self):
        assert "oi" == word_to_espeak("oy", stress=False)

    def test_aw_becomes_au(self):
        assert "au" == word_to_espeak("aw", stress=False)

    def test_ow_becomes_ou(self):
        assert "ou" == word_to_espeak("ow", stress=False)

    def test_yo_becomes_jo(self):
        assert "jo" == word_to_espeak("yo", stress=False)

    def test_yi_becomes_ji(self):
        assert "ji" == word_to_espeak("yi", stress=False)

    def test_yo_stressed(self):
        # Single syllable → assign_stress returns unstressed; no apostrophe
        assert "jo" == word_to_espeak("yo")


class TestEspeakPunctuation:
    """Punctuation and non-word tokens are preserved in output."""

    def test_sentence_with_punctuation(self):
        # SPACE is consumed as separator (no SPACE token); PUNCT tokens pass through
        assert "[[at'tiSe'mirad.]]" == text_to_espeak_phoneme_input("At tixe Mirad.")

    def test_punctuation_mixed_tokens(self):
        # No spaces between tokens; PUNCT tokens each pass through as-is
        assert "[['mirad,'igai!?]]" == text_to_espeak_phoneme_input("Mirad, igay!?")

    def test_question_mark(self):
        assert "[[vai?]]" == text_to_espeak_phoneme_input("vay?")

    def test_exclamation(self):
        assert "[['ama!]]" == text_to_espeak_phoneme_input("ama!")

    def test_colon_preserved(self):
        assert "[['ama:]]" == text_to_espeak_phoneme_input("ama:")

    def test_double_brackets_exactly_one_pair(self):
        result = text_to_espeak_phoneme_input("vay")
        assert result.startswith("[[")
        assert result.endswith("]]")


class TestNegativeAndBoundaryCases:
    """Error handling and edge-case inputs."""

    def test_empty_input(self):
        assert "[[]]" == text_to_espeak_phoneme_input("")

    def test_whitespace_only_input(self):
        # No WORD tokens → empty conversion, single [[]]
        assert "[[]]" == text_to_espeak_phoneme_input("   ")

    def test_word_with_no_nucleus_maps_without_crash(self):
        assert "br" == word_to_espeak("br")

    def test_invalid_word_character_raises_contextual_error(self):
        with pytest.raises(EspeakConversionError) as exc_info:
            word_to_espeak("mi3")

        message = str(exc_info.value)
        assert "mi3" in message
        assert "invalid character" in message

    def test_unsupported_consonant_raises(self):
        with pytest.raises(EspeakConversionError) as exc_info:
            word_to_espeak("ß")  # sharp s is not a Mirad consonant

        assert "unsupported consonant" in str(exc_info.value)

    def test_empty_word_returns_empty(self):
        assert "" == word_to_espeak("")

    def test_whitespace_word(self):
        assert "" == word_to_espeak("   ")

    def test_text_token_invalid_char_raises_wrapping(self):
        # NUMBER tokens (like '3') pass through without conversion; no error raised
        # The word 'mi' converts fine; only invalid chars in WORD tokens raise
        result = text_to_espeak_phoneme_input("mi3")
        assert "mi3" in result  # mi converts, 3 passes through as NUMBER token

    def test_error_contains_word_context(self):
        with pytest.raises(EspeakConversionError) as exc_info:
            word_to_espeak("abc!def")

        assert "abc!def" in str(exc_info.value)


class TestSynthesizeToWav:
    """Synthesis pipeline with mocked subprocess."""

    def test_empty_text_raises_value_error(self, tmp_path: Path):
        with pytest.raises(ValueError, match="text must not be empty"):
            synthesize_to_wav("   ", tmp_path / "out.wav")

    def test_invalid_output_path_directory_raises_value_error(self, tmp_path: Path):
        with pytest.raises(ValueError, match="must be a file path"):
            synthesize_to_wav("At tixe Mirad.", tmp_path)

    def test_invalid_output_parent_raises_value_error(self, tmp_path: Path):
        bad_path = tmp_path / "missing-parent" / "out.wav"
        with pytest.raises(ValueError, match="parent directory does not exist"):
            synthesize_to_wav("At tixe Mirad.", bad_path)

    def test_missing_binary_raises_specialized_error(self, tmp_path: Path, monkeypatch):
        def _raise_missing(*_args, **_kwargs):
            raise FileNotFoundError("espeak-ng")

        monkeypatch.setattr(subprocess, "run", _raise_missing)

        with pytest.raises(EspeakBinaryNotFoundError) as exc_info:
            synthesize_to_wav("At tixe Mirad.", tmp_path / "out.wav")

        message = str(exc_info.value)
        assert "espeak-ng" in message
        assert "output_path=" in message
        assert "command" in message

    def test_timeout_raises_specialized_error(self, tmp_path: Path, monkeypatch):
        def _raise_timeout(*_args, **_kwargs):
            raise subprocess.TimeoutExpired(
                cmd=["espeak-ng", "-w", "out.wav"], timeout=0.01, stderr="hung"
            )

        monkeypatch.setattr(subprocess, "run", _raise_timeout)

        with pytest.raises(EspeakSynthesisTimeoutError) as exc_info:
            synthesize_to_wav("At tixe Mirad.", tmp_path / "out.wav", timeout_seconds=0.01)

        message = str(exc_info.value)
        assert "timeout_seconds=0.01" in message
        assert "stderr=hung" in message
        assert "output_path=" in message
        assert "command" in message

    def test_non_zero_exit_raises_synthesis_error(self, tmp_path: Path, monkeypatch):
        def _return_failed(*_args, **_kwargs):
            return subprocess.CompletedProcess(
                args=["espeak-ng", "-w", "out.wav"], returncode=2, stderr="boom"
            )

        monkeypatch.setattr(subprocess, "run", _return_failed)

        with pytest.raises(EspeakSynthesisError) as exc_info:
            synthesize_to_wav("At tixe Mirad.", tmp_path / "out.wav")

        message = str(exc_info.value)
        assert "exit_code=2" in message
        assert "stderr=boom" in message
        assert "output_path=" in message
        assert "command" in message

    def test_voice_override_included_in_command(self, tmp_path: Path, monkeypatch):
        captured: dict[str, object] = {}
        output = tmp_path / "voice.wav"

        def _run(command, **kwargs):
            captured["command"] = command
            output.write_bytes(b"RIFF....WAVE")
            return subprocess.CompletedProcess(args=command, returncode=0, stderr="")

        monkeypatch.setattr(subprocess, "run", _run)

        result = synthesize_to_wav("At tixe Mirad.", output, voice="en")
        assert result == output
        assert captured["command"] == [
            "espeak-ng", "-w", str(output),
            "-s", "120", "-p", "40", "-g", "4", "-a", "90",
            "-v", "en", "-z",
        ]

    def test_default_command_without_voice(self, tmp_path: Path, monkeypatch):
        captured: dict[str, object] = {}
        output = tmp_path / "default.wav"

        def _run(command, **kwargs):
            captured["command"] = command
            output.write_bytes(b"RIFF....WAVE")
            return subprocess.CompletedProcess(args=command, returncode=0, stderr="")

        monkeypatch.setattr(subprocess, "run", _run)

        synthesize_to_wav("At tixe Mirad.", output)
        assert captured["command"] == [
            "espeak-ng", "-w", str(output),
            "-s", "120", "-p", "40", "-g", "4", "-a", "90", "-z",
        ]

    def test_custom_params_in_command(self, tmp_path: Path, monkeypatch):
        captured: dict[str, object] = {}
        output = tmp_path / "custom.wav"

        def _run(command, **kwargs):
            captured["command"] = command
            output.write_bytes(b"RIFF....WAVE")
            return subprocess.CompletedProcess(args=command, returncode=0, stderr="")

        monkeypatch.setattr(subprocess, "run", _run)

        synthesize_to_wav(
            "At tixe Mirad.", output,
            voice="en-gb", speed=175, pitch=50, word_gap=0,
            amplitude=100, no_final_pause=False,
        )
        assert captured["command"] == [
            "espeak-ng", "-w", str(output),
            "-s", "175", "-p", "50", "-g", "0", "-a", "100",
            "-v", "en-gb",
        ]
        # No -z flag when no_final_pause=False

    def test_existing_output_is_overwritten(self, tmp_path: Path, monkeypatch):
        output = tmp_path / "overwrite.wav"
        output.write_bytes(b"old")

        def _run(command, **kwargs):
            Path(command[2]).write_bytes(b"new-wav-bytes")
            return subprocess.CompletedProcess(args=command, returncode=0, stderr="")

        monkeypatch.setattr(subprocess, "run", _run)

        synthesize_to_wav("At tixe Mirad.", output)
        assert output.read_bytes() == b"new-wav-bytes"

    def test_uses_converted_phoneme_input_not_raw_text(self, tmp_path: Path, monkeypatch):
        seen_input: dict[str, str] = {}
        output = tmp_path / "out.wav"
        raw = "At tixe Mirad."

        def _run(command, **kwargs):
            seen_input["input"] = kwargs["input"]
            output.write_bytes(b"RIFF....WAVE")
            return subprocess.CompletedProcess(args=command, returncode=0, stderr="")

        monkeypatch.setattr(subprocess, "run", _run)

        synthesize_to_wav(raw, output)
        assert seen_input["input"] == text_to_espeak_phoneme_input(raw)
        assert seen_input["input"] != raw

    def test_non_empty_wav_created_when_espeak_available(self, tmp_path: Path):
        if shutil.which("espeak-ng") is None:
            pytest.skip("espeak-ng not installed in environment")

        output = tmp_path / "runtime.wav"
        result = synthesize_to_wav("At tixe Mirad.", output)

        assert result == output
        assert output.exists()
        assert output.stat().st_size > 0


class TestEspeakRegressionFromCsv:
    """Regression tests using anchor data from data/pronunciation_tests.csv.

    The espeak column contains actual code outputs per MEM021.
    """

    @pytest.mark.parametrize(
        "word,expected",
        [
            ("ama", "'ama"),
            ("aymsea", "aim'sea"),
            ("upayo", "u'pajo"),
            pytest.param("tambwa", None, marks=pytest.mark.xfail(reason="w not in espeak vowels — crashes EspeakConversionError")),
            ("booka", "bo'oka"),
            ("Mirad", "'mirad"),
            ("igay", "'igai"),
            ("vay", "vai"),
            ("tejna", "'teZna"),
            ("akea", "a'kea"),
            ("byoskyin", "'bjoskjin"),
            ("xati", "'Sati"),
            ("kopo", "'kopo"),
            ("xei", "'Sei"),
            ("zoi", "'zoi"),
            pytest.param("auwa", None, marks=pytest.mark.xfail(reason="w not in espeak vowels — crashes EspeakConversionError")),
            ("tei", "'tei"),
            ("jal", "Zal"),
            ("tanra", "'tanra"),
            ("skeit", "'skeit"),
            ("glyn", "gljn"),
            ("skropo", "'skropo"),
            ("spoli", "'spoli"),
            ("jukita", "Zu'kita"),
            ("zopra", "'zopra"),
            ("blasi", "'blasi"),
            ("amra", "'amra"),
            ("xulu", "'Sulu"),
            ("tebra", "'tebra"),
            ("tixe", "'tiSe"),
            ("paktro", "'paktro"),
        ],
    )
    def test_espeak_regression(self, word, expected):
        if expected is None:
            pytest.skip(f"{word} crashes on espeak conversion (w not in espeak vowels)")
        assert word_to_espeak(word) == expected, f"eSpeak regression failed for {word}"