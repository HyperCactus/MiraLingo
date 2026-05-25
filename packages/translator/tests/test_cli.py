import pytest
import subprocess
from unittest.mock import patch, Mock, MagicMock
import sys
import os
import logging
import dspy

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from mirad_translator.cli import main


def test_cli_help():
    """Test mirad-translate --help runs without error."""
    result = subprocess.run([
        "python", "-m", "mirad_translator.cli", "--help"
    ], capture_output=True, text=True)

    assert result.returncode == 0
    assert "Text to translate" in result.stdout


def test_cli_translation():
    """Test CLI translation command (En→Mir, default direction)."""
    mock_prediction = dspy.Prediction(
        mirad_text="Helo",
        word_equivalents={"hello": "helo"},
        context=["[grammar] verb rules"],
    )

    with patch('mirad_translator.cli._configure_deepinfra_lm') as mock_lm_config, \
         patch('mirad_translator.cli.DefaultTranslator') as mock_factory:
        mock_translator = Mock()
        # Module call: translator(english_text=...) returns prediction
        mock_translator.return_value = mock_prediction
        mock_factory.return_value = mock_translator

        original_argv = sys.argv
        try:
            sys.argv = ['mirad-translate', 'Hello']
            import io
            from contextlib import redirect_stdout
            f = io.StringIO()
            with redirect_stdout(f):
                main()
            output = f.getvalue()

            assert "Helo" in output

        finally:
            sys.argv = original_argv


def test_cli_reverse_translation():
    """Test CLI --reverse flag for Mir→En translation."""
    mock_prediction = dspy.Prediction(
        english_text="I know the answer.",
        word_equivalents={"at": "i", "te": "know"},
        context=["[grammar] verb rules"],
    )

    with patch('mirad_translator.cli._configure_deepinfra_lm') as mock_lm_config, \
         patch('mirad_translator.cli.DefaultTranslator') as mock_factory:
        mock_translator = Mock()
        mock_translator.return_value = mock_prediction
        mock_factory.return_value = mock_translator

        original_argv = sys.argv
        try:
            sys.argv = ['mirad-translate', '--reverse', 'At te ha dud.']
            import io
            from contextlib import redirect_stdout
            f = io.StringIO()
            with redirect_stdout(f):
                main()
            output = f.getvalue()

            assert "I know the answer" in output

        finally:
            sys.argv = original_argv

        # Verify direction was set correctly
        mock_factory.assert_called_once_with(direction="mir_to_en")


def test_cli_retrieve_mode():
    """Test CLI --retrieve flag shows word equivalents and context."""
    mock_prediction = dspy.Prediction(
        mirad_text="At tose oma.",
        word_equivalents={"i": "at", "cold": "oma"},
        context=["[grammar_rules] verb rules"],
    )

    with patch('mirad_translator.cli._configure_deepinfra_lm') as mock_lm_config, \
         patch('mirad_translator.cli.DefaultTranslator') as mock_factory:
        mock_translator = Mock()
        mock_translator.return_value = mock_prediction
        mock_factory.return_value = mock_translator

        original_argv = sys.argv
        try:
            sys.argv = ['mirad-translate', '--retrieve', 'I am cold.']
            import io
            from contextlib import redirect_stdout
            f = io.StringIO()
            with redirect_stdout(f):
                main()
            output = f.getvalue()

            assert "--- Word equivalents ---" in output
            assert "cold → oma" in output or "i → at" in output
            assert "--- Structured grammar rules ---" in output
            assert "--- Translation ---" in output
            assert "At tose oma." in output

        finally:
            sys.argv = original_argv


def test_cli_no_text():
    """Test CLI exits with error when no text provided."""
    original_argv = sys.argv
    try:
        sys.argv = ['mirad-translate']  # No positional text arg
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
    finally:
        sys.argv = original_argv


def test_cli_debug_mode():
    """Test CLI debug mode enables logging."""
    mock_prediction = dspy.Prediction(
        mirad_text="Helo",
        word_equivalents={}, context=[],
    )

    with patch('logging.basicConfig') as mock_logging, \
         patch('mirad_translator.cli._configure_deepinfra_lm') as mock_lm_config, \
         patch('mirad_translator.cli.DefaultTranslator') as mock_factory:
        mock_translator = Mock()
        mock_translator.return_value = mock_prediction
        mock_factory.return_value = mock_translator

        original_argv = sys.argv
        try:
            sys.argv = ['mirad-translate', '--debug', 'Hello']
            main()
        finally:
            sys.argv = original_argv

        mock_logging.assert_called_with(level=logging.DEBUG)

def test_cli_vocab_only_preserves_input_order(monkeypatch, capsys):
    from mirad_translator import cli

    monkeypatch.setattr('sys.argv', ['mirad-translator', '--vocab-only', 'congratulated toasted'])
    monkeypatch.setattr('mirad_translator.lexicon_db.lookup_word_candidates', lambda english_word=None, **_: {
        'congratulated': ['hwaydwa', 'yanivtosdwa'],
        'toasted': ['aymxwa', 'hwaydwa'],
    }.get(english_word, []))

    cli.main()
    assert capsys.readouterr().out.splitlines() == [
        'congratulated → hwaydwa, yanivtosdwa',
        'toasted → aymxwa, hwaydwa',
    ]


def test_cli_vocab_only_reverse_preserves_input_order(monkeypatch, capsys):
    from mirad_translator import cli

    monkeypatch.setattr('sys.argv', ['mirad-translator', '--vocab-only', '--reverse', 'hwaydwa yanivtosdwa'])
    monkeypatch.setattr('mirad_translator.lexicon_db.lookup_mirad_word_candidates', lambda mirad_word=None, **_: {
        'hwaydwa': ['cheered on', 'congratulated', 'toasted'],
        'yanivtosdwa': ['congratulated', 'felicitated'],
    }.get(mirad_word, []))

    cli.main()
    assert capsys.readouterr().out.splitlines() == [
        'hwaydwa → cheered on, congratulated, toasted',
        'yanivtosdwa → congratulated, felicitated',
    ]
