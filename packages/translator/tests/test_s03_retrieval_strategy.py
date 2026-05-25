import json

from mirad_translator.retrieval_strategy import RetrievalStrategyConfig, build_retrieval_payload


DEVSET_PATH = "data/eval/devset_s01_bidirectional.json"


def _load_devset():
    with open(DEVSET_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


def test_build_retrieval_payload_en_to_mir_uses_semantic_pairs_and_deduped_grammar():
    devset = _load_devset()
    example = next(item for item in devset if item["id"] == "s01-002-en-to-mir-comparison-vyel")

    def fake_semantic_lookup(text, **kwargs):
        assert text == example["source_text"]
        assert kwargs["top_k_per_word"] == 2
        return {"house": "tam", "bigger": "aga", "my": "ata"}

    def fake_retrieve_all(query, top_k):
        assert "comparison-linker" in query
        assert top_k == 4
        return {
            "grammar": [
                {
                    "text": "comparison rule text",
                    "metadata": {"source_section": "comparisons", "rule_id": "cmp.vyel"},
                    "rule": {"id": "cmp.vyel", "description": "Use vyel after comparative forms."},
                },
                {
                    "text": "duplicate id ignored",
                    "metadata": {"source_section": "comparisons", "rule_id": "cmp.vyel"},
                    "rule": {"id": "cmp.vyel", "description": "Use vyel after comparative forms."},
                },
                {
                    "text": "possession rule text",
                    "metadata": {"source_section": "noun_phrases", "rule_id": "np.possessive"},
                    "rule": {"id": "np.possessive", "description": "Possessives add -a to pronouns."},
                },
            ]
        }

    payload = build_retrieval_payload(
        example,
        config=RetrievalStrategyConfig(max_grammar_rules=4, max_few_shot_examples=2),
        comparison_examples=devset,
        semantic_lookup_multi_fn=fake_semantic_lookup,
        retrieve_all_fn=fake_retrieve_all,
    )

    assert payload["example_id"] == example["id"]
    assert payload["direction"] == "en_to_mir"
    assert payload["normalized_search_terms"][0] == "comparison-linker"
    assert payload["lexicon_pairs"] == [
        {"source": "house", "target": "tam", "match_type": "semantic"},
        {"source": "bigger", "target": "aga", "match_type": "semantic"},
        {"source": "my", "target": "ata", "match_type": "semantic"},
    ]
    assert payload["grammar_rules"] == [
        {"rule_id": "cmp.vyel", "passage": "Use vyel after comparative forms.", "source_section": "comparisons"},
        {"rule_id": "np.possessive", "passage": "Possessives add -a to pronouns.", "source_section": "noun_phrases"},
    ]
    assert payload["few_shot_examples"][0]["id"] == "s01-006-en-to-mir-possession-book"
    assert payload["warnings"] == []


def test_build_retrieval_payload_en_to_mir_falls_back_to_exact_lookup_on_semantic_error():
    devset = _load_devset()
    example = next(item for item in devset if item["id"] == "s01-004-en-to-mir-object-order")

    def fake_exact_lookup(*, english_word):
        return {"give": "buu", "me": "at", "that": "hua", "box": "nyem"}.get(english_word)

    payload = build_retrieval_payload(
        example,
        semantic_lookup_multi_fn=lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("chromadb unavailable")),
        exact_lookup_fn=fake_exact_lookup,
        retrieve_all_fn=lambda *_args, **_kwargs: {"grammar": []},
    )

    assert [item["match_type"] for item in payload["lexicon_pairs"]] == ["exact", "exact", "exact", "exact"]
    assert payload["lexicon_pairs"][0] == {"source": "give", "target": "buu", "match_type": "exact"}
    assert payload["warnings"] == [{"phase": "lexicon_semantic", "message": "chromadb unavailable"}]


def test_build_retrieval_payload_mir_to_en_uses_reverse_lookup_only():
    devset = _load_devset()
    example = next(item for item in devset if item["id"] == "s01-007-mir-to-en-locative-be-home")

    seen_words = []

    def fake_reverse_lookup(*, mirad_word):
        seen_words.append(mirad_word)
        return {"At": "I", "yexe": "work", "be": "at", "tam": "home"}.get(mirad_word)

    payload = build_retrieval_payload(
        example,
        reverse_lookup_fn=fake_reverse_lookup,
        retrieve_all_fn=lambda *_args, **_kwargs: {"grammar": []},
    )

    assert seen_words == ["At", "yexe", "be", "tam"]
    assert payload["lexicon_pairs"] == [
        {"source": "At", "target": "I", "match_type": "reverse_exact"},
        {"source": "yexe", "target": "work", "match_type": "reverse_exact"},
        {"source": "be", "target": "at", "match_type": "reverse_exact"},
        {"source": "tam", "target": "home", "match_type": "reverse_exact"},
    ]
    assert payload["warnings"] == []


def test_build_retrieval_payload_is_json_serializable_and_bounds_few_shot_examples():
    devset = _load_devset()
    example = next(item for item in devset if item["id"] == "s01-005-en-to-mir-subordinate-whether")

    payload = build_retrieval_payload(
        example,
        config=RetrievalStrategyConfig(max_few_shot_examples=1),
        comparison_examples=devset,
        semantic_lookup_multi_fn=lambda *_args, **_kwargs: {"know": "te", "whether": "ven"},
        retrieve_all_fn=lambda *_args, **_kwargs: {"grammar": []},
    )

    encoded = json.dumps(payload, sort_keys=True)
    assert '"few_shot_examples"' in encoded
    assert len(payload["few_shot_examples"]) == 1
    assert sorted(payload.keys()) == [
        "direction",
        "example_id",
        "few_shot_examples",
        "grammar_rules",
        "lexicon_pairs",
        "normalized_search_terms",
        "warnings",
    ]
