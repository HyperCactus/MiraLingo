import pytest
import dspy
from unittest.mock import Mock, patch
from mirad_translator.translate import TranslatorModule, EnglishToMiradSignature

def test_translate_signature():
    """Test the DSPy signature structure."""
    # Input fields should contain english_text
    assert 'english_text' in EnglishToMiradSignature.input_fields
    # Output fields should contain mirad_text and confidence
    assert 'mirad_text' in EnglishToMiradSignature.output_fields
    assert 'confidence' in EnglishToMiradSignature.output_fields
    
    # Verify field types and descriptions via model_fields
    fields = EnglishToMiradSignature.model_fields
    assert fields['english_text'].json_schema_extra['__dspy_field_type'] == 'input'
    assert fields['mirad_text'].json_schema_extra['__dspy_field_type'] == 'output'
    assert fields['confidence'].json_schema_extra['__dspy_field_type'] == 'output'
    
    assert fields['english_text'].json_schema_extra['desc'] == "English text to translate"
    assert fields['mirad_text'].json_schema_extra['desc'] == "Translated text in Mirad"
    assert fields['confidence'].json_schema_extra['desc'] == "Confidence score between 0 and 1"

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
