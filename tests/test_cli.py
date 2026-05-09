from pathlib import Path

import pytest

from mirad_tts import cli
from mirad_tts.espeak_backend import (
    EspeakBinaryNotFoundError,
    EspeakConversionError,
    EspeakSynthesisError,
    EspeakSynthesisTimeoutError,
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _run(argv: list[str]):
    """Call run() and return (selected, debug_lines, wav_path, voice)."""
    return cli.run(argv)


# ---------------------------------------------------------------------------
# Test CLI default and explicit modes
# ---------------------------------------------------------------------------

class TestCliModes:
    """Tests for --ipa, --syllables, --espeak flags and default IPA mode."""

    def test_default_mode_is_ipa(self, capsys):
        code = cli.main(["Mirad"])
        captured = capsys.readouterr()
        assert code == 0
        assert "ˈmiɾad" in captured.out.strip()
        assert captured.err == ""

    def test_explicit_ipa_flag(self, capsys):
        code = cli.main(["--ipa", "Mirad"])
        captured = capsys.readouterr()
        assert code == 0
        assert "ˈmiɾad" in captured.out.strip()

    def test_ipa_flag_matches_default(self, capsys):
        default_out = cli.main(["Mirad"])
        explicit_out = cli.main(["--ipa", "Mirad"])
        assert default_out == 0 == explicit_out

    def test_syllables_mode(self, capsys):
        code = cli.main(["--syllables", "Mirad"])
        captured = capsys.readouterr()
        assert code == 0
        # syllabification: Mi.rad, stress on first → ˈmi.rad
        assert "ˈmi.rad" in captured.out.strip()

    def test_syllables_mode_preserves_punctuation(self, capsys):
        code = cli.main(["--syllables", "Mirad,", "igay!?"])
        captured = capsys.readouterr()
        assert code == 0
        assert "ˈmi.rad,ˈi.gay!?" in captured.out.strip()

    def test_espeak_mode(self, capsys):
        code = cli.main(["--espeak", "Mirad"])
        captured = capsys.readouterr()
        assert code == 0
        assert "[['mirad]]" == captured.out.strip()

    def test_at_tixe_mirad_ipa(self, capsys):
        code = cli.main(["At", "tixe", "Mirad."])
        captured = capsys.readouterr()
        assert code == 0
        # text_to_ipa('At tixe Mirad.') → 'atˈtiʃeˈmiɾad.' (lowercased per IPA convention)
        assert "atˈtiʃeˈmiɾad." in captured.out.strip()

    def test_at_tixe_mirad_syllables(self, capsys):
        code = cli.main(["--syllables", "At", "tixe", "Mirad."])
        captured = capsys.readouterr()
        assert code == 0
        assert "atˈti.xeˈmi.rad." in captured.out.strip()

    def test_at_tixe_mirad_espeak(self, capsys):
        code = cli.main(["--espeak", "At", "tixe", "Mirad."])
        captured = capsys.readouterr()
        assert code == 0
        assert "[[at'tiSe'mirad.]]" in captured.out.strip()

    def test_preserves_punctuation(self, capsys):
        code = cli.main(["Mirad?!"])
        captured = capsys.readouterr()
        assert code == 0
        assert "ˈmiɾad?!" in captured.out.strip()

    def test_preserves_numbers(self, capsys):
        code = cli.main(["tixe", "123"])
        captured = capsys.readouterr()
        assert code == 0
        assert "ˈtiʃe123" in captured.out.strip()

    def test_single_word(self, capsys):
        code = cli.main(["igay"])
        captured = capsys.readouterr()
        assert code == 0
        assert "ˈigaɪ" in captured.out.strip()

    def test_multiple_sentences(self, capsys):
        code = cli.main(["Mirad.", "igay!?"])
        captured = capsys.readouterr()
        assert code == 0
        out = captured.out.strip()
        assert "ˈmiɾad." in out
        assert "ˈigaɪ!?" in out


# ---------------------------------------------------------------------------
# Test mutually exclusive flags
# ---------------------------------------------------------------------------

class TestMutuallyExclusiveFlags:
    """--syllables and --espeak cannot be combined."""

    def test_syllables_and_espeak_mutually_exclusive(self, capsys):
        try:
            cli.main(["--syllables", "--espeak", "Mirad"])
        except SystemExit as e:
            assert e.code == 2
        captured = capsys.readouterr()
        assert "not allowed with argument" in captured.err

    def test_all_three_modes_mutually_exclusive(self, capsys):
        try:
            cli.main(["--ipa", "--syllables", "--espeak", "Mirad"])
        except SystemExit as e:
            assert e.code == 2


# ---------------------------------------------------------------------------
# Test --debug flag
# ---------------------------------------------------------------------------

class TestDebugFlag:
    """Tests for --debug stage-line output to stderr."""

    def test_debug_outputs_four_stage_lines(self, capsys):
        code = cli.main(["--debug", "Mirad"])
        captured = capsys.readouterr()
        assert code == 0
        lines = [l for l in captured.err.strip().split("\n") if l]
        assert len(lines) == 4

    def test_debug_format_each_line(self, capsys):
        cli.main(["--debug", "Mirad"])
        captured = capsys.readouterr()
        for line in captured.err.strip().split("\n"):
            assert line.startswith("debug stage=")

    def test_debug_tokenizer_line_format(self, capsys):
        cli.main(["--debug", "Mirad"])
        captured = capsys.readouterr()
        assert any("stage=tokenizer" in l and "tokens=" in l for l in captured.err.strip().split("\n"))

    def test_debug_syllables_line_format(self, capsys):
        cli.main(["--debug", "Mirad"])
        captured = capsys.readouterr()
        assert any("stage=syllables_stress" in l and "output=" in l for l in captured.err.strip().split("\n"))

    def test_debug_ipa_line_format(self, capsys):
        cli.main(["--debug", "Mirad"])
        captured = capsys.readouterr()
        assert any("stage=ipa" in l and "output=" in l for l in captured.err.strip().split("\n"))

    def test_debug_espeak_line_format(self, capsys):
        cli.main(["--debug", "Mirad"])
        captured = capsys.readouterr()
        assert any("stage=espeak" in l and "output=" in l for l in captured.err.strip().split("\n"))

    def test_debug_no_output_on_stdout(self, capsys):
        cli.main(["--debug", "Mirad"])
        captured = capsys.readouterr()
        # stdout should contain the selected output, not debug lines
        assert "debug stage=" not in captured.out

    def test_debug_combined_with_syllables(self, capsys):
        cli.main(["--debug", "--syllables", "Mirad"])
        captured = capsys.readouterr()
        lines = [l for l in captured.err.strip().split("\n") if l]
        assert len(lines) == 4  # still 4 stage lines
        assert "ˈmi.rad" in captured.out  # syllables on stdout

    def test_debug_combined_with_espeak(self, capsys):
        cli.main(["--debug", "--espeak", "Mirad"])
        captured = capsys.readouterr()
        lines = [l for l in captured.err.strip().split("\n") if l]
        assert len(lines) == 4
        assert "[['mirad]]" in captured.out  # espeak on stdout

    def test_no_debug_flag_produces_no_stderr(self, capsys):
        cli.main(["Mirad"])
        captured = capsys.readouterr()
        assert captured.err == ""


# ---------------------------------------------------------------------------
# Test run() directly
# ---------------------------------------------------------------------------

class TestRunFunction:
    """Tests for the run() function return values."""

    def test_run_returns_selected_debug_wav_voice(self):
        selected, debug_lines, wav_path, voice = _run(["Mirad"])
        assert isinstance(selected, str)
        assert isinstance(debug_lines, list)
        assert wav_path is None
        assert voice is None

    def test_run_debug_lines_empty_without_flag(self):
        selected, debug_lines, wav_path, voice = _run(["Mirad"])
        assert debug_lines == []

    def test_run_debug_lines_populated_with_flag(self):
        selected, debug_lines, wav_path, voice = _run(["--debug", "Mirad"])
        assert len(debug_lines) == 4

    def test_run_syllables_selected(self):
        selected, debug_lines, wav_path, voice = _run(["--syllables", "Mirad"])
        assert "ˈmi.rad" in selected

    def test_run_espeak_selected(self):
        selected, debug_lines, wav_path, voice = _run(["--espeak", "Mirad"])
        assert "[['mirad]]" in selected

    def test_run_wav_path_returned(self):
        # Without --wav flag, run() skips synthesis and wav_path is None
        selected, debug_lines, wav_path, voice = _run(["Mirad"])
        assert wav_path is None

    def test_run_voice_returned(self):
        selected, debug_lines, wav_path, voice = _run(["--voice", "en", "Mirad"])
        assert voice == "en"

    def test_run_wav_and_voice_returned_together(self):
        # Without --wav, only voice is returned without triggering synthesis
        selected, debug_lines, wav_path, voice = _run(["--voice", "en", "Mirad"])
        assert voice == "en"
        assert wav_path is None

    def test_run_returns_selected_output(self):
        selected, debug_lines, wav_path, voice = _run(["At", "tixe", "Mirad."])
        assert selected == "atˈtiʃeˈmiɾad."


# ---------------------------------------------------------------------------
# Test error paths and CliPipelineError stage attribution
# ---------------------------------------------------------------------------

class TestErrorPaths:
    """Tests for error handling with stage-qualified CliPipelineError messages."""

    def test_empty_text_raises_cli_pipeline_error(self):
        with pytest.raises(cli.CliPipelineError) as exc_info:
            _run(["   "])
        assert exc_info.value.stage == "input"
        assert "must not be empty" in str(exc_info.value)

    def test_empty_text_return_code_1(self, capsys):
        code = cli.main(["   "])
        captured = capsys.readouterr()
        assert code == 1
        assert "stage=input" in captured.err

    def test_legacy_orthography_returns_error(self):
        with pytest.raises(cli.CliPipelineError) as exc_info:
            _run(["mîrad"])
        assert exc_info.value.stage == "tokenizer"
        assert "UnsupportedLegacyOrthographyError" in str(exc_info.value)

    def test_legacy_orthography_return_code_1(self, capsys):
        code = cli.main(["mîrad"])
        captured = capsys.readouterr()
        assert code == 1
        assert "stage=tokenizer" in captured.err

    def test_tokenizer_error_stage_attributed(self):
        # \\x00 is handled silently by tokenizer; use legacy orthography
        with pytest.raises(cli.CliPipelineError) as exc_info:
            _run(["m\u00eemrad"])  # ê = legacy diacritic → tokenizer error
        assert exc_info.value.stage == "tokenizer"

    def test_input_error_stage_attributed(self):
        with pytest.raises(cli.CliPipelineError) as exc_info:
            _run([""])
        assert exc_info.value.stage == "input"

    def test_cli_pipeline_error_str_format(self):
        with pytest.raises(cli.CliPipelineError) as exc_info:
            _run(["   "])
        err_str = str(exc_info.value)
        assert "stage=input" in err_str
        assert "ValueError" in err_str


# ---------------------------------------------------------------------------
# Test return codes
# ---------------------------------------------------------------------------

class TestReturnCodes:
    """Tests for 0/1 exit codes from main()."""

    def test_return_code_0_on_success(self, capsys):
        code = cli.main(["Mirad"])
        assert code == 0

    def test_return_code_0_with_syllables(self, capsys):
        code = cli.main(["--syllables", "Mirad"])
        assert code == 0

    def test_return_code_0_with_espeak(self, capsys):
        code = cli.main(["--espeak", "Mirad"])
        assert code == 0

    def test_return_code_0_with_debug(self, capsys):
        code = cli.main(["--debug", "Mirad"])
        assert code == 0

    def test_return_code_1_on_empty_input(self, capsys):
        assert cli.main(["   "]) == 1

    def test_return_code_1_on_legacy_orthography(self, capsys):
        assert cli.main(["mîrad"]) == 1

    def test_return_code_0_multi_word_success(self, capsys):
        code = cli.main(["Mirad", "igay", "tixe"])
        assert code == 0


# ---------------------------------------------------------------------------
# Test --wav and --voice synthesis flags
# ---------------------------------------------------------------------------

class TestWavVoiceFlags:
    """Tests for --wav and --voice synthesis integration."""

    def test_wav_raises_when_no_binary(self, capsys, tmp_path: Path):
        with pytest.raises(cli.CliPipelineError) as exc_info:
            _run(["--wav", str(tmp_path / "out.wav"), "Mirad"])
        assert exc_info.value.stage == "synthesis"
        assert "EspeakBinaryNotFoundError" in str(exc_info.value)

    def test_wav_return_code_1_when_binary_missing(self, capsys, tmp_path: Path):
        code = cli.main(["--wav", str(tmp_path / "out.wav"), "Mirad"])
        captured = capsys.readouterr()
        assert code == 1
        assert "stage=synthesis" in captured.err

    def test_wav_parent_dir_nonexistent(self, capsys):
        with pytest.raises(cli.CliPipelineError) as exc_info:
            _run(["--wav", "/nonexistent/parent/out.wav", "Mirad"])
        assert exc_info.value.stage == "synthesis"

    def test_voice_passed_through_mocked(self, tmp_path: Path, monkeypatch, capsys):
        seen = {}

        def _fake_synthesize(text, output_path, *, voice=None, timeout_seconds=10.0):
            seen["voice"] = voice
            Path(output_path).write_bytes(b"RIFF....WAVE")
            return Path(output_path)

        monkeypatch.setattr(cli, "synthesize_to_wav", _fake_synthesize)
        out = tmp_path / "demo.wav"

        code = cli.main(["--wav", str(out), "--voice", "en", "Mirad"])

        captured = capsys.readouterr()
        assert code == 0
        assert seen["voice"] == "en"
        assert "ˈmiɾad" in captured.out

    def test_wav_creates_file_mocked(self, tmp_path: Path, monkeypatch, capsys):
        def _fake_synthesize(text, output_path, *, voice=None, timeout_seconds=10.0):
            Path(output_path).write_bytes(b"RIFF....WAVE")
            return Path(output_path)

        monkeypatch.setattr(cli, "synthesize_to_wav", _fake_synthesize)
        out = tmp_path / "out.wav"

        code = cli.main(["--wav", str(out), "Mirad"])

        assert code == 0
        assert out.exists()
        assert out.stat().st_size > 0

    def test_wav_output_path_must_be_file_not_directory(self, tmp_path: Path, capsys):
        code = cli.main(["--wav", str(tmp_path), "Mirad"])
        captured = capsys.readouterr()
        assert code == 1
        assert "stage=synthesis" in captured.err

    def test_wav_empty_text_fails_input_stage(self, tmp_path: Path, capsys):
        code = cli.main(["--wav", str(tmp_path / "out.wav"), "   "])
        captured = capsys.readouterr()
        assert code == 1
        assert "stage=input" in captured.err

    def test_wav_overwrites_existing(self, tmp_path: Path, monkeypatch, capsys):
        out = tmp_path / "overwrite.wav"
        out.write_bytes(b"old")

        def _fake_synthesize(text, output_path, *, voice=None, timeout_seconds=10.0):
            Path(output_path).write_bytes(b"RIFF....new")
            return Path(output_path)

        monkeypatch.setattr(cli, "synthesize_to_wav", _fake_synthesize)

        code = cli.main(["--wav", str(out), "Mirad"])

        captured = capsys.readouterr()
        assert code == 0
        assert out.read_bytes() == b"RIFF....new"

    def test_wav_synthesis_error_classes_are_distinguishable(
        self, tmp_path: Path, monkeypatch, capsys
    ):
        test_cases = [
            (EspeakBinaryNotFoundError("espeak-ng not found"), "EspeakBinaryNotFoundError"),
            (EspeakSynthesisTimeoutError("timeout"), "EspeakSynthesisTimeoutError"),
            (EspeakSynthesisError("exit code 3"), "EspeakSynthesisError"),
        ]
        for exc, expected_name in test_cases:
            def _raise(*_args, **_kwargs):
                raise exc

            monkeypatch.setattr(cli, "synthesize_to_wav", _raise)

            code = cli.main(["--wav", str(tmp_path / "out.wav"), "Mirad"])
            captured = capsys.readouterr()
            assert code == 1
            assert "stage=synthesis" in captured.err
            assert expected_name in captured.err

    def test_voice_without_wav_not_passed_to_synthesize(self, monkeypatch):
        """--voice without --wav should not attempt synthesis."""
        seen = {}
        original_synthesize = cli.synthesize_to_wav

        def _track(*args, **kwargs):
            seen["called"] = True
            return original_synthesize(*args, **kwargs)

        monkeypatch.setattr(cli, "synthesize_to_wav", _track)

        selected, debug_lines, wav_path, voice = _run(["--voice", "en", "Mirad"])
        assert seen.get("called", False) is False  # synthesize not called
        assert voice == "en"

    def test_wav_and_debug_flags_combined(self, tmp_path: Path, monkeypatch, capsys):
        def _fake_synthesize(text, output_path, *, voice=None, timeout_seconds=10.0):
            Path(output_path).write_bytes(b"RIFF....WAVE")
            return Path(output_path)

        monkeypatch.setattr(cli, "synthesize_to_wav", _fake_synthesize)
        out = tmp_path / "debug.wav"

        code = cli.main(["--debug", "--wav", str(out), "Mirad"])

        captured = capsys.readouterr()
        assert code == 0
        assert "debug stage=tokenizer" in captured.err
        assert out.exists()


# ---------------------------------------------------------------------------
# Parametric tests for grammar anchor words
# ---------------------------------------------------------------------------

_ANCHOR_WORDS = [
    ("ama", "ˈama", "'ama"),
    ("aymsea", "aɪmˈsea", "aim'sea"),
    ("igay", "ˈigaɪ", "'igai"),
    ("vay", "vaɪ", "vai"),
    ("tejna", "ˈteʒna", "'teZna"),
    ("Mirad", "ˈmiɾad", "'mirad"),
]

_IDENTITY_WORDS = [
    ("tixe", "ˈtiʃe"),
    ("auwa", "aˈuwa"),
    ("jal", "ʒal"),
]


class TestGrammarAnchorWordsIpa:
    """Parametric IPA tests for grammar anchor words."""

    @pytest.mark.parametrize("word,expected_ipa,_espeak", _ANCHOR_WORDS, ids=[w[0] for w in _ANCHOR_WORDS])
    def test_anchor_word_ipa(self, word, expected_ipa, _espeak):
        selected, debug_lines, wav_path, voice = _run([word])
        assert expected_ipa in selected

    @pytest.mark.parametrize("word,expected_ipa", _IDENTITY_WORDS, ids=[w[0] for w in _IDENTITY_WORDS])
    def test_identity_word_ipa(self, word, expected_ipa):
        selected, debug_lines, wav_path, voice = _run([word])
        assert expected_ipa in selected


class TestGrammarAnchorWordsEspeak:
    """Parametric espeak tests for grammar anchor words."""

    @pytest.mark.parametrize("word,_ipa,expected_espeak", _ANCHOR_WORDS, ids=[w[0] for w in _ANCHOR_WORDS])
    def test_anchor_word_espeak(self, word, _ipa, expected_espeak):
        selected, debug_lines, wav_path, voice = _run(["--espeak", word])
        assert expected_espeak in selected


class TestGrammarAnchorWordsDebug:
    """Parametric debug-line tests for grammar anchor words — all modes produce 4 stage lines."""

    @pytest.mark.parametrize("word,_,__", _ANCHOR_WORDS, ids=[w[0] for w in _ANCHOR_WORDS])
    def test_anchor_word_debug_lines_count(self, word, _, __):
        selected, debug_lines, wav_path, voice = _run(["--debug", word])
        assert len(debug_lines) == 4

    @pytest.mark.parametrize("word,_,__", _ANCHOR_WORDS, ids=[w[0] for w in _ANCHOR_WORDS])
    def test_anchor_word_debug_all_stages_present(self, word, _, __):
        selected, debug_lines, wav_path, voice = _run(["--debug", word])
        stages = [l.split()[1].split("=")[1] for l in debug_lines]
        assert set(stages) == {"tokenizer", "syllables_stress", "ipa", "espeak"}

    @pytest.mark.parametrize("word", [w[0] for w in _ANCHOR_WORDS + _IDENTITY_WORDS])
    def test_all_anchor_words_produce_nonempty_output(self, word):
        selected, debug_lines, wav_path, voice = _run([word])
        assert selected.strip() != ""

    def test_auwa_ipa_only(self):
        # auwa works in IPA mode directly
        from mirad_tts.ipa import text_to_ipa
        result = text_to_ipa("auwa")
        assert result.strip() != ""


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Edge case and boundary condition tests."""

    def test_all_whitespace(self, capsys):
        for whitespace_input in ["", "   ", "\t\n", "  \t  \n"]:
            code = cli.main([whitespace_input])
            assert code == 1, f"Expected failure for input {whitespace_input!r}"

    def test_debug_with_empty_input(self, capsys):
        code = cli.main(["--debug", "   "])
        captured = capsys.readouterr()
        assert code == 1
        assert "stage=input" in captured.err

    def test_unknown_flag_handled_by_argparse(self, capsys):
        try:
            cli.main(["--unknown-flag", "Mirad"])
        except SystemExit as e:
            assert e.code == 2

    def test_cli_pipeline_error_is_frozen_dataclass(self):
        err = cli.CliPipelineError("test", ValueError("msg"))
        with pytest.raises(AttributeError):
            err.stage = "changed"

    def test_cli_pipeline_error_contains_cause(self):
        cause = ValueError("original")
        err = cli.CliPipelineError("test", cause)
        assert err.cause is cause  # frozen dataclass: __cause__ may not propagate
        assert "test" in str(err)  # __str__ uses stage and cause

    def test_syllables_with_accented_char_raises_tokenizer_error(self, capsys):
        code = cli.main(["--syllables", "êmra"])
        captured = capsys.readouterr()
        assert code == 1
        assert "stage=tokenizer" in captured.err