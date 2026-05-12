import pytest
import subprocess
from unittest.mock import patch, Mock
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
    """Test CLI translation command."""
    mock_prediction = dspy.Prediction(
        mirad_text="Helo",
        confidence="0.95",
        word_equivalents={"hello": "helo"},
        context=["[grammar] verb rules"],
    )

    with patch('mirad_translator.cli.OllamaLM') as mock_ollama_class, \
         patch('mirad_translator.cli.DefaultTranslator') as mock_factory, \
         patch('mirad_translator.cli.dspy.configure'):
        mock_ollama_instance = Mock()
        mock_ollama_class.return_value = mock_ollama_instance

        mock_translator = Mock()
        mock_translator.forward.return_value = mock_prediction
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
            assert "[0.95]" in output

        finally:
            sys.argv = original_argv

        mock_translator.forward.assert_called_once_with(english_text="Hello")


def test_cli_retrieve_mode():
    """Test CLI --retrieve flag shows word equivalents and context."""
    mock_prediction = dspy.Prediction(
        mirad_text="At tose oma.",
        confidence="0.90",
        word_equivalents={"i": "at", "cold": "oma"},
        context=["[grammar] verb rules", "[thesaurus] weather terms"],
    )

    with patch('mirad_translator.cli.OllamaLM') as mock_ollama_class, \
         patch('mirad_translator.cli.DefaultTranslator') as mock_factory, \
         patch('mirad_translator.cli.dspy.configure'):
        mock_translator = Mock()
        mock_translator.forward.return_value = mock_prediction
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
            assert "cold → oma" in output
            assert "--- Context ---" in output
            assert "--- Mirad ---" in output
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
        mirad_text="Helo", confidence="0.95",
        word_equivalents={}, context=[],
    )

    with patch('logging.basicConfig') as mock_logging, \
         patch('mirad_translator.cli.OllamaLM') as mock_ollama, \
         patch('mirad_translator.cli.dspy.configure'), \
         patch('mirad_translator.cli.DefaultTranslator') as mock_factory:
        mock_translator = Mock()
        mock_translator.forward.return_value = mock_prediction
        mock_factory.return_value = mock_translator

        original_argv = sys.argv
        try:
            sys.argv = ['mirad-translate', '--debug', 'Hello']
            main()
        finally:
            sys.argv = original_argv

        mock_logging.assert_called_with(level=logging.DEBUG)