"""Tests for retrieval module (ChromaDB)."""
import pytest, os, sys
from pathlib import Path

SRC = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, SRC)


def test_chunk_counts_returns_dict():
    from mirad_translator.retrieval import get_chunk_counts
    counts = get_chunk_counts()
    assert isinstance(counts, dict)
    assert "grammar" in counts
    assert "thesaurus" in counts


def test_retrieval_module_has_required_functions():
    from mirad_translator import retrieval
    assert callable(retrieval.retrieve_grammar)
    assert callable(retrieval.retrieve_thesaurus)
    assert callable(retrieval.retrieve_all)
    assert callable(retrieval.build_indexes)
    assert callable(retrieval.get_chunk_counts)


def test_retrieve_all_returns_structure():
    try:
        from mirad_translator.retrieval import retrieve_all
        results = retrieve_all("grammar rules verb conjugation", top_k=2)
        assert isinstance(results, dict)
        assert "grammar" in results
        assert "thesaurus" in results
        assert all(isinstance(r, list) for r in results.values())
    except RuntimeError as e:
        if "chromadb" in str(e) or "sentence" in str(e):
            pytest.skip(f"Missing dependency: {e}")
        raise


def test_retrieve_grammar_returns_list_or_skips():
    try:
        from mirad_translator.retrieval import retrieve_grammar
        results = retrieve_grammar("verb conjugation rules", top_k=2)
        assert isinstance(results, list)
        assert len(results) <= 2
        for r in results:
            assert "text" in r
            assert "distance" in r
    except RuntimeError as e:
        if "chromadb" in str(e) or "sentence" in str(e):
            pytest.skip(f"Missing dependency: {e}")
        raise

def test_load_grammar_rules_flattens_nested_json_rule_payloads():
    from mirad_translator.retrieval import _load_grammar_rules

    rules = _load_grammar_rules()
    assert rules
    first = rules[0]

    assert first["id"] == "orthography.alphabet.roman_no_diacritics"
    assert "Native Mirad words" in first["description"]
    assert "token.is_native_mirad" in first["pseudocode"]
    assert not first["description"].startswith("{")


def test_format_rule_document_contains_structured_fields_not_dict_repr():
    from mirad_translator.retrieval import _format_rule_document, _load_grammar_rules

    doc = _format_rule_document(_load_grammar_rules()[0])

    assert "ID: orthography.alphabet.roman_no_diacritics" in doc
    assert "DESCRIPTION: Native Mirad words" in doc
    assert "PSEUDOCODE: if token.is_native_mirad:" in doc
    assert "'description':" not in doc
