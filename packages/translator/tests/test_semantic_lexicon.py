from __future__ import annotations

from mirad_translator import semantic_lexicon as module


class _FakeEmbedder:
    def encode(self, texts, show_progress_bar=False):
        assert texts == ["the"]

        class _Vec:
            def tolist(self):
                return [[0.1, 0.2, 0.3]]

        return _Vec()


class _FakeCollection:
    def query(self, query_embeddings, n_results):
        assert query_embeddings == [[0.1, 0.2, 0.3]]
        assert n_results == 4
        return {
            "documents": [["the", "there", "this", "the"]],
            "distances": [[0.0, 0.4, 0.5, 0.0]],
            "metadatas": [[
                {"mirad": "ha"},
                {"mirad": "be hum"},
                {"mirad": "tad"},
                {"mirad": "ha"},
            ]],
        }


def test_semantic_lookup_mirad_keeps_input_mirad_word_for_exact_hit(monkeypatch) -> None:
    monkeypatch.setattr(module, "lookup_mirad_word_candidates", lambda mirad_word: ["the"])
    monkeypatch.setattr(module, "_get_lexicon_collection", lambda: _FakeCollection())
    monkeypatch.setattr(module, "_get_embedder", lambda: _FakeEmbedder())

    hits = module.semantic_lookup_mirad("ha", top_k=3, min_similarity=0.5, include_exact=True)

    assert hits[0] == {
        "mirad": "ha",
        "english": "the",
        "distance": 0.0,
        "cosine_similarity": 1.0,
        "is_exact": True,
    }
    assert len([hit for hit in hits if hit["is_exact"]]) == 1
    assert hits[1]["mirad"] == "be hum"
    assert hits[1]["english"] == "there"
