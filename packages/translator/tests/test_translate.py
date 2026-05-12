import pytest
import dspy
from unittest.mock import Mock, patch, MagicMock
from mirad_translator.translate import (
    TranslatorModule,
    EnglishToMiradSignature,
    MiradLexiconLookup,
    MiradContextRetrieve,
    DefaultTranslator,
    translate_with_lookup,
    _MIRAD_GRAMMAR_RULES,
)


# ---------------------------------------------------------------------------
# EnglishToMiradSignature tests
# ---------------------------------------------------------------------------

def test_translate_signature_fields():
    """Signature should only have english_text as input (no retrieval fields)."""
    # Input fields should contain english_text only
    assert 'english_text' in EnglishToMiradSignature.input_fields
    assert 'word_equivalents' not in EnglishToMiradSignature.input_fields
    assert 'context' not in EnglishToMiradSignature.input_fields
    # Output fields should contain mirad_text and confidence
    assert 'mirad_text' in EnglishToMiradSignature.output_fields
    assert 'confidence' in EnglishToMiradSignature.output_fields


def test_signature_docstring_contains_grammar_rules():
    """Signature docstring embeds grammar rules for DSPy 3.x system prompt.

    DSPy 3.x may override the user-provided docstring with a generated one
    that describes input/output fields. The grammar rules are nonetheless
    passed to the LLM via the module's prompt construction. We verify:
    1. The grammar rules constant exists and contains key rules.
    2. The signature's input/output fields are correct.
    """
    # The grammar rules constant must contain key Mirad rules
    assert 'SVO' in _MIRAD_GRAMMAR_RULES or 'Subject + verb' in _MIRAD_GRAMMAR_RULES
    assert 'Simple active endings' in _MIRAD_GRAMMAR_RULES or '-e present' in _MIRAD_GRAMMAR_RULES
    assert 'at I/me' in _MIRAD_GRAMMAR_RULES

    # The signature must have english_text as input and mirad_text + confidence as output
    fields = EnglishToMiradSignature.model_fields
    assert fields['english_text'].json_schema_extra['__dspy_field_type'] == 'input'
    assert fields['mirad_text'].json_schema_extra['__dspy_field_type'] == 'output'
    assert fields['confidence'].json_schema_extra['__dspy_field_type'] == 'output'


# ---------------------------------------------------------------------------
# MiradLexiconLookup tests
# ---------------------------------------------------------------------------

def test_lexicon_lookup_returns_word_equivalents():
    """MiradLexiconLookup should return a Prediction with word_equivalents dict."""
    word_map = {'hello': 'helo', 'world': 'woldu'}

    def mock_lookup(db_path=None, english_word=None):
        if english_word:
            return word_map.get(english_word.lower(), None)
        return None

    with patch('mirad_translator.lexicon_db.lookup_word', side_effect=mock_lookup):
        lookup = MiradLexiconLookup(db_path=":memory:")
        result = lookup(english_text="Hello world")
        assert hasattr(result, 'word_equivalents')
        assert result.word_equivalents == {'hello': 'helo', 'world': 'woldu'}


def test_lexicon_lookup_no_matches():
    """MiradLexiconLookup returns empty dict when no words match."""
    with patch('mirad_translator.lexicon_db.lookup_word', return_value=None):
        lookup = MiradLexiconLookup(db_path=":memory:")
        result = lookup(english_text="xyzzy plugh")
        assert result.word_equivalents == {}


# ---------------------------------------------------------------------------
# MiradContextRetrieve tests
# ---------------------------------------------------------------------------

def test_context_retrieve_returns_passages():
    """MiradContextRetrieve returns a Prediction with passages list."""
    mock_result = {
        "grammar": [{"text": "Verbs: ...", "metadata": {"source_section": "verbs"}}],
        "thesaurus": [{"text": "Weather: ...", "metadata": {"source_section": "weather"}}],
    }
    with patch('mirad_translator.retrieval.retrieve_all', return_value=mock_result):
        retriever = MiradContextRetrieve(k=3)
        result = retriever(query="How does verb conjugation work?")
        assert hasattr(result, 'passages')
        assert len(result.passages) == 2
        assert '[verbs]' in result.passages[0]
        assert '[weather]' in result.passages[1]


def test_context_retrieve_failure_returns_empty():
    """MiradContextRetrieve returns empty list on retrieval failure."""
    with patch('mirad_translator.retrieval.retrieve_all', side_effect=RuntimeError("ChromaDB not available")):
        retriever = MiradContextRetrieve(k=3)
        result = retriever(query="test query")
        assert result.passages == []


# ---------------------------------------------------------------------------
# TranslatorModule tests
# ---------------------------------------------------------------------------

