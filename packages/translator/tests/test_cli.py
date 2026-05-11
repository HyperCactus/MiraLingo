import pytest
import subprocess
from unittest.mock import patch, Mock
import sys
import os
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from mirad_translator.cli import main


def test_cli_help():
    """Test mirad-translate --help runs without error."""
    import subprocess
    
    result = subprocess.run([
        "python", "-m", "mirad_translator.cli", "--help"
    ], capture_output=True, text=True)
    
    assert result.returncode == 0
    assert "Text to translate" in result.stdout
    

def test_cli_translation():
    """Test CLI translation command."""
    with patch('mirad_translator.cli.OllamaLM') as mock_ollama_class, \
         patch('mirad_translator.cli.TranslatorModule') as mock_translator_class, \
         patch('mirad_translator.cli.dspy.configure') as mock_configure:
        # Setup mock OllamaLM instance
        mock_ollama_instance = Mock()
        mock_ollama_class.return_value = mock_ollama_instance
        
        # Setup mock translator instance
        mock_instance = Mock()
        mock_prediction = Mock()
        mock_prediction.mirad_text = "Helo"
        mock_prediction.confidence = 0.95
        mock_instance.forward.return_value = mock_prediction
        mock_translator_class.return_value = mock_instance
        
        # Save original sys.argv and replace
        original_argv = sys.argv
        try:
            sys.argv = ['mirad-translate', 'Hello']
            # Capture stdout
            import io
            from contextlib import redirect_stdout
            f = io.StringIO()
            with redirect_stdout(f):
                main()
            output = f.getvalue()
            
            # Verify output
            assert "Helo" in output
            assert "[0.95]" in output
            
        finally:
            sys.argv = original_argv
        
        # Verify the translator was instantiated
        mock_translator_class.assert_called_once()
        
        # Verify forward was called
        mock_instance.forward.assert_called_once_with(english_text="Hello")


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
    with patch('logging.basicConfig') as mock_logging, \
         patch('mirad_translator.cli.OllamaLM') as mock_ollama, \
         patch('mirad_translator.cli.dspy.configure'), \
         patch('mirad_translator.cli.TranslatorModule') as mock_translator:
        mock_instance = Mock()
        mock_prediction = Mock()
        mock_prediction.mirad_text = "Helo"
        mock_prediction.confidence = 0.95
        mock_instance.forward.return_value = mock_prediction
        mock_translator.return_value = mock_instance
        
        original_argv = sys.argv
        try:
            sys.argv = ['mirad-translate', '--debug', 'Hello']
            main()
        finally:
            sys.argv = original_argv
        
        # Verify logging was called with debug level
        mock_logging.assert_called_with(level=logging.DEBUG)
