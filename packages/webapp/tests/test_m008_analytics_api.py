from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from mirad_webapp.api import create_app
from mirad_webapp.config import Settings
from mirad_webapp.practice import MAX_EVENTS


NOW = datetime(2026, 5, 24, 12, 0, tzinfo=timezone.utc)


def _write_phrase_csv(path: Path) -> Path:
    path.write_text(
        "english,mirad\n"
        "hello world,ha world\n"
        "good morning,gud morgen\n",
        encoding="utf-8",
    )
    return path


def _app_with_cards(monkeypatch, tmp_path: Path):
    phrase_csv = _write_phrase_csv(tmp_path / "phrases.csv")

    def fake_lookup(english_word: str) -> str | None:
        return {"the": "te", "be": "bi"}.get(english_word)

    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", fake_lookup)
    return create_app(Settings(session_secret="test-secret", database_path=tmp_path / "miralingo.sqlite3", phrase_csv_path=phrase_csv))


def _login(client: TestClient) -> None:
    response = client.post("/auth/login", json={"username": "admin", "password": "admin"})
    assert response.status_code == 200


def _seed_answer(
    app,
    *,
    username: str,
    session_id: str,
    base_card_id: str,
    direction: str,
    card_type: str,
    correct: bool,
    answered_at: datetime,
) -> None:
    card_id = f"{base_card_id}#{direction.replace('_', '-')}"
    app.state.storage.record_practice_lifecycle_answer(
        username=username,
        session_id=session_id,
        base_card_id=base_card_id,
        direction=direction,
        card_id=card_id,
        card_type=card_type,
        submitted_answer="ok" if correct else "wrong",
        expected_answer="ok",
        correct=correct,
        answered_at=answered_at,
    )


def test_practice_analytics_requires_authenticated_session(monkeypatch, tmp_path: Path) -> None:
    client = TestClient(_app_with_cards(monkeypatch, tmp_path))

    response = client.get("/practice/analytics")

    assert response.status_code == 401
    assert response.json() == {
        "ok": False,
        "error": "unauthenticated",
        "phase": "practice_analytics",
        "detail": "Login is required to request practice analytics.",
    }


def test_practice_analytics_starts_sparse_for_new_learner(monkeypatch, tmp_path: Path) -> None:
    client = TestClient(_app_with_cards(monkeypatch, tmp_path))
    _login(client)

    response = client.get("/practice/analytics")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["phase"] == "practice_analytics"
    assert payload["event_count"] == 0
    assert payload["accuracy"] is None
    assert payload["session_count"] == 0
    assert payload["lifecycle_count"] == 0
    assert payload["sparse_history"] == {
        "is_sparse": True,
        "events": 0,
        "sessions": 0,
        "lifecycles": 0,
        "reason": "new_learner",
    }


def test_practice_analytics_reports_sessions_timing_streaks_and_breakdowns(monkeypatch, tmp_path: Path) -> None:
    app = _app_with_cards(monkeypatch, tmp_path)
    client = TestClient(app)
    _login(client)

    storage = app.state.storage
    storage.ensure_session_user(username="admin", role="local_admin", phase="practice_analytics")

    first = storage.start_practice_session(username="admin", started_at=NOW - timedelta(days=2))
    second = storage.start_practice_session(username="admin", started_at=NOW - timedelta(days=1))

    _seed_answer(
        app,
        username="admin",
        session_id=first["session_id"],
        base_card_id="word:the",
        direction="english_to_mirad",
        card_type="word",
        correct=True,
        answered_at=NOW - timedelta(days=2, minutes=20),
    )
    _seed_answer(
        app,
        username="admin",
        session_id=first["session_id"],
        base_card_id="phrase:hello-world",
        direction="mirad_to_english",
        card_type="phrase",
        correct=False,
        answered_at=NOW - timedelta(days=2, minutes=10),
    )
    _seed_answer(
        app,
        username="admin",
        session_id=second["session_id"],
        base_card_id="phrase:good-morning",
        direction="english_to_mirad",
        card_type="phrase",
        correct=True,
        answered_at=NOW - timedelta(days=1, minutes=5),
    )

    storage.end_active_practice_session(username="admin", ended_at=NOW - timedelta(days=1, minutes=1))

    response = client.get("/practice/analytics?window_days=30&include_cards=true")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["phase"] == "practice_analytics"
    assert payload["event_count"] == 3
    assert payload["session_count"] == 2
    assert payload["lifecycle_count"] >= 2
    assert payload["active_deck_count"] == min(10, payload["active_count"])
    assert payload["timing"]["first_answered_at"] is not None
    assert payload["timing"]["last_answered_at"] is not None
    assert payload["streak"]["current_days"] >= 0
    assert "direction_breakdown" in payload
    assert "card_type_breakdown" in payload
    assert payload["direction_breakdown"]["english_to_mirad"]["attempts"] == 2
    assert payload["card_type_breakdown"]["phrase"]["attempts"] == 2
    assert payload["per_card"]


