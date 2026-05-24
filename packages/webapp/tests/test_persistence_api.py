from __future__ import annotations

import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from mirad_webapp.api import create_app
from mirad_webapp.config import Settings
from mirad_webapp.storage import StorageError


def _write_phrase_csv(path: Path) -> Path:
    path.write_text(
        "english,mirad\n"
        "hello world,ha world\n"
        "good morning,gud morgen\n",
        encoding="utf-8",
    )
    return path


def _settings(tmp_path: Path, database_path: Path) -> Settings:
    return Settings(
        session_secret="test-secret",
        phrase_csv_path=_write_phrase_csv(tmp_path / "phrases.csv"),
        database_path=database_path,
    )


def _register(client: TestClient, username: str = "mira", password: str = "learner-password-1") -> None:
    response = client.post("/auth/register", json={"username": username, "password": password})
    assert response.status_code == 201


def _login(client: TestClient, username: str = "mira", password: str = "learner-password-1") -> None:
    response = client.post("/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200


def test_registered_learner_login_survives_app_recreation(tmp_path: Path) -> None:
    database_path = tmp_path / "miralingo.sqlite3"
    _register(TestClient(create_app(_settings(tmp_path, database_path))))

    recreated = TestClient(create_app(_settings(tmp_path, database_path)))
    login = recreated.post("/auth/login", json={"username": "MIRA", "password": "learner-password-1"})

    assert login.status_code == 200
    assert login.json() == {"authenticated": True, "user": {"username": "mira", "role": "learner"}}
    assert "learner-password-1" not in login.text


def test_queue_persists_shown_cards_with_direction_and_language_metadata(monkeypatch, tmp_path: Path) -> None:
    database_path = tmp_path / "miralingo.sqlite3"
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: {"the": "te"}.get(english_word))
    client = TestClient(create_app(_settings(tmp_path, database_path)))
    _register(client)

    queue = client.get("/practice/queue?limit=3")

    assert queue.status_code == 200
    payload = queue.json()
    assert payload["event_count"] == 0
    assert len(payload["cards"]) == 3
    with sqlite3.connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT username, card_id, base_card_id, direction, card_type,
                   prompt_language, answer_language
            FROM shown_cards
            ORDER BY id
            """
        ).fetchall()
    assert len(rows) == 3
    assert rows[0] == (
        "mira",
        "phrase:hello-world#english-to-mirad",
        "phrase:hello-world",
        "english_to_mirad",
        "phrase",
        "english",
        "mirad",
    )
    assert rows[1][3] == "mirad_to_english"
    assert rows[1][5:] == ("mirad", "english")


def test_answer_events_survive_restart_and_progress_reports_correctness(monkeypatch, tmp_path: Path) -> None:
    database_path = tmp_path / "miralingo.sqlite3"
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: {"the": "te"}.get(english_word))
    first = TestClient(create_app(_settings(tmp_path, database_path)))
    _register(first)

    answer = first.post("/practice/answers", json={"card_id": "word:the", "answer": " TE "})
    assert answer.status_code == 200
    assert answer.json()["correct"] is True
    assert first.post("/auth/logout").status_code == 200

    second = TestClient(create_app(_settings(tmp_path, database_path)))
    _login(second)
    progress = second.get("/practice/progress")

    assert progress.status_code == 200
    payload = progress.json()
    assert payload["event_count"] == 1
    assert payload["total"] == 1
    assert payload["correct"] == 1
    assert payload["incorrect"] == 0
    assert payload["accuracy"] == 1.0
    assert payload["latest_event"]["card_id"] == "word:the#english-to-mirad"
    with sqlite3.connect(database_path) as connection:
        rows = connection.execute(
            "SELECT submitted_answer, expected_answer, correct FROM answer_events"
        ).fetchall()
    assert rows == [("TE", "te", 1)]


def test_unknown_card_answer_does_not_append_answer_event(monkeypatch, tmp_path: Path) -> None:
    database_path = tmp_path / "miralingo.sqlite3"
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: None)
    client = TestClient(create_app(_settings(tmp_path, database_path)))
    _register(client)

    response = client.post("/practice/answers", json={"card_id": "word:missing", "correct": False})

    assert response.status_code == 404
    assert response.json() == {
        "ok": False,
        "error": "unknown_card",
        "phase": "practice_answer",
        "card_id": "word:missing",
        "event_count": 0,
        "detail": "Practice card was not found in the configured content source.",
    }
    with sqlite3.connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM answer_events").fetchone()[0] == 0


def test_unauthenticated_practice_requests_keep_phase_diagnostics(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path, tmp_path / "miralingo.sqlite3")))

    queue = client.get("/practice/queue")
    answer = client.post("/practice/answers", json={"card_id": "phrase:hello-world", "correct": True})
    progress = client.get("/practice/progress")

    assert queue.status_code == 401
    assert queue.json()["phase"] == "practice_queue"
    assert answer.status_code == 401
    assert answer.json()["phase"] == "practice_answer"
    assert progress.status_code == 401
    assert progress.json()["phase"] == "practice_progress"


def test_auth_storage_failure_returns_stable_phase_without_password_echo(tmp_path: Path) -> None:
    app = create_app(_settings(tmp_path, tmp_path / "miralingo.sqlite3"))
    secret = "learner-password-1"

    def fail_register(*, username: str, password: str):
        raise StorageError(phase="auth_register", detail="Could not register account in storage.")

    app.state.storage.register_account = fail_register
    response = TestClient(app).post("/auth/register", json={"username": "mira", "password": secret})

    assert response.status_code == 503
    assert response.json() == {
        "ok": False,
        "error": "storage_error",
        "phase": "auth_register",
        "detail": "Could not register account in storage.",
    }
    assert secret not in response.text


def test_queue_storage_failure_does_not_claim_shown_card_persistence(monkeypatch, tmp_path: Path) -> None:
    database_path = tmp_path / "miralingo.sqlite3"
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: {"the": "te"}.get(english_word))
    app = create_app(_settings(tmp_path, database_path))
    client = TestClient(app)
    _register(client)

    def fail_record(*, username: str, cards: list[dict]):
        raise StorageError(phase="practice_queue", detail="Could not record shown cards.")

    app.state.storage.record_cards_shown = fail_record
    response = client.get("/practice/queue?limit=1")

    assert response.status_code == 503
    assert response.json() == {
        "ok": False,
        "error": "storage_error",
        "phase": "practice_queue",
        "detail": "Could not record shown cards.",
    }
    with sqlite3.connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM shown_cards").fetchone()[0] == 0


def test_answer_storage_failure_does_not_append_cookie_or_database_event(monkeypatch, tmp_path: Path) -> None:
    database_path = tmp_path / "miralingo.sqlite3"
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: {"the": "te"}.get(english_word))
    app = create_app(_settings(tmp_path, database_path))
    client = TestClient(app)
    _register(client)

    def fail_append(**kwargs):
        raise StorageError(phase="practice_answer", detail="Could not record answer event.")

    app.state.storage.append_answer_event = fail_append
    response = client.post("/practice/answers", json={"card_id": "word:the", "answer": "te"})

    assert response.status_code == 503
    assert response.json() == {
        "ok": False,
        "error": "storage_error",
        "phase": "practice_answer",
        "detail": "Could not record answer event.",
    }
    with sqlite3.connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM answer_events").fetchone()[0] == 0
