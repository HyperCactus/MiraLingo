import pytest
import dspy
from unittest.mock import Mock, patch
from mirad_translator.translate import TranslatorModule, EnglishToMiradSignature

def test_translate_signature():
    """Test the DSPy signature structure."""
    # Test that the signature has the required fields
    assert hasattr(EnglishToMiradSignature, 'english_text')
    assert hasattr(EnglishToMiradSignature, 'mirad_text')
    assert hasattr(EnglishToMiradSignature, 'confidence')
    
    # Test field types and descriptions
    assert isinstance(EnglishToMiradSignature.english_text, dspy.InputField)
    assert isinstance(EnglishToMiradSignature.mirad_text, dspy.OutputField)
    assert isinstance(EnglishToMiradSignature.confidence, dspy.OutputField)
    
    assert EnglishToMiradSignature.english_text.desc == "English text to translate"
    assert EnglishToMiradSignature.mirad_text.desc == "Translated text in Mirad"
    assert EnglishToMiradSignature.confidence.desc == "Confidence score between 0 and 1"

def test_translator_module_forward():
    """Test TranslatorModule forward method."""
    # Mock DSPy prediction
    mock_prediction = Mock()
    mock_prediction.mirad_text = "Helo"
    mock_prediction.confidence = 0.95
    
    # Mock the ChainOfThought module
    with patch('dspy.ChainOfThought') as mock_cot:
        mock_instance = Mock()
        mock_instance.return_value = mock_prediction
        mock_cot.return_value = mock_instance
        
        # Initialize and test
        translator = TranslatorModule()
        result = translator.forward(english_text="Hello")
        
        # Verify
        assert result.mirad_text == "Helo"
        assert result.confidence == 0.95
        mock_cot.assert_called_once()

def test_translator_module_initialization():
    """Test TranslatorModule initialization."""
    with patch('dspy.ChainOfThought') as mock_cot:
        mock_instance = Mock()
        mock_cot.return_value = mock_instance
        
        translator = TranslatorModule()
        
        # Verify initialization
        assert hasattr(translator, 'generate')
        assert mock_cot.called
        
        # Verify the signature used
        # Since ChainOfThought doesn't have a direct 'signature' attribute,
        # we verify it was called with the correct signature class
        mock_cot.assert_called_once_with(EnglishToMiradSignature)

def test_translator_module_forward_error_handling():
    """Test TranslatorModule forward method error handling."""
    with patch('dspy.ChainOfThought') as mock_cot:
        # Setup mock to raise an exception
        mock_instance = Mock()
        mock_instance.side_effect = Exception("DSPy error")
        mock_cot.return_value = mock_instance
        
        translator = TranslatorModule()
        
        # This should raise the exception
        with pytest.raises(Exception, match="DSPy error"):
            translator.forward(english_text="Hello")
