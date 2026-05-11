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
    with patch('mirad_translator.translate.TranslatorModule') as mock_translator_class:
        # Setup mock instance
        mock_instance = Mock()
        mock_prediction = Mock()
        mock_prediction.mirad_text = "Helo"
        mock_prediction.confidence = 0.95
        mock_instance.forward.return_value = mock_prediction
        mock_translator_class.return_value = mock_instance
        
        # Test with arguments
        test_args = ['python', '-m', 'mirad_translator.cli', 'Hello']
        
        # Save original sys.argv and replace
        original_argv = sys.argv
        try:
            sys.argv = test_args
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
    with patch('sys.exit') as mock_exit:
        # Save original sys.argv
        original_argv = sys.argv
        try:
            sys.argv = ['python', '-m', 'mirad_translator.cli']
            main()
        except SystemExit:
            pass
        finally:
            sys.argv = original_argv
        
        mock_exit.assert_called_once_with(1)


def test_cli_debug_mode():
    """Test CLI debug mode enables logging."""
    with patch('logging.basicConfig') as mock_logging:
        with patch('sys.exit') as mock_exit:
            # Setup args with debug
            test_args = ['python', '-m', 'mirad_translator.cli', '--debug', 'Hello']
            
            # Save original sys.argv
            original_argv = sys.argv
            try:
                sys.argv = test_args
                main()
            except SystemExit:
                pass
            finally:
                sys.argv = original_argv
            
            # Verify logging was called with debug level
            mock_logging.assert_called_with(level=logging.DEBUG)
            
            # Verify exit was called (since no Ollama connection)
            mock_exit.assert_called()