def test_practice_progress_compact_contract_remains_compatible(monkeypatch, tmp_path: Path) -> None:
    app = _app_with_cards(monkeypatch, tmp_path)
    client = TestClient(app)
    _login(client)

    answer = client.post("/practice/answers", json={"card_id": "phrase:hello-world", "correct": True})
    assert answer.status_code == 200

    analytics = client.get("/practice/analytics")
    assert analytics.status_code == 200

    progress = client.get("/practice/progress")
    assert progress.status_code == 200
    payload = progress.json()
    assert payload["ok"] is True
    assert payload["phase"] == "practice_progress"
    assert payload["event_count"] >= 1
    assert "per_type" in payload
    assert "latest_event" in payload


def test_practice_summary_is_fast_compact_and_reports_streak(monkeypatch, tmp_path: Path) -> None:
    app = _app_with_cards(monkeypatch, tmp_path)
    client = TestClient(app)
    _login(client)

    storage = app.state.storage
    storage.ensure_session_user(username="admin", role="local_admin", phase="practice_summary")
    session = storage.start_practice_session(username="admin", started_at=NOW - timedelta(days=1))
    _seed_answer(
        app,
        username="admin",
        session_id=session["session_id"],
        base_card_id="phrase:hello-world",
        direction="english_to_mirad",
        card_type="phrase",
        correct=True,
        answered_at=NOW - timedelta(days=1),
    )
    _seed_answer(
        app,
        username="admin",
        session_id=session["session_id"],
        base_card_id="phrase:good-morning",
        direction="mirad_to_english",
        card_type="phrase",
        correct=False,
        answered_at=NOW,
    )

    response = client.get("/practice/summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["phase"] == "practice_summary"
    assert payload["event_count"] == 2
    assert payload["correct"] == 1
    assert payload["accuracy"] == 0.5
    assert payload["streak"]["best_days"] >= 2
    assert payload["active_deck_count"] == min(10, payload["active_count"])
    assert "per_card" not in payload


def test_practice_analytics_missing_content_source_returns_structured_payload(tmp_path: Path) -> None:
    missing_csv = tmp_path / "missing.csv"
    app = create_app(Settings(session_secret="test-secret", database_path=tmp_path / "miralingo.sqlite3", phrase_csv_path=missing_csv))
    client = TestClient(app)
    _login(client)

    response = client.get("/practice/analytics")

    assert response.status_code == 404
    payload = response.json()
    assert payload["ok"] is False
    assert payload["error"] == "source_missing"
    assert payload["phase"] == "phrase_import"
    assert payload["source_type"] == "phrase_csv"
    assert payload["source_path"] == str(missing_csv)
    assert payload["practice_phase"] == "practice_analytics"


def test_practice_analytics_invalid_filters_and_malformed_events_are_safe(monkeypatch, tmp_path: Path) -> None:
    app = _app_with_cards(monkeypatch, tmp_path)
    client = TestClient(app)
    _login(client)

    storage = app.state.storage
    storage.ensure_session_user(username="admin", role="local_admin", phase="practice_analytics")
    session = storage.start_practice_session(username="admin", started_at=NOW)

    with storage._connect("practice_analytics") as connection:
        connection.execute(
            """
            INSERT INTO answer_events
                (username, card_id, base_card_id, direction, card_type, submitted_answer, expected_answer, correct, answered_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("admin", "word:the#english-to-mirad", "word:the", "english_to_mirad", "word", "te", "te", 1, "not-a-date"),
        )

    invalid = client.get("/practice/analytics?window_days=-7")
    assert invalid.status_code == 422
    assert invalid.json()["phase"] == "practice_validation"

    before = len(storage.list_answer_events(username="admin", phase="practice_analytics"))
    valid = client.get("/practice/analytics?window_days=7")
    assert valid.status_code == 200
    after = len(storage.list_answer_events(username="admin", phase="practice_analytics"))
    assert before == after

    payload = valid.json()
    assert payload["event_count"] <= MAX_EVENTS