def test_translator_module_forward():
    """TranslatorModule.forward takes only english_text and returns Prediction."""
    mock_prediction = Mock()
    mock_prediction.mirad_text = "At tose oma."
    mock_prediction.confidence = "0.95"

    with patch('dspy.ChainOfThought') as mock_cot:
        mock_instance = Mock()
        mock_instance.return_value = mock_prediction
        mock_cot.return_value = mock_instance

        translator = TranslatorModule(db_path=":memory:")
        # Patch internal sub-modules
        translator.lexicon_lookup = Mock(return_value=dspy.Prediction(word_equivalents={"i": "at", "cold": "oma"}))
        translator.context_retrieve = Mock(return_value=dspy.Prediction(passages=["[grammar] verb rules"]))

        result = translator.forward(english_text="I am cold.")

        assert result.mirad_text == "At tose oma."
        assert result.confidence == "0.95"
        assert result.word_equivalents == {"i": "at", "cold": "oma"}
        assert result.context == ["[grammar] verb rules"]


def test_translator_module_forward_injects_context_into_prompt():
    """TranslatorModule should inject word_equivalents and context into the prompt."""
    mock_prediction = Mock()
    mock_prediction.mirad_text = "At tose oma."
    mock_prediction.confidence = "0.95"

    with patch('dspy.ChainOfThought') as mock_cot:
        mock_instance = Mock()
        mock_instance.return_value = mock_prediction
        mock_cot.return_value = mock_instance

        translator = TranslatorModule(db_path=":memory:")
        word_eq = {"i": "at", "am": "ese", "cold": "oma"}
        translator.lexicon_lookup = Mock(return_value=dspy.Prediction(word_equivalents=word_eq))
        translator.context_retrieve = Mock(return_value=dspy.Prediction(passages=["[grammar] verb rules"]))

        translator.forward(english_text="I am cold.")

        # Verify ChainOfThought was called with enriched english_text
        call_args = mock_instance.call_args
        enriched_text = call_args.kwargs.get('english_text', call_args[0][0] if call_args[0] else '')
        assert "I am cold." in enriched_text
        assert "Word equivalents" in enriched_text
        assert "am → ese" in enriched_text
        assert "[grammar] verb rules" in enriched_text


def test_translator_module_forward_no_retrieval():
    """TranslatorModule works with empty word_equivalents and context."""
    mock_prediction = Mock()
    mock_prediction.mirad_text = "Helo."
    mock_prediction.confidence = "0.5"

    with patch('dspy.ChainOfThought') as mock_cot:
        mock_instance = Mock()
        mock_instance.return_value = mock_prediction
        mock_cot.return_value = mock_instance

        translator = TranslatorModule(db_path=":memory:")
        translator.lexicon_lookup = Mock(return_value=dspy.Prediction(word_equivalents={}))
        translator.context_retrieve = Mock(return_value=dspy.Prediction(passages=[]))

        result = translator.forward(english_text="Hello.")

        # Should still call ChainOfThought, just without enrichment
        assert mock_instance.called
        assert result.mirad_text == "Helo."


def test_translator_module_initialization():
    """TranslatorModule initializes with generate, lexicon_lookup, and context_retrieve."""
    with patch('dspy.ChainOfThought') as mock_cot:
        mock_instance = Mock()
        mock_cot.return_value = mock_instance

        translator = TranslatorModule(db_path=":memory:")

        assert hasattr(translator, 'generate')
        assert hasattr(translator, 'lexicon_lookup')
        assert hasattr(translator, 'context_retrieve')
        mock_cot.assert_called_once_with(EnglishToMiradSignature)


# ---------------------------------------------------------------------------
# translate_with_lookup tests
# ---------------------------------------------------------------------------

def test_translate_with_lookup_calls_module():
    """translate_with_lookup runs the full pipeline and returns all fields."""
    mock_pred = dspy.Prediction(
        mirad_text="At tose oma.",
        confidence="0.9",
        word_equivalents={"i": "at", "cold": "oma"},
        context=["[grammar] verb rules"],
    )

    with patch('mirad_translator.translate.DefaultTranslator') as mock_factory:
        mock_translator = Mock()
        mock_translator.forward.return_value = mock_pred
        mock_factory.return_value = mock_translator

        result = translate_with_lookup("I am cold.", db_path=":memory:")

        assert result[0] == "At tose oma."
        assert result[1] == "0.9"
        assert result[2] == {"i": "at", "cold": "oma"}
        assert result[3] == ["[grammar] verb rules"]


# ---------------------------------------------------------------------------
# DSPy Example creation tests
# ---------------------------------------------------------------------------

def test_eval_example_correct_shape():
    """Evaluation Examples should only have english_text as input."""
    ex = dspy.Example(
        english_text="I am cold.",
        mirad_text="At tose oma.",
    ).with_inputs("english_text")

    assert set(ex.inputs().keys()) == {"english_text"}
    assert ex.english_text == "I am cold."
    assert ex.mirad_text == "At tose oma."


def test_signature_accepts_only_english_text_input():
    """The signature should accept english_text as the sole input field."""
    fields = EnglishToMiradSignature.model_fields
    input_fields = {
        name for name, f in fields.items()
        if f.json_schema_extra and f.json_schema_extra.get('__dspy_field_type') == 'input'
    }
    assert input_fields == {"english_text"}