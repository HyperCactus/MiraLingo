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
    MiradToEnglishSignature,
    MiradToEnglishModule,
    MiradLexiconReverseLookup,
    MiradSemanticReverseLexiconLookup,
    _MIRAD_TO_ENGLISH_RULES,
)


# ---------------------------------------------------------------------------
# EnglishToMiradSignature tests
# ---------------------------------------------------------------------------

def test_translate_signature_fields():
    """Signature should have english_text, word_equivalents, context_passages as inputs."""
    # Input fields
    assert 'english_text' in EnglishToMiradSignature.input_fields
    assert 'word_equivalents' in EnglishToMiradSignature.input_fields
    assert 'context_passages' in EnglishToMiradSignature.input_fields
    # Output fields — no confidence
    assert 'mirad_text' in EnglishToMiradSignature.output_fields
    assert 'confidence' not in EnglishToMiradSignature.output_fields


def test_signature_docstring_contains_grammar_rules():
    """Signature docstring embeds grammar rules for DSPy 3.x system prompt."""
    # The grammar rules constant must contain key Mirad rules
    assert 'SVO' in _MIRAD_GRAMMAR_RULES or 'Subject + verb' in _MIRAD_GRAMMAR_RULES
    assert 'Simple active endings' in _MIRAD_GRAMMAR_RULES or '-e present' in _MIRAD_GRAMMAR_RULES
    assert 'at I/me' in _MIRAD_GRAMMAR_RULES


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

def test_context_retrieve_returns_grammar_passages_only():
    """MiradContextRetrieve returns grammar rules as individual rule passages."""
    mock_grammar_result = [
        {
            "text": "Verbs: ...",
            "distance": 0.3,
            "cosine_similarity": 0.96,
            "importance": 0.9,
            "combined_score": 1.71,
            "metadata": {"source_section": "verbs", "rule_id": "verb.test"},
            "rule": {"id": "verb.test", "description": "Test verb rule", "pseudocode": "", "examples": []},
        }
    ]
    with patch('mirad_translator.retrieval.retrieve_grammar', return_value=mock_grammar_result):
        retriever = MiradContextRetrieve(k=3)
        result = retriever(query="How does verb conjugation work?")
        assert hasattr(result, 'passages')
        assert len(result.passages) == 1
        assert 'verb.test' in result.passages[0]
        assert 'Test verb rule' in result.passages[0]


def test_context_retrieve_returns_structured_grammar_rule_payloads():
    """Structured grammar rules are formatted and exposed for rule-id tracking."""
    mock_rule = {
        "text": "tense rule",
        "distance": 0.3,
        "cosine_similarity": 0.96,
        "importance": 0.9,
        "combined_score": 1.71,
        "metadata": {"rule_id": "verb.tense"},
        "rule": {"id": "verb.tense", "description": "Tense suffixes", "pseudocode": "", "examples": []},
    }
    with patch('mirad_translator.retrieval.retrieve_grammar', return_value=[mock_rule]):
        retriever = MiradContextRetrieve(k=3)
        result = retriever(query="past tense")
        assert result.grammar_rules == [mock_rule]
        assert len(result.passages) == 1
        assert 'verb.tense' in result.passages[0]
        assert 'Tense suffixes' in result.passages[0]


def test_context_retrieve_failure_returns_empty():
    """MiradContextRetrieve returns empty list on retrieval failure."""
    with patch('mirad_translator.retrieval.retrieve_grammar', side_effect=RuntimeError("ChromaDB not available")):
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

    mock_vocab = {
        "word_equivalents": {"i": "at", "cold": "oma"},
        "relevant_words": {},
        "back_translation": {"at": "I, me", "oma": "cold, hill"},
    }

    with patch('dspy.ChainOfThought') as mock_cot, \
         patch('mirad_translator.semantic_lexicon.semantic_lookup_structured', return_value=mock_vocab):
        mock_instance = Mock()
        mock_instance.return_value = mock_prediction
        mock_cot.return_value = mock_instance

        translator = TranslatorModule(db_path=":memory:")
        translator.context_retrieve = Mock(return_value=dspy.Prediction(passages=["Rule ID: verb.test\nDescription: Test"]))

        result = translator.forward(english_text="I am cold.")

        assert result.mirad_text == "At tose oma."
        assert "i" in result.word_equivalents
        assert "cold" in result.word_equivalents
        assert result.context == ["Rule ID: verb.test\nDescription: Test"]


def test_translator_module_forward_passes_separate_fields():
    """TranslatorModule should pass word_equivalents and context_passages as separate fields."""
    mock_prediction = Mock()
    mock_prediction.mirad_text = "At tose oma."

    mock_vocab = {
        "word_equivalents": {"i": "at", "am": "ese", "cold": "oma"},
        "relevant_words": {},
        "back_translation": {},
    }

    with patch('dspy.ChainOfThought') as mock_cot, \
         patch('mirad_translator.semantic_lexicon.semantic_lookup_structured', return_value=mock_vocab):
        mock_instance = Mock()
        mock_instance.return_value = mock_prediction
        mock_cot.return_value = mock_instance

        translator = TranslatorModule(db_path=":memory:")
        translator.context_retrieve = Mock(return_value=dspy.Prediction(passages=["Rule ID: verb.test\nDescription: Test"]))

        translator.forward(english_text="I am cold.")

        # Verify ChainOfThought was called with separate input fields
        call_kwargs = mock_instance.call_args.kwargs
        assert call_kwargs['english_text'] == "I am cold."
        assert "at" in call_kwargs['word_equivalents']
        assert "ese" in call_kwargs['word_equivalents']


def test_translator_module_forward_no_retrieval():
    """TranslatorModule works with empty word_equivalents and context."""
    mock_prediction = Mock()
    mock_prediction.mirad_text = "Helo."

    mock_vocab = {
        "word_equivalents": {},
        "relevant_words": {},
        "back_translation": {},
    }

    with patch('dspy.ChainOfThought') as mock_cot, \
         patch('mirad_translator.semantic_lexicon.semantic_lookup_structured', return_value=mock_vocab):
        mock_instance = Mock()
        mock_instance.return_value = mock_prediction
        mock_cot.return_value = mock_instance

        translator = TranslatorModule(db_path=":memory:")
        translator.context_retrieve = Mock(return_value=dspy.Prediction(passages=[]))

        result = translator.forward(english_text="Hello.")

        # Should still call ChainOfThought, with empty intermediates
        assert mock_instance.called
        call_kwargs = mock_instance.call_args.kwargs
        assert call_kwargs['word_equivalents'] == ""
        assert call_kwargs['context_passages'] == ""
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
        word_equivalents={"i": "at", "cold": "oma"},
        context=["[grammar] verb rules"],
    )

    with patch('mirad_translator.translate.DefaultTranslator') as mock_factory:
        mock_translator = Mock()
        mock_translator.forward.return_value = mock_pred
        mock_factory.return_value = mock_translator

        result = translate_with_lookup("I am cold.", db_path=":memory:")

        assert result[0] == "At tose oma."
        assert result[1] == {"i": "at", "cold": "oma"}
        assert result[2] == ["[grammar] verb rules"]


# ---------------------------------------------------------------------------
# DSPy Example creation tests
# ---------------------------------------------------------------------------

def test_eval_example_correct_shape():
    """Evaluation Examples should have english_text as input (Module computes intermediates)."""
    ex = dspy.Example(
        english_text="I am cold.",
        mirad_text="At tose oma.",
    ).with_inputs("english_text")

    assert set(ex.inputs().keys()) == {"english_text"}
    assert ex.english_text == "I am cold."
    assert ex.mirad_text == "At tose oma."


def test_enriched_example_correct_shape():
    """Enriched examples for LabeledFewShot should have all signature input fields."""
    ex = dspy.Example(
        english_text="I am cold.",
        word_equivalents="i → at\ncold → oma",
        context_passages="",
        mirad_text="At tose oma.",
    ).with_inputs("english_text", "word_equivalents", "context_passages")

    assert set(ex.inputs().keys()) == {"english_text", "word_equivalents", "context_passages"}
    assert ex.english_text == "I am cold."
    assert "i → at" in ex.word_equivalents


def test_signature_accepts_all_input_fields():
    """The signature should accept english_text, word_equivalents, context_passages as inputs."""
    fields = EnglishToMiradSignature.model_fields
    input_fields = {
        name for name, f in fields.items()
        if f.json_schema_extra and f.json_schema_extra.get('__dspy_field_type') == 'input'
    }
    output_fields = {
        name for name, f in fields.items()
        if f.json_schema_extra and f.json_schema_extra.get('__dspy_field_type') == 'output'
    }
    assert input_fields == {"english_text", "normalized_structure", "word_equivalents", "context_passages"}
    assert output_fields == {"mirad_text", "used_rule_ids"}
    assert "confidence" not in output_fields


# ---------------------------------------------------------------------------
# MiradToEnglishSignature tests (reverse direction)
# ---------------------------------------------------------------------------

def test_mir_to_english_signature_fields():
    """MiradToEnglishSignature should have mirad_text, word_equivalents, context_passages as inputs."""
    # Input fields
    assert 'mirad_text' in MiradToEnglishSignature.input_fields
    assert 'word_equivalents' in MiradToEnglishSignature.input_fields
    assert 'context_passages' in MiradToEnglishSignature.input_fields
    # Output fields
    assert 'english_text' in MiradToEnglishSignature.output_fields
    assert 'mirad_text' not in MiradToEnglishSignature.output_fields
    assert 'confidence' not in MiradToEnglishSignature.output_fields


def test_mir_to_english_signature_docstring():
    """MiradToEnglishSignature docstring embeds Mir→En grammar rules for DSPy."""
    assert 'SVO' in _MIRAD_TO_ENGLISH_RULES or 'Mirad' in _MIRAD_TO_ENGLISH_RULES
    assert 'ha = the' in _MIRAD_TO_ENGLISH_RULES
    assert 'at=I' in _MIRAD_TO_ENGLISH_RULES or 'at=I/me' in _MIRAD_TO_ENGLISH_RULES
    # Verify it covers the reverse direction vocabulary
    assert 'voy = not' in _MIRAD_TO_ENGLISH_RULES


# ---------------------------------------------------------------------------
# MiradLexiconReverseLookup tests (Mirad→English)
# ---------------------------------------------------------------------------

def test_mirad_lexicon_reverse_lookup_returns_word_equivalents():
    """MiradLexiconReverseLookup returns Mirad→English word pairs."""
    # Mirad words are lowercase in the DB; lookup is case-sensitive
    word_map = {'at': 'i', 'tose': 'cold', 'oma': 'weather'}

    def mock_lookup(db_path=None, mirad_word=None):
        if mirad_word:
            return word_map.get(mirad_word, None)
        return None

    with patch('mirad_translator.lexicon_db.lookup_mirad_word_candidates', side_effect=lambda db_path=None, mirad_word=None: [word_map[mirad_word]] if mirad_word in word_map else []):
        lookup = MiradLexiconReverseLookup(db_path=":memory:")
        # Use lowercase — Mirad words in the DB are lowercase and lookup is case-sensitive
        result = lookup(mirad_text="at tose oma")
        assert hasattr(result, 'word_equivalents')
        assert result.word_equivalents == {'at': 'i', 'tose': 'cold', 'oma': 'weather'}


def test_mirad_lexicon_reverse_lookup_no_matches():
    """MiradLexiconReverseLookup returns empty dict when no words match."""
    with patch('mirad_translator.lexicon_db.lookup_mirad_word_candidates', return_value=[]):
        lookup = MiradLexiconReverseLookup(db_path=":memory:")
        result = lookup(mirad_text="xyzzy plugh")
        assert result.word_equivalents == {}


def test_mirad_semantic_reverse_lookup_enriches_exact_matches_with_semantic_neighbors():
    """Mirad→English lookup exact-matches Mirad first, then searches semantically near the English equivalent."""
    def mock_reverse_lookup(db_path=None, mirad_word=None):
        return ['big'] if mirad_word == 'aga' else []

    def mock_forward_lookup(db_path=None, english_word=None):
        return {'big': ['aga'], 'large': ['aga'], 'huge': ['zyaga']}.get(english_word, [])

    def mock_semantic_lookup(english_word, top_k, min_similarity, include_exact):
        assert english_word == 'big'
        assert top_k == 5
        assert include_exact is True
        return [
            {'english': 'big', 'mirad': 'aga', 'cosine_similarity': 1.0, 'is_exact': True},
            {'english': 'large', 'mirad': 'aga', 'cosine_similarity': 0.91, 'is_exact': False},
            {'english': 'huge', 'mirad': 'zyaga', 'cosine_similarity': 0.86, 'is_exact': False},
        ]

    with patch('mirad_translator.lexicon_db.lookup_mirad_word_candidates', side_effect=mock_reverse_lookup), \
         patch('mirad_translator.lexicon_db.lookup_word_candidates', side_effect=mock_forward_lookup), \
         patch('mirad_translator.semantic_lexicon.semantic_lookup', side_effect=mock_semantic_lookup):
        lookup = MiradSemanticReverseLexiconLookup(db_path=":memory:", top_k_per_word=5, max_total_pairs=6)
        result = lookup(mirad_text="aga")
        assert result.word_equivalents == {
            'aga': 'big',
            'big': 'aga',
            'large': 'aga',
            'huge': 'zyaga',
        }


def test_mirad_semantic_reverse_lookup_falls_back_to_exact_reverse_lookup():
    """Semantic failures still return exact Mirad→English equivalents."""
    def mock_reverse_lookup(db_path=None, mirad_word=None):
        return ['house']

    with patch('mirad_translator.lexicon_db.lookup_mirad_word_candidates', side_effect=mock_reverse_lookup), \
         patch('mirad_translator.semantic_lexicon.semantic_lookup', side_effect=RuntimeError('index unavailable')):
        lookup = MiradSemanticReverseLexiconLookup(db_path=":memory:")
        result = lookup(mirad_text="tam")
        assert result.word_equivalents == {'tam': 'house'}


# ---------------------------------------------------------------------------
# MiradToEnglishModule tests
# ---------------------------------------------------------------------------

def test_mirad_to_english_module_initialization():
    """MiradToEnglishModule initializes with generate, lexicon_lookup, and context_retrieve."""
    with patch('dspy.ChainOfThought') as mock_cot:
        mock_instance = Mock()
        mock_cot.return_value = mock_instance

        module = MiradToEnglishModule(db_path=":memory:")

        assert hasattr(module, 'generate')
        assert hasattr(module, 'lexicon_lookup')
        assert hasattr(module, 'context_retrieve')
        mock_cot.assert_called_once_with(MiradToEnglishSignature)


def test_mirad_to_english_module_forward():
    """MiradToEnglishModule.forward takes mirad_text and returns Prediction with english_text."""
    mock_prediction = Mock()
    mock_prediction.english_text = "I am cold."

    with patch('dspy.ChainOfThought') as mock_cot:
        mock_instance = Mock()
        mock_instance.return_value = mock_prediction
        mock_cot.return_value = mock_instance

        module = MiradToEnglishModule(db_path=":memory:")
        module.lexicon_lookup = Mock(return_value=dspy.Prediction(word_equivalents={"at": "i", "tose": "am cold"}))
        module.context_retrieve = Mock(return_value=dspy.Prediction(passages=["[grammar] pronoun rules"]))

        result = module.forward(mirad_text="At tose oma.")

        assert result.english_text == "I am cold."
        assert result.word_equivalents == {"at": "i", "tose": "am cold"}
        assert result.context == ["[grammar] pronoun rules"]


def test_mirad_to_english_module_forward_no_retrieval():
    """MiradToEnglishModule works with empty word_equivalents and context."""
    mock_prediction = Mock()
    mock_prediction.english_text = "Hello."

    with patch('dspy.ChainOfThought') as mock_cot:
        mock_instance = Mock()
        mock_instance.return_value = mock_prediction
        mock_cot.return_value = mock_instance

        module = MiradToEnglishModule(db_path=":memory:")
        module.lexicon_lookup = Mock(return_value=dspy.Prediction(word_equivalents={}))
        module.context_retrieve = Mock(return_value=dspy.Prediction(passages=[]))

        result = module.forward(mirad_text="Helo.")

        assert mock_instance.called
        call_kwargs = mock_instance.call_args.kwargs
        assert call_kwargs['mirad_text'] == "Helo."
        assert call_kwargs['word_equivalents'] == ""
        assert call_kwargs['context_passages'] == ""
        assert result.english_text == "Hello."


def test_mirad_to_english_module_forward_passes_reverse_format():
    """MiradToEnglishModule formats word equivalents as 'mirad → english'."""
    mock_prediction = Mock()
    mock_prediction.english_text = "I know the answer."

    with patch('dspy.ChainOfThought') as mock_cot:
        mock_instance = Mock()
        mock_instance.return_value = mock_prediction
        mock_cot.return_value = mock_instance

        module = MiradToEnglishModule(db_path=":memory:")
        module.lexicon_lookup = Mock(return_value=dspy.Prediction(word_equivalents={"at": "i", "te": "know", "ha": "the"}))
        module.context_retrieve = Mock(return_value=dspy.Prediction(passages=[]))

        result = module.forward(mirad_text="At te ha dud.")

        call_kwargs = mock_instance.call_args.kwargs
        # Should be formatted as "mirad → english"
        assert "at → i" in call_kwargs['word_equivalents']
        assert "te → know" in call_kwargs['word_equivalents']
        assert "ha → the" in call_kwargs['word_equivalents']
        assert result.english_text == "I know the answer."


# ---------------------------------------------------------------------------
# MiradToEnglish Example shape tests
# ---------------------------------------------------------------------------

def test_mir_to_english_example_correct_shape():
    """Evaluation Examples for Mir→En should have mirad_text as input."""
    ex = dspy.Example(
        mirad_text="At tose oma.",
        english_text="I am cold.",
    ).with_inputs("mirad_text")

    assert set(ex.inputs().keys()) == {"mirad_text"}
    assert ex.mirad_text == "At tose oma."
    assert ex.english_text == "I am cold."