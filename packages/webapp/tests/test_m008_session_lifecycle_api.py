from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from mirad_webapp.api import create_app
from mirad_webapp.config import Settings
from mirad_webapp.storage import StorageError


def _write_phrase_csv(path: Path) -> Path:
    path.write_text("english,mirad\nhello world,ha world\n", encoding="utf-8")
    return path


def _app(tmp_path: Path):
    settings = Settings(
        session_secret="test-secret",
        database_path=tmp_path / "miralingo.sqlite3",
        phrase_csv_path=_write_phrase_csv(tmp_path / "phrases.csv"),
    )
    return create_app(settings)


def _login(client: TestClient) -> None:
    assert client.post("/auth/login", json={"username": "admin", "password": "admin"}).status_code == 200


def test_practice_sessions_requires_authentication(tmp_path: Path) -> None:
    client = TestClient(_app(tmp_path))
    response = client.get("/practice/sessions")
    assert response.status_code == 401
    assert response.json()["phase"] == "practice_session"


def test_answers_promote_after_five_correct_across_sessions(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: None)
    app = _app(tmp_path)
    client = TestClient(app)
    _login(client)

    for _ in range(2):
        first = client.post("/practice/answers", json={"card_id": "phrase:hello-world#english-to-mirad", "answer": "ha world"})
        assert first.status_code == 200

    state = app.state.storage.get_practice_lifecycle(username="admin", base_card_id="phrase:hello-world", direction="english_to_mirad")
    assert state["lifecycle"] == "active"
    assert state["correct_streak"] == 2

    app.state.storage.start_practice_session(username="admin")
    for _ in range(3):
        second = client.post("/practice/answers", json={"card_id": "phrase:hello-world#english-to-mirad", "answer": "ha world"})
        assert second.status_code == 200

    promoted = app.state.storage.get_practice_lifecycle(username="admin", base_card_id="phrase:hello-world", direction="english_to_mirad")
    assert promoted["lifecycle"] == "revision"
    assert promoted["session_streak"] >= 2


def test_unknown_card_does_not_create_lifecycle(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: None)
    app = _app(tmp_path)
    client = TestClient(app)
    _login(client)

    response = client.post("/practice/answers", json={"card_id": "word:missing", "correct": False})
    assert response.status_code == 404

    lifecycle = app.state.storage.get_practice_lifecycle(username="admin", base_card_id="word:missing", direction="english_to_mirad")
    assert lifecycle["first_seen_at"] is None
    assert lifecycle["correct_streak"] == 0


def test_practice_answer_lifecycle_storage_failure_returns_storage_payload(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: None)
    app = _app(tmp_path)
    client = TestClient(app)
    _login(client)

    def fail(**_kwargs):
        raise StorageError(phase="practice_lifecycle", detail="Could not record practice lifecycle answer.")

    app.state.storage.record_practice_lifecycle_answer = fail
    response = client.post("/practice/answers", json={"card_id": "phrase:hello-world#english-to-mirad", "answer": "ha world"})
    assert response.status_code == 503
    assert response.json()["phase"] == "practice_lifecycle"
