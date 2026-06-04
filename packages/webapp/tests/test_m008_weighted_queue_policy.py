from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from mirad_webapp.api import create_app
from mirad_webapp.config import Settings
from mirad_webapp.practice_engine import build_practice_queue


NOW = datetime(2026, 5, 24, 12, 0, tzinfo=timezone.utc)


def _cards() -> list[dict[str, str]]:
    return [
        {"id": "phrase:greeting", "type": "phrase", "english": "good day", "mirad": "gud dey"},
        {"id": "phrase:thanks", "type": "phrase", "english": "thank you", "mirad": "sye"},
        {"id": "word:alpha", "type": "word", "english": "alpha", "mirad": "alfa"},
        {"id": "word:bravo", "type": "word", "english": "bravo", "mirad": "brava"},
    ]


def _event(
    card_id: str,
    *,
    correct: bool,
    answered_at: datetime,
    base_card_id: str | None = None,
    direction: str | None = None,
    card_type: str = "word",
) -> dict[str, object]:
    resolved_direction = direction or card_id.rsplit("#", maxsplit=1)[1].replace("-", "_")
    resolved_base = base_card_id or card_id.split("#", maxsplit=1)[0]
    return {
        "card_id": card_id,
        "base_card_id": resolved_base,
        "direction": resolved_direction,
        "card_type": card_type,
        "submitted_answer": "x",
        "expected_answer": "x",
        "correct": correct,
        "answered_at": answered_at.isoformat(),
    }


def test_weighted_queue_reports_ratio_mix_weight_and_repeat_gap_diagnostics_contract() -> None:
    queue = build_practice_queue(cards=_cards(), events=[], now=NOW, limit=6, mode="mixed")

    # S02 contract: queue must expose requested/actual policy diagnostics.
    assert "diagnostics" in queue
    diagnostics = queue["diagnostics"]
    assert diagnostics["requested_active_revision_ratio"] == {"active": 0.7, "revision": 0.3}
    assert diagnostics["actual_active_revision_ratio"]["active"] + diagnostics["actual_active_revision_ratio"]["revision"] == 1.0
    assert diagnostics["requested_word_phrase_mix"] == {"word": 0.5, "phrase": 0.5}
    assert diagnostics["actual_word_phrase_mix"]["word"] + diagnostics["actual_word_phrase_mix"]["phrase"] == 1.0
    assert "weighting_inputs" in diagnostics
    assert set(diagnostics["weighting_inputs"].keys()) >= {"exposure_weight", "recent_performance_weight"}
    assert set(diagnostics.keys()) >= {"repeat_gap", "repeat_gap_satisfied", "fallback_reasons"}


def test_weighted_queue_prefers_lower_exposure_and_weak_recent_performance_in_diagnostics() -> None:
    cards = _cards()
    events = [
        _event("word:alpha#english-to-mirad", correct=True, answered_at=NOW - timedelta(minutes=20)),
        _event("word:alpha#english-to-mirad", correct=True, answered_at=NOW - timedelta(minutes=19)),
        _event("word:alpha#english-to-mirad", correct=True, answered_at=NOW - timedelta(minutes=18)),
        _event("word:bravo#english-to-mirad", correct=False, answered_at=NOW - timedelta(minutes=2)),
    ]

    queue = build_practice_queue(cards=cards, events=events, now=NOW, limit=4, mode="mixed")

    assert "diagnostics" in queue
    per_card = queue["diagnostics"]["per_card_weights"]
    assert per_card["word:bravo#english-to-mirad"]["recent_performance_factor"] > per_card["word:alpha#english-to-mirad"]["recent_performance_factor"]
    assert per_card["word:bravo#english-to-mirad"]["exposure_factor"] > per_card["word:alpha#english-to-mirad"]["exposure_factor"]


def test_weighted_queue_small_pool_reports_drift_and_repeat_gap_relaxation_reasons() -> None:
    small_cards = [
        {"id": "word:one", "type": "word", "english": "one", "mirad": "un"},
        {"id": "word:two", "type": "word", "english": "two", "mirad": "du"},
    ]

    queue = build_practice_queue(cards=small_cards, events=[], now=NOW, limit=4, mode="mixed")

    assert "diagnostics" in queue
    assert queue["diagnostics"]["repeat_gap_relaxed"] is True
    assert "small_pool" in queue["diagnostics"]["fallback_reasons"]
    assert "ratio_drift" in queue["diagnostics"]["fallback_reasons"]
    assert "mix_drift" in queue["diagnostics"]["fallback_reasons"]


def _write_phrase_csv(path: Path) -> Path:
    path.write_text("english,mirad\ngood day,gud dey\nthank you,sye\n", encoding="utf-8")
    return path


def _app(tmp_path: Path):
    return create_app(
        Settings(
            session_secret="test-secret",
            database_path=tmp_path / "miralingo.sqlite3",
            phrase_csv_path=_write_phrase_csv(tmp_path / "phrases.csv"),
        )
    )


def _login(client: TestClient) -> None:
    assert client.post("/auth/login", json={"username": "admin", "password": "admin"}).status_code == 200


def test_practice_queue_api_returns_weighted_policy_diagnostics_with_compatible_payload(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: {"alpha": "alfa", "bravo": "brava"}.get(english_word))
    app = _app(tmp_path)
    client = TestClient(app)
    _login(client)

    app.state.storage.ensure_session_user(username="admin", role="admin", phase="practice_session")
    session_one = app.state.storage.start_practice_session(username="admin")
    for _ in range(2):
        app.state.storage.record_practice_lifecycle_answer(
            username="admin",
            session_id=session_one["session_id"],
            base_card_id="word:alpha",
            direction="english_to_mirad",
            correct=True,
        )
    session_two = app.state.storage.start_practice_session(username="admin")
    for _ in range(2):
        app.state.storage.record_practice_lifecycle_answer(
            username="admin",
            session_id=session_two["session_id"],
            base_card_id="word:alpha",
            direction="english_to_mirad",
            correct=True,
        )

    response = client.get("/practice/queue?limit=6&mode=mixed")

    assert response.status_code == 200
    payload = response.json()
    # Backward-compatible envelope still present.
    assert payload["ok"] is True
    assert payload["phase"] == "practice_queue"
    assert isinstance(payload["cards"], list)

    # S02 diagnostics contract.
    assert "diagnostics" in payload
    diagnostics = payload["diagnostics"]
    assert set(diagnostics.keys()) >= {
        "requested_active_revision_ratio",
        "actual_active_revision_ratio",
        "requested_word_phrase_mix",
        "actual_word_phrase_mix",
        "weighting_inputs",
        "lifecycle_counts",
        "exposure_by_item",
        "repeat_gap_relaxed",
        "fallback_reasons",
    }
    assert diagnostics["lifecycle_counts"]["active"] >= 1
    assert isinstance(diagnostics["exposure_by_item"], dict)
