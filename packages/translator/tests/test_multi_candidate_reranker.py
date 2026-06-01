from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mirad_translator.multi_candidate import _rerank_verified_candidates


def test_reranker_prefers_semantic_fidelity_and_hard_fail_filtering():
    candidates = [
        {"index": 0, "candidate_id": "cand-1", "mirad_text": "wrong but fluent", "temperature": 0.1},
        {"index": 1, "candidate_id": "cand-2", "mirad_text": "better semantics", "temperature": 0.4},
        {"index": 2, "candidate_id": "cand-3", "mirad_text": "best grammar but wrong negation", "temperature": 0.8},
    ]
    verifier_payload = {
        "winner_id": "cand-2",
        "ranking": ["cand-2", "cand-1", "cand-3"],
        "winner_explanation": "cand-2 preserves meaning and polarity best.",
        "candidates": [
            {
                "candidate_id": "cand-1",
                "semantic_fidelity": 0.45,
                "morphology_tense_negation": 0.9,
                "grammar_style": 0.95,
                "hard_failures": ["semantic_mismatch"],
                "soft_errors": [],
                "justification": "Fluent but wrong meaning.",
            },
            {
                "candidate_id": "cand-2",
                "semantic_fidelity": 0.92,
                "morphology_tense_negation": 0.84,
                "grammar_style": 0.7,
                "hard_failures": [],
                "soft_errors": ["slightly_awkward_style"],
                "justification": "Best semantic match.",
            },
            {
                "candidate_id": "cand-3",
                "semantic_fidelity": 0.6,
                "morphology_tense_negation": 0.2,
                "grammar_style": 0.98,
                "hard_failures": ["wrong_negation"],
                "soft_errors": [],
                "justification": "Grammar good, polarity wrong.",
            },
        ],
    }

    winner_index, winner_score, rationale, ranked = _rerank_verified_candidates(
        candidates,
        verifier_payload,
        direction="en_to_mir",
        source_text="I do not like that but I will go.",
    )

    assert winner_index == 1
    assert ranked[winner_index]["candidate_id"] == "cand-2"
    assert ranked[winner_index]["winner"] is True
    assert ranked[winner_index]["rank"] == 0
    assert all("rule_precheck" in c for c in ranked)
    assert winner_score > ranked[2]["judge"]["total_score"]
    assert "meaning" in rationale.lower() or "semantic" in rationale.lower()
