from __future__ import annotations

import sys
import types

from fastapi.testclient import TestClient

from mirad_webapp.api import create_app


def _install_lexicon_db_module(
    monkeypatch,
    *,
    lookup_word_candidates,
    lookup_mirad_word_candidates,
) -> None:
    package = sys.modules.get("mirad_translator") or types.ModuleType("mirad_translator")
    module = types.ModuleType("mirad_translator.lexicon_db")
    module.lookup_word_candidates = lookup_word_candidates  # type: ignore[attr-defined]
    module.lookup_mirad_word_candidates = lookup_mirad_word_candidates  # type: ignore[attr-defined]
    package.lexicon_db = module  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "mirad_translator", package)
    monkeypatch.setitem(sys.modules, "mirad_translator.lexicon_db", module)


def _install_semantic_lexicon_module(
    monkeypatch,
    *,
    semantic_lookup,
    semantic_lookup_mirad,
) -> None:
    package = sys.modules.get("mirad_translator") or types.ModuleType("mirad_translator")
    module = types.ModuleType("mirad_translator.semantic_lexicon")
    module.semantic_lookup = semantic_lookup  # type: ignore[attr-defined]
    module.semantic_lookup_mirad = semantic_lookup_mirad  # type: ignore[attr-defined]
    package.semantic_lexicon = module  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "mirad_translator", package)
    monkeypatch.setitem(sys.modules, "mirad_translator.semantic_lexicon", module)


def test_lookup_exact_en_to_mir_returns_immediate_sql_hit(monkeypatch) -> None:
    def fake_word_candidates(*, english_word: str, db_path=None):
        assert english_word == "hello"
        return ["hay"]

    def unused_mirad_candidates(*, mirad_word: str, db_path=None):
        raise AssertionError("mir_to_en exact lookup should not run for en_to_mir requests")

    _install_lexicon_db_module(
        monkeypatch,
        lookup_word_candidates=fake_word_candidates,
        lookup_mirad_word_candidates=unused_mirad_candidates,
    )

    client = TestClient(create_app())

    response = client.get("/lookup/exact", params={"q": "hello", "direction": "en_to_mir"})

    assert response.status_code == 200
    assert response.json() == [
        {
            "english": "hello",
            "mirad": "hay",
            "cosine_similarity": 1.0,
            "is_exact": True,
        }
    ]


def test_lookup_exact_mir_to_en_returns_immediate_sql_hit(monkeypatch) -> None:
    def unused_word_candidates(*, english_word: str, db_path=None):
        raise AssertionError("en_to_mir exact lookup should not run for mir_to_en requests")

    def fake_mirad_candidates(*, mirad_word: str, db_path=None):
        assert mirad_word == "te"
        return ["the"]

    _install_lexicon_db_module(
        monkeypatch,
        lookup_word_candidates=unused_word_candidates,
        lookup_mirad_word_candidates=fake_mirad_candidates,
    )

    client = TestClient(create_app())

    response = client.get("/lookup/exact", params={"q": "te", "direction": "mir_to_en"})

    assert response.status_code == 200
    assert response.json() == [
        {
            "mirad": "te",
            "english": "the",
            "cosine_similarity": 1.0,
            "is_exact": True,
        }
    ]


def test_lookup_en_to_mir_returns_semantic_hits(monkeypatch) -> None:
    def fake_lookup(*, english_word: str, top_k: int, min_similarity: float, include_exact: bool):
        assert english_word == "run"
        assert top_k == 2
        assert min_similarity == 0.5
        assert include_exact is True
        return [
            {
                "english": "run",
                "mirad": "xebwa",
                "cosine_similarity": 1.0,
                "is_exact": True,
                "distance": 0.0,
            },
            {
                "english": "sprint",
                "mirad": "glopa",
                "cosine_similarity": 0.8123,
                "is_exact": False,
                "distance": 0.6123,
            },
        ]

    def fake_lookup_mirad(*, mirad_word: str, top_k: int, min_similarity: float, include_exact: bool):
        raise AssertionError("mir_to_en lookup should not run for en_to_mir requests")

    _install_semantic_lexicon_module(
        monkeypatch,
        semantic_lookup=fake_lookup,
        semantic_lookup_mirad=fake_lookup_mirad,
    )

    client = TestClient(create_app())

    response = client.get("/lookup", params={"q": "run", "direction": "en_to_mir", "top_k": 2})

    assert response.status_code == 200
    assert response.json() == [
        {
            "english": "run",
            "mirad": "xebwa",
            "cosine_similarity": 1.0,
            "is_exact": True,
        },
        {
            "english": "sprint",
            "mirad": "glopa",
            "cosine_similarity": 0.8123,
            "is_exact": False,
        },
    ]


def test_lookup_mir_to_en_returns_semantic_hits(monkeypatch) -> None:
    def fake_lookup(*, english_word: str, top_k: int, min_similarity: float, include_exact: bool):
        raise AssertionError("en_to_mir lookup should not run for mir_to_en requests")

    def fake_lookup_mirad(*, mirad_word: str, top_k: int, min_similarity: float, include_exact: bool):
        assert mirad_word == "te"
        assert top_k == 3
        assert min_similarity == 0.5
        assert include_exact is True
        return [
            {
                "mirad": "te",
                "english": "the",
                "cosine_similarity": 1.0,
                "is_exact": True,
                "distance": 0.0,
            },
            {
                "mirad": "tad",
                "english": "this",
                "cosine_similarity": 0.7789,
                "is_exact": False,
                "distance": 0.665,
            },
        ]

    _install_semantic_lexicon_module(
        monkeypatch,
        semantic_lookup=fake_lookup,
        semantic_lookup_mirad=fake_lookup_mirad,
    )

    client = TestClient(create_app())

    response = client.get("/lookup", params={"q": "te", "direction": "mir_to_en"})

    assert response.status_code == 200
    assert response.json() == [
        {
            "mirad": "te",
            "english": "the",
            "cosine_similarity": 1.0,
            "is_exact": True,
        },
        {
            "mirad": "tad",
            "english": "this",
            "cosine_similarity": 0.7789,
            "is_exact": False,
        },
    ]


def test_lookup_returns_service_unavailable_when_semantic_search_fails(monkeypatch) -> None:
    def failing_lookup(*, english_word: str, top_k: int, min_similarity: float, include_exact: bool):
        raise RuntimeError("chromadb not installed")

    def unused_lookup_mirad(*, mirad_word: str, top_k: int, min_similarity: float, include_exact: bool):
        raise AssertionError("mir_to_en lookup should not run for en_to_mir requests")

    _install_semantic_lexicon_module(
        monkeypatch,
        semantic_lookup=failing_lookup,
        semantic_lookup_mirad=unused_lookup_mirad,
    )

    client = TestClient(create_app())

    response = client.get("/lookup", params={"q": "run", "direction": "en_to_mir"})

    assert response.status_code == 503
    payload = response.json()
    assert payload["error"] == "semantic search unavailable"
    assert payload["detail"] == "chromadb not installed"
