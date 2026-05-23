from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from mirad_webapp.api import create_app
from mirad_webapp.config import Settings


def _write_phrase_csv(path: Path) -> Path:
    path.write_text(
        "english,mirad\n"
        "hello world,ha world\n"
        "good morning,gud morgen\n",
        encoding="utf-8",
    )
    return path


def _login(client: TestClient) -> None:
    response = client.post("/auth/login", json={"username": "admin", "password": "admin"})
    assert response.status_code == 200


def test_practice_queue_requires_authenticated_session(tmp_path: Path) -> None:
    app = create_app(Settings(session_secret="test-secret", phrase_csv_path=_write_phrase_csv(tmp_path / "phrases.csv")))
    client = TestClient(app)

    response = client.get("/practice/queue")

    assert response.status_code == 401
    assert response.json() == {
        "ok": False,
        "error": "unauthenticated",
        "phase": "practice_queue",
        "detail": "Login is required to request a practice queue.",
    }


def test_authenticated_practice_queue_returns_cards_and_scheduler_diagnostics(monkeypatch, tmp_path: Path) -> None:
    phrase_csv = _write_phrase_csv(tmp_path / "phrases.csv")

    def fake_lookup(english_word: str) -> str | None:
        return {"the": "te", "be": "bi"}.get(english_word)

    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", fake_lookup)
    app = create_app(Settings(session_secret="test-secret", phrase_csv_path=phrase_csv))
    client = TestClient(app)
    _login(client)

    response = client.get("/practice/queue?limit=3")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["phase"] == "practice_queue"
    assert payload["card_count"] == 4
    assert payload["event_count"] == 0
    assert payload["limit"] == 3
    assert [card["scheduler_reason"] for card in payload["cards"]] == ["new_item", "new_item", "new_item"]
    assert payload["cards"][0] == {
        "id": "phrase:hello-world",
        "type": "phrase",
        "prompt": "hello world",
        "answer": "ha world",
        "scheduler_reason": "new_item",
        "mastery": {"attempts": 0, "correct": 0, "incorrect": 0, "accuracy": None},
        "recency": {"last_seen_at": None, "age_seconds": None},
    }


def test_practice_answer_persists_event_in_signed_session_and_prioritizes_weak_card(monkeypatch, tmp_path: Path) -> None:
    phrase_csv = _write_phrase_csv(tmp_path / "phrases.csv")

    def fake_lookup(english_word: str) -> str | None:
        return {"the": "te", "be": "bi"}.get(english_word)

    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", fake_lookup)
    app = create_app(Settings(session_secret="test-secret", phrase_csv_path=phrase_csv))
    client = TestClient(app)
    _login(client)

    submit = client.post("/practice/answers", json={"card_id": "word:the", "correct": False})
    queue = client.get("/practice/queue?limit=2")

    assert submit.status_code == 200
    submit_payload = submit.json()
    assert submit_payload["ok"] is True
    assert submit_payload["phase"] == "practice_answer"
    assert submit_payload["card_id"] == "word:the"
    assert submit_payload["card_type"] == "word"
    assert submit_payload["correct"] is False
    assert submit_payload["event_count"] == 1
    assert submit_payload["scheduler_reason"] == "weak_recent_performance"
    assert submit_payload["mastery"] == {"attempts": 1, "correct": 0, "incorrect": 1, "accuracy": 0.0}
    assert submit_payload["latest_event"]["card_id"] == "word:the"
    assert submit_payload["latest_event"]["correct"] is False

    assert queue.status_code == 200
    assert queue.json()["event_count"] == 1
    assert queue.json()["cards"][0]["id"] == "word:the"
    assert queue.json()["cards"][0]["scheduler_reason"] == "weak_recent_performance"


def test_practice_answer_requires_authenticated_session(tmp_path: Path) -> None:
    app = create_app(Settings(session_secret="test-secret", phrase_csv_path=_write_phrase_csv(tmp_path / "phrases.csv")))
    client = TestClient(app)

    response = client.post("/practice/answers", json={"card_id": "phrase:hello-world", "correct": True})

    assert response.status_code == 401
    assert response.json() == {
        "ok": False,
        "error": "unauthenticated",
        "phase": "practice_answer",
        "detail": "Login is required to submit a practice answer.",
    }


def test_practice_answer_unknown_card_returns_404_without_appending_event(monkeypatch, tmp_path: Path) -> None:
    phrase_csv = _write_phrase_csv(tmp_path / "phrases.csv")
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: None)
    app = create_app(Settings(session_secret="test-secret", phrase_csv_path=phrase_csv))
    client = TestClient(app)
    _login(client)

    response = client.post("/practice/answers", json={"card_id": "word:missing", "correct": False})
    queue = client.get("/practice/queue")

    assert response.status_code == 404
    assert response.json() == {
        "ok": False,
        "error": "unknown_card",
        "phase": "practice_answer",
        "card_id": "word:missing",
        "event_count": 0,
        "detail": "Practice card was not found in the configured content source.",
    }
    assert queue.status_code == 200
    assert queue.json()["event_count"] == 0


def test_practice_invalid_limit_returns_practice_validation_payload(tmp_path: Path) -> None:
    app = create_app(Settings(session_secret="test-secret", phrase_csv_path=_write_phrase_csv(tmp_path / "phrases.csv")))
    client = TestClient(app)
    _login(client)

    response = client.get("/practice/queue?limit=0")

    assert response.status_code == 422
    assert response.json() == {
        "ok": False,
        "error": "invalid_practice_payload",
        "phase": "practice_validation",
        "detail": "Practice request payload or query parameters failed validation.",
    }


def test_practice_queue_missing_content_source_returns_structured_payload(tmp_path: Path) -> None:
    missing_csv = tmp_path / "missing.csv"
    app = create_app(Settings(session_secret="test-secret", phrase_csv_path=missing_csv))
    client = TestClient(app)
    _login(client)

    response = client.get("/practice/queue")

    assert response.status_code == 404
    payload = response.json()
    assert payload["ok"] is False
    assert payload["error"] == "source_missing"
    assert payload["phase"] == "phrase_import"
    assert payload["source_type"] == "phrase_csv"
    assert payload["source_path"] == str(missing_csv)
    assert payload["practice_phase"] == "practice_queue"
