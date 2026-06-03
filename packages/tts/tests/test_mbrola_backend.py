"""Comprehensive MBROLA backend tests for the Mirad TTS pipeline.

Covers phone mappings, .pho generation, CLI integration, error classes,
and an integration test skipped unless ``mbrola`` + ``de6`` are installed.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

from mirad_tts.mbrola_backend import (
    DURATIONS,
    MBROLA_COMPLEX_VOWELS,
    MBROLA_CONSONANTS,
    MBROLA_SIMPLE_VOWELS,
    MbrolaError,
    MbrolaNotFoundError,
    MbrolaSynthesisError,
    MbrolaVoiceNotFoundError,
    PhoLine,
    _phone_duration,
    _phone_pitch,
    _validate_phones,
    diagnose_mbrola,
    generate_pho,
    pho_to_string,
    syllable_to_mbrola,
    synthesize_to_wav,
    text_to_mbrola_phones,
    word_to_mbrola,
    word_to_mbrola_phones,
    write_pho,
)
from mirad_tts.syllabify import Syllable


# ── Phone mapping tests ────────────────────────────────────────────────────────


class TestMbrolaConsonants:
    """All consonants map correctly to de6 phone symbols."""

    @pytest.mark.parametrize(
        "mirad,de6",
        [
            ("b", "b"), ("c", "tS"), ("d", "d"), ("f", "f"), ("g", "g"),
            ("h", "h"), ("j", "Z"), ("k", "k"), ("l", "l"), ("m", "m"),
            ("n", "n"), ("p", "p"), ("q", "k"), ("r", "r"), ("s", "s"),
            ("t", "t"), ("v", "v"), ("x", "S"), ("z", "z"),
        ],
    )
    def test_consonant_mapping(self, mirad, de6):
        assert MBROLA_CONSONANTS[mirad] == de6

    def test_x_maps_to_S(self):
        """Key requirement: x → S (post-alveolar fricative)."""
        assert MBROLA_CONSONANTS["x"] == "S"

    def test_j_maps_to_Z(self):
        """Key requirement: j → Z (voiced palatal fricative)."""
        assert MBROLA_CONSONANTS["j"] == "Z"

    def test_c_maps_to_tS(self):
        """Key requirement: c → tS (affricate)."""
        assert MBROLA_CONSONANTS["c"] == "tS"

    def test_h_maps_to_h(self):
        """Key requirement: h → h (de6 supports it, unlike Italian voices)."""
        assert MBROLA_CONSONANTS["h"] == "h"


class TestMbrolaVowels:
    """Vowel mappings for de6."""

    def test_a_short(self):
        assert MBROLA_SIMPLE_VOWELS["a"] == "a"

    def test_e_long(self):
        assert MBROLA_SIMPLE_VOWELS["e"] == "e:"

    def test_i_long(self):
        assert MBROLA_SIMPLE_VOWELS["i"] == "i:"

    def test_o_long(self):
        assert MBROLA_SIMPLE_VOWELS["o"] == "o:"

    def test_u_long(self):
        assert MBROLA_SIMPLE_VOWELS["u"] == "u:"


class TestMbrolaComplexVowels:
    """Complex vowel expansions into de6 phone sequences."""

    def test_ya_maps_to_j_a(self):
        assert MBROLA_COMPLEX_VOWELS["ya"] == "j a"

    def test_ay_maps_to_a_j(self):
        assert MBROLA_COMPLEX_VOWELS["ay"] == "a j"

    def test_aw_maps_to_O(self):
        """aw → O (German open 'o' approximation in de6)."""
        assert MBROLA_COMPLEX_VOWELS["aw"] == "O"

    def test_yi_maps_to_j_i_colon(self):
        assert MBROLA_COMPLEX_VOWELS["yi"] == "j i:"

    def test_way_maps_to_w_a_j(self):
        assert MBROLA_COMPLEX_VOWELS["way"] == "w a j"

    def test_all_complex_vowels_have_spaces(self):
        """All complex vowel mappings produce space-separated phone sequences."""
        for key, value in MBROLA_COMPLEX_VOWELS.items():
            assert " " in value or len(value) <= 3, f"Complex vowel {key!r} unexpectedly short: {value!r}"


# ── Syllable-to-MBROLA conversion tests ────────────────────────────────────────


class TestSyllableToMbrola:
    """Direct unit tests for syllable_to_mbrola()."""

    def test_simple_onset_nucleus(self):
        syl = Syllable(text="ha", onset="h", nucleus="a", coda="", stressed=False)
        assert syllable_to_mbrola(syl, source_word="ha") == "h a"

    def test_stressed_syllable_same_phones(self):
        """Stress affects duration/pitch in .pho, not phone symbols."""
        syl = Syllable(text="mi", onset="m", nucleus="i", coda="", stressed=True)
        assert syllable_to_mbrola(syl, source_word="mi") == "m i:"

    def test_coda_consonant(self):
        syl = Syllable(text="jal", onset="j", nucleus="a", coda="l", stressed=False)
        assert syllable_to_mbrola(syl, source_word="jal") == "Z a l"

    def test_complex_vowel_ay(self):
        syl = Syllable(text="vay", onset="v", nucleus="ay", coda="", stressed=False)
        assert syllable_to_mbrola(syl, source_word="vay") == "v a j"

    def test_complex_vowel_ya(self):
        syl = Syllable(text="ya", onset="", nucleus="ya", coda="", stressed=False)
        assert syllable_to_mbrola(syl, source_word="ya") == "j a"

    def test_complex_vowel_aw(self):
        syl = Syllable(text="maw", onset="m", nucleus="aw", coda="", stressed=False)
        assert syllable_to_mbrola(syl, source_word="maw") == "m O"

    def test_x_in_onset(self):
        syl = Syllable(text="xa", onset="x", nucleus="a", coda="", stressed=False)
        assert syllable_to_mbrola(syl, source_word="xa") == "S a"

    def test_q_maps_to_k(self):
        syl = Syllable(text="qa", onset="q", nucleus="a", coda="", stressed=False)
        assert syllable_to_mbrola(syl, source_word="qa") == "k a"


class TestWordToMbrola:
    """Word-level conversion including stress."""

    def test_mirad(self):
        # mi-RA → stressed on penult "ra": ' m i: r a d
        result = word_to_mbrola("Mirad")
        phones = result.split()
        assert "m" in phones
        assert "i:" in phones
        assert "r" in phones
        assert "a" in phones
        assert "d" in phones

    def test_ha_mirad_words(self):
        ha = word_to_mbrola("ha")
        assert ha == "h a"

    def test_single_syllable_vay(self):
        result = word_to_mbrola("vay")
        assert result == "v a j"

    def test_empty_word(self):
        assert word_to_mbrola("") == ""

    def test_triple_vowel_word_with_complex_then_simple_nucleus(self):
        result = word_to_mbrola("twiyubien")
        phones = result.split()
        assert phones[:4] == ["t", "w", "i:", "j"]
        assert "u:" in phones
        assert "b" in phones
        assert phones[-2:] == ["e:", "n"]


class TestTextToMbrolaPhones:
    """Full-text phone sequence generation."""

    def test_single_word(self):
        phones = text_to_mbrola_phones("ha")
        assert phones == ["h", "a"]

    def test_two_words_adds_pause(self):
        phones = text_to_mbrola_phones("ha Mirad")
        # Should include _ word boundary between words
        assert "_" in phones
        assert phones[0] == "h"
        assert phones[1] == "a"

    def test_punctuation_not_in_phones(self):
        phones = text_to_mbrola_phones("ha.")
        # Period is not in phone list; only words contribute
        assert all(p != "." for p in phones)


# ── .pho generation tests ──────────────────────────────────────────────────────


class TestPhoGeneration:
    """Tests for .pho file generation (durations, pitch, pauses)."""

    def test_pho_line_format(self):
        line = PhoLine(phone="a", duration_ms=110, pitch=[0, 110, 100, 105])
        assert line.to_line() == "a 110 0 110 100 105"

    def test_pho_line_no_pitch(self):
        line = PhoLine(phone="m", duration_ms=75, pitch=[])
        assert line.to_line() == "m 75"

    def test_initial_silence(self):
        lines = generate_pho("ha")
        assert lines[0].phone == "_"
        assert lines[0].duration_ms == 80

    def test_final_silence(self):
        lines = generate_pho("ha")
        assert lines[-1].phone == "_"
        assert lines[-1].duration_ms == 120

    def test_sentence_final_pause(self):
        lines = generate_pho("ha.")
        # Should have a sentence pause before the final silence
        # Find the sentence pause (duration 220)
        pause_found = any(
            line.phone == "_" and line.duration_ms == DURATIONS["sentence_pause"]
            for line in lines
        )
        assert pause_found, "Sentence-final pause not found"

    def test_comma_pause(self):
        lines = generate_pho("ha,")
        pause_found = any(
            line.phone == "_" and line.duration_ms == DURATIONS["comma_pause"]
            for line in lines
        )
        assert pause_found, "Comma pause not found"

    def test_stressed_vowel_has_stressed_pitch(self):
        """Stressed vowels should have the 3-point pitch contour."""
        lines = generate_pho("Mirad")
        # "mi" is stressed → its vowel i: should have stressed pitch
        stressed_vowel_lines = [l for l in lines if l.phone == "i:" and l.duration_ms == DURATIONS["stressed_vowel"]]
        assert len(stressed_vowel_lines) >= 1
        # Stressed pitch has 6 values (3 position% Hz pairs)
        assert len(stressed_vowel_lines[0].pitch) == 6

    def test_unstressed_vowel_has_unstressed_pitch(self):
        """Unstressed vowels should have the 2-point pitch contour."""
        lines = generate_pho("Mirad")
        # "rad" has unstressed "a" → should have unstressed pitch
        unstressed_vowel_lines = [l for l in lines if l.phone == "a" and l.duration_ms == DURATIONS["vowel"]]
        assert len(unstressed_vowel_lines) >= 1
        # Unstressed pitch has 4 values (2 position% Hz pairs)
        assert len(unstressed_vowel_lines[0].pitch) == 4

    def test_consonants_have_no_pitch(self):
        """Consonants should have empty pitch lists."""
        lines = generate_pho("ha")
        # h is a consonant → no pitch
        h_lines = [l for l in lines if l.phone == "h"]
        assert len(h_lines) == 1
        assert h_lines[0].pitch == []

    def test_pho_to_string(self):
        lines = generate_pho("ha")
        text = pho_to_string(lines)
        assert text.startswith("_ 80\n")
        assert text.strip().endswith("_ 120")

    def test_write_pho_creates_file(self, tmp_path: Path):
        pho_path = write_pho("ha", str(tmp_path / "test.pho"))
        assert pho_path.exists()
        content = pho_path.read_text()
        assert content.startswith("_ 80")
        assert "h" in content
        assert "a" in content

    def test_ha_mirad_pho_includes_key_phones(self):
        """The phrase 'Ha Mirad.' should contain h, a, m, i:, r, a, d."""
        lines = generate_pho("Ha Mirad.")
        phone_list = [l.phone for l in lines]
        assert "h" in phone_list, "Missing phone 'h'"
        assert "a" in phone_list, "Missing phone 'a'"
        assert "m" in phone_list, "Missing phone 'm'"
        assert "i:" in phone_list, "Missing phone 'i:'"
        assert "r" in phone_list, "Missing phone 'r'"
        assert "d" in phone_list, "Missing phone 'd'"

    def test_word_pause_between_words(self):
        lines = generate_pho("ha Mirad")
        word_pauses = [l for l in lines if l.phone == "_" and l.duration_ms == DURATIONS["word_pause"]]
        # At least one word pause between the two words
        assert len(word_pauses) >= 1, "No word pause found between words"


# ── Duration classification tests ──────────────────────────────────────────────


class TestPhoneDuration:
    """Duration classification for de6 phone types."""

    def test_vowel_duration(self):
        assert _phone_duration("a") == DURATIONS["vowel"]

    def test_stressed_vowel_duration(self):
        assert _phone_duration("a", stressed=True) == DURATIONS["stressed_vowel"]

    def test_glide_duration(self):
        assert _phone_duration("j") == DURATIONS["glide"]

    def test_liquid_duration(self):
        assert _phone_duration("r") == DURATIONS["liquid"]

    def test_nasal_duration(self):
        assert _phone_duration("m") == DURATIONS["nasal"]

    def test_stop_duration(self):
        assert _phone_duration("t") == DURATIONS["stop"]

    def test_fricative_duration(self):
        assert _phone_duration("h") == DURATIONS["fricative"]

    def test_affricate_duration(self):
        assert _phone_duration("tS") == DURATIONS["affricate"]

    def test_unknown_phone_fallback(self):
        assert _phone_duration("ZZ") == 80

    def test_long_vowel_duration(self):
        assert _phone_duration("e:") == DURATIONS["vowel"]

    def test_O_duration(self):
        """aw → O should have vowel duration."""
        assert _phone_duration("O") == DURATIONS["vowel"]


# ── Pitch classification tests ──────────────────────────────────────────────────


class TestPhonePitch:
    """Pitch target generation for de6 phones."""

    def test_vowel_has_pitch(self):
        pitch = _phone_pitch("a", stressed=False)
        assert len(pitch) > 0

    def test_stressed_vowel_has_stressed_pitch(self):
        unstressed = _phone_pitch("a", stressed=False)
        stressed = _phone_pitch("a", stressed=True)
        assert len(stressed) > len(unstressed)

    def test_consonant_no_pitch(self):
        assert _phone_pitch("h") == []
        assert _phone_pitch("m") == []
        assert _phone_pitch("t") == []

    def test_glide_no_pitch(self):
        assert _phone_pitch("j") == []
        assert _phone_pitch("w") == []


# ── Validation tests ────────────────────────────────────────────────────────────


class TestPhoneValidation:
    """Phone symbol validation for de6."""

    def test_valid_phones_pass(self):
        _validate_phones(["h", "a", "m", "i:", "r", "d"])  # Should not raise

    def test_invalid_phone_raises(self):
        with pytest.raises(MbrolaError, match="Unsupported de6 phone symbols"):
            _validate_phones(["h", "INVALID", "a"])

    def test_pause_phone_ignored(self):
        _validate_phones(["_", "a", "h"])  # _ should not trigger validation error


# ── Synthesis tests (mocked) ──────────────────────────────────────────────────


class TestSynthesizeToWav:
    """MBROLA synthesis pipeline tests with mocked subprocess."""

    def test_empty_text_raises_value_error(self, tmp_path: Path):
        with pytest.raises(ValueError, match="text must not be empty"):
            synthesize_to_wav("   ", tmp_path / "out.wav")

    def test_directory_output_raises_value_error(self, tmp_path: Path):
        with pytest.raises(ValueError, match="must be a file path"):
            synthesize_to_wav("Ha Mirad.", tmp_path)

    def test_missing_parent_raises_value_error(self, tmp_path: Path):
        bad_path = tmp_path / "missing-parent" / "out.wav"
        with pytest.raises(ValueError, match="parent directory does not exist"):
            synthesize_to_wav("Ha Mirad.", bad_path)

    def test_missing_binary_raises_not_found_error(self, tmp_path: Path, monkeypatch):
        monkeypatch.setattr(shutil, "which", lambda _: None)
        with pytest.raises(MbrolaNotFoundError):
            synthesize_to_wav("Ha Mirad.", tmp_path / "out.wav")

    def test_missing_voice_db_raises_not_found_error(self, tmp_path: Path, monkeypatch):
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/bin/mbrola")
        # Create a non-existent voice db path so the check fails
        fake_db = tmp_path / "nonexistent" / "de6" / "de6"
        with pytest.raises(MbrolaVoiceNotFoundError):
            synthesize_to_wav("Ha Mirad.", tmp_path / "out.wav", mbrola_db=fake_db)

    def test_successful_synthesis(self, tmp_path: Path, monkeypatch):
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/bin/mbrola")

        fake_db = tmp_path / "de6" / "de6"
        fake_db.parent.mkdir(parents=True)
        fake_db.write_text("fake")

        output = tmp_path / "out.wav"

        def mock_run(command, **kwargs):
            # Simulate mbrola creating the output file
            Path(command[3]).write_bytes(b"RIFF" + b"\x00" * 100)
            return subprocess.CompletedProcess(args=command, returncode=0, stderr="")

        monkeypatch.setattr(subprocess, "run", mock_run)

        result = synthesize_to_wav(
            "Ha Mirad.", output, mbrola_db=fake_db
        )
        assert result == output
        assert output.exists()

    def test_mbrola_non_zero_exit_raises(self, tmp_path: Path, monkeypatch):
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/bin/mbrola")

        fake_db = tmp_path / "de6" / "de6"
        fake_db.parent.mkdir(parents=True)
        fake_db.write_text("fake")

        def mock_run(command, **kwargs):
            return subprocess.CompletedProcess(
                args=command, returncode=1, stderr="phone not found"
            )

        monkeypatch.setattr(subprocess, "run", mock_run)

        with pytest.raises(MbrolaSynthesisError, match="exit code 1"):
            synthesize_to_wav("Ha Mirad.", tmp_path / "out.wav", mbrola_db=fake_db)


# ── Diagnostics tests ──────────────────────────────────────────────────────────


class TestDiagnoseMbrola:
    """Diagnostic output for MBROLA phone inspection."""

    def test_single_word(self):
        diags = diagnose_mbrola("ha")
        assert len(diags) == 1
        assert diags[0]["word"] == "ha"
        assert diags[0]["error"] is None

    def test_multiple_words(self):
        diags = diagnose_mbrola("Ha Mirad")
        assert len(diags) == 2
        assert diags[0]["word"] == "Ha"
        assert diags[1]["word"] == "Mirad"

    def test_punctuation_ignored(self):
        diags = diagnose_mbrola("ha.")
        # Only one WORD token
        assert len(diags) == 1
        assert diags[0]["word"] == "ha"


# ── Integration test (skipped unless mbrola + de6 installed) ────────────────────


class TestMbrolaIntegration:
    """Integration tests that require actual mbrola binary and de6 voice.

    These tests are skipped unless both ``mbrola`` and
    ``/usr/share/mbrola/de6/de6`` exist on the system.
    """

    @pytest.fixture(autouse=True)
    def check_mbrola(self):
        if shutil.which("mbrola") is None:
            pytest.skip("mbrola not installed (install: sudo apt install mbrola mbrola-de6)")
        if not Path("/usr/share/mbrola/de6/de6").exists():
            pytest.skip("mbrola de6 voice not installed (install: sudo apt install mbrola-de6)")

    def test_synthesize_ha_mirad(self, tmp_path: Path):
        """Synthesize 'Ha Mirad.' and verify output exists and is non-empty."""
        output = tmp_path / "mirad.wav"
        result = synthesize_to_wav("Ha Mirad.", output)
        assert result == output
        assert output.exists()
        assert output.stat().st_size > 0

    def test_synthesize_single_word(self, tmp_path: Path):
        output = tmp_path / "ha.wav"
        result = synthesize_to_wav("ha", output)
        assert result == output
        assert output.exists()
        assert output.stat().st_size > 0

    def test_pho_file_written_correctly(self, tmp_path: Path):
        """Write and verify a .pho file produces valid MBROLA input."""
        pho_path = write_pho("ha", str(tmp_path / "test.pho"))
        content = pho_path.read_text()
        assert "h" in content
        assert "a" in content

    def test_synthesize_with_custom_db_path(self, tmp_path: Path):
        """Verify synthesis works with explicit mbrola_db parameter."""
        output = tmp_path / "mirad_custom.wav"
        result = synthesize_to_wav(
            "Mirad.", output,
            mbrola_db=Path("/usr/share/mbrola/de6/de6"),
        )
        assert result == output
        assert output.exists()
        assert output.stat().st_size > 0

    def test_sentence_with_all_key_phones(self, tmp_path: Path):
        """Synthesize a sentence using h, S, Z, tS phones to exercise de6."""
        output = tmp_path / "test_phones.wav"
        # "xeloja cey" → S e: l o Z a tS e: j
        result = synthesize_to_wav("xeloja cey.", output)
        assert result == output
        assert output.exists()
        assert output.stat().st_size > 0

    def test_cli_mbrola_backend(self, tmp_path: Path):
        """CLI --backend mbrola produces WAV output."""
        from mirad_tts.cli import run as cli_run
        output = tmp_path / "cli_test.wav"
        selected, debug, wav, voice = cli_run([
            "--backend", "mbrola",
            "--wav", str(output),
            "Mirad.",
        ])
        assert Path(output).exists()
        assert Path(output).stat().st_size > 0

    def test_cli_mbrola_debug(self, tmp_path: Path):
        """CLI --mbrola-debug produces diagnostics."""
        from mirad_tts.cli import run as cli_run
        selected, debug_lines, wav, voice = cli_run([
            "--mbrola",
            "--mbrola-debug",
            "Mirad",
        ])
        assert any("MBROLA PHONES" in line for line in debug_lines)

    def test_cli_mbrola_pho_output(self, tmp_path: Path):
        """CLI --pho writes .pho file."""
        from mirad_tts.cli import run as cli_run
        pho_path = tmp_path / "test.pho"
        selected, debug, wav, voice = cli_run([
            "--mbrola",
            "--pho", str(pho_path),
            "Ha Mirad.",
        ])
        assert pho_path.exists()
        content = pho_path.read_text()
        assert "h" in content
        assert "a" in content