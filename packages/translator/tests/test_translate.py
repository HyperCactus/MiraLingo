import pytest
import dspy
from unittest.mock import Mock, patch, MagicMock
from mirad_translator.translate import (
    TranslatorModule,
    EnglishToMiradSignature,
    DefaultTranslator,
    translate_with_lookup,
    _MIRAD_GRAMMAR_RULES,
)


def test_translate_signature():
    """Test the DSPy signature structure."""
    # Input fields should contain english_text
    assert 'english_text' in EnglishToMiradSignature.input_fields
    # Output fields should contain mirad_text and confidence
    assert 'mirad_text' in EnglishToMiradSignature.output_fields
    assert 'confidence' in EnglishToMiradSignature.output_fields
    # word_equivalents and context added as input fields for T03
    assert 'word_equivalents' in EnglishToMiradSignature.input_fields
    assert 'context' in EnglishToMiradSignature.input_fields

    # Verify field types and descriptions via model_fields
    fields = EnglishToMiradSignature.model_fields
    assert fields['english_text'].json_schema_extra['__dspy_field_type'] == 'input'
    assert fields['mirad_text'].json_schema_extra['__dspy_field_type'] == 'output'
    assert fields['confidence'].json_schema_extra['__dspy_field_type'] == 'output'
    assert fields['word_equivalents'].json_schema_extra['__dspy_field_type'] == 'input'
    assert fields['context'].json_schema_extra['__dspy_field_type'] == 'input'

    assert fields['english_text'].json_schema_extra['desc'] == "English text to translate"
    assert fields['mirad_text'].json_schema_extra['desc'] == "Translated text in Mirad"
    assert fields['confidence'].json_schema_extra['desc'] == "Confidence score between 0 and 1"
    assert fields['word_equivalents'].json_schema_extra['desc'] == "Dict of English word → Mirad translation from lexicon"
    assert fields['context'].json_schema_extra['desc'] == "Retrieved grammar and thesaurus chunks relevant to the input"


def test_signature_docstring_contains_grammar_rules():
    """Test that the signature docstring embeds grammar rules for DSPy 2.x system prompt."""
    docstring = EnglishToMiradSignature.__doc__
    assert docstring is not None
    # Syntax rules
    assert 'SVO' in docstring or 'Subject + verb' in docstring
    # Verb rules
    assert 'Simple active endings' in docstring or '-e present' in docstring
    # Pronoun rules
    assert 'at I/me' in docstring
    # Check that _MIRAD_GRAMMAR_RULES constant matches what was set
    assert _MIRAD_GRAMMAR_RULES == docstring


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


def test_translator_module_forward_with_lookup_and_context():
    """Test TranslatorModule forward passes word_equivalents and context to generate."""
    mock_prediction = Mock()
    mock_prediction.mirad_text = "Helo"
    mock_prediction.confidence = 0.95

    with patch('dspy.ChainOfThought') as mock_cot:
        mock_instance = Mock()
        mock_instance.return_value = mock_prediction
        mock_cot.return_value = mock_instance

        translator = TranslatorModule()
        word_eq = {"hello": "helo", "world": "woldu"}
        ctx = ["[grammar] A clause", "[thesaurus] A related entry"]
        result = translator.forward(
            english_text="Hello world",
            word_equivalents=word_eq,
            context=ctx
        )

        assert result.mirad_text == "Helo"
        # Verify generate was called with all three inputs
        call_kwargs = mock_instance.call_args.kwargs
        assert call_kwargs['english_text'] == "Hello world"
        assert call_kwargs['word_equivalents'] == word_eq
        assert call_kwargs['context'] == ctx


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


def test_word_lookup_called(monkeypatch):
    """Test that translate_with_lookup calls lexicon lookup for each word."""
    lookup_calls = []

    def mock_lookup(db_path=None, english_word=None):
        lookup_calls.append(english_word)
        return "helo" if english_word else None

    monkeypatch.setattr("mirad_translator.translate.lookup_word", mock_lookup)

    with patch('mirad_translator.translate.DefaultTranslator') as mock_factory:
        mock_translator = Mock()
        mock_pred = Mock()
        mock_pred.mirad_text = "helo"
        mock_pred.confidence = 0.9
        mock_translator.forward.return_value = mock_pred
        mock_factory.return_value = mock_translator

        translate_with_lookup("Hello world", db_path=":memory:")

        assert "hello" in lookup_calls
        assert "world" in lookup_calls


def test_retrieval_called(monkeypatch):
    """Test that translate_with_lookup calls retrieval with top_k."""
    retrieval_calls = []

    def mock_retrieve_all(query, top_k=3):
        retrieval_calls.append((query, top_k))
        return {"grammar": [], "thesaurus": []}

    monkeypatch.setattr("mirad_translator.translate.retrieve_all", mock_retrieve_all)

    with patch('mirad_translator.translate.DefaultTranslator') as mock_factory:
        mock_translator = Mock()
        mock_pred = Mock()
        mock_pred.mirad_text = "helo"
        mock_pred.confidence = 0.9
        mock_translator.forward.return_value = mock_pred
        mock_factory.return_value = mock_translator

        translate_with_lookup("Hello friend", db_path=":memory:", top_k=5)

        assert len(retrieval_calls) == 1
        assert retrieval_calls[0][0] == "Hello friend"
        assert retrieval_calls[0][1] == 5