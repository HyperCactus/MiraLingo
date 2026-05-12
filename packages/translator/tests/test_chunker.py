"""Tests for chunker module."""
import pytest, os, sys
from pathlib import Path

SRC = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, SRC)


def test_count_tokens():
    from mirad_translator.chunker import count_tokens
    assert count_tokens("hello world") == 2
    assert count_tokens("") == 0
    assert count_tokens("one two three four five") == 5


def test_chunk_by_paragraphs_basic():
    from mirad_translator.chunker import chunk_by_paragraphs
    chunks = chunk_by_paragraphs("Para one.\n\nPara two.\n\nPara three.", max_tokens=10, overlap_tokens=2)
    assert len(chunks) >= 1
    assert all(isinstance(c, str) for c in chunks)


def test_chunk_grammar_returns_list():
    from mirad_translator.chunker import chunk_grammar
    chunks = chunk_grammar()
    assert isinstance(chunks, list)
    assert len(chunks) > 0
    assert all(isinstance(c, str) for c in chunks)


def test_chunk_thesaurus_returns_list():
    from mirad_translator.chunker import chunk_thesaurus
    chunks = chunk_thesaurus()
    assert isinstance(chunks, list)
    assert len(chunks) > 0
    assert all(isinstance(c, str) for c in chunks)


def test_grammar_chunks_reasonable_size():
    from mirad_translator.chunker import chunk_grammar, count_tokens
    chunks = chunk_grammar()
    for c in chunks[:10]:
        assert count_tokens(c) < 2000


def test_thesaurus_chunks_reasonable_size():
    from mirad_translator.chunker import chunk_thesaurus, count_tokens
    chunks = chunk_thesaurus()
    for c in chunks[:10]:
        assert count_tokens(c) < 2000


def test_grammar_sections_differentiated():
    from mirad_translator.chunker import chunk_grammar
    chunks = chunk_grammar()
    # Multiple distinct chunks
    assert len(chunks) >= 5


def test_thesaurus_sections_differentiated():
    from mirad_translator.chunker import chunk_thesaurus
    chunks = chunk_thesaurus()
    assert len(chunks) >= 5