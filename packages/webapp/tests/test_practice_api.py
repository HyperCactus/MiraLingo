from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from mirad_webapp.api import create_app
from mirad_webapp.config import Settings
from mirad_webapp.storage import StorageError


NOW = datetime(2026, 5, 24, 12, 0, tzinfo=timezone.utc)
STALE_AT = NOW - timedelta(days=15)


def _write_phrase_csv(path: Path) -> Path:
    path.write_text(
        "english,mirad\n"
        "hello world,ha world\n"
        "good morning,gud morgen\n",
        encoding="utf-8",
    )
    return path


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        session_secret="test-secret",
        database_path=tmp_path / "miralingo.sqlite3",
        phrase_csv_path=_write_phrase_csv(tmp_path / "phrases.csv"),
    )


def _app(tmp_path: Path):
    return create_app(_settings(tmp_path))


def _login(client: TestClient) -> None:
    response = client.post("/auth/login", json={"username": "admin", "password": "admin"})
    assert response.status_code == 200


def test_practice_queue_requires_authenticated_session(tmp_path: Path) -> None:
    client = TestClient(_app(tmp_path))

    response = client.get("/practice/queue?mode=revision")

    assert response.status_code == 401
    assert response.json() == {
        "ok": False,
        "error": "unauthenticated",
        "phase": "practice_queue",
        "detail": "Login is required to request a practice queue.",
    }


def test_authenticated_practice_queue_returns_cards_and_scheduler_diagnostics(monkeypatch, tmp_path: Path) -> None:
    def fake_lookup(english_word: str) -> str | None:
        return {"the": "te", "be": "bi"}.get(english_word)

    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", fake_lookup)
    client = TestClient(_app(tmp_path))
    _login(client)

    response = client.get("/practice/queue?limit=3")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["phase"] == "practice_queue"
    assert payload["mode"] == "mixed"
    assert payload["mode_detail"] == "default_mixed"
    assert payload["repeat_gap"] == 10
    assert payload["repeat_gap_satisfied"] is False
    assert payload["card_count"] == 8
    assert payload["base_card_count"] == 4
    assert payload["event_count"] == 0
    assert payload["limit"] == 3
    assert [card["scheduler_reason"] for card in payload["cards"]] == ["new_item", "new_item", "new_item"]
    assert payload["cards"][0] == {
        "id": "phrase:hello-world#english-to-mirad",
        "base_card_id": "phrase:hello-world",
        "audio_card_id": "phrase:hello-world",
        "type": "phrase",
        "direction": "english_to_mirad",
        "prompt_language": "english",
        "answer_language": "mirad",
        "prompt": "hello world",
        "answer": "ha world",
        "english_text": "hello world",
        "mirad_text": "ha world",
        "scheduler_reason": "new_item",
        "mastery": {"attempts": 0, "correct": 0, "incorrect": 0, "accuracy": None},
        "recency": {"last_seen_at": None, "age_seconds": None},
    }
    assert len({card["base_card_id"] for card in payload["cards"]}) == 3
    assert all(card["direction"] == "english_to_mirad" for card in payload["cards"])


def test_practice_queue_revision_mode_returns_only_stale_items(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: {"the": "te", "be": "bi"}.get(english_word))
    app = _app(tmp_path)
    client = TestClient(app)
    _login(client)

    app.state.storage.ensure_session_user(username="admin", role="admin", phase="practice_answer")
    app.state.storage.append_answer_event(
        username="admin",
        card_id="word:the#english-to-mirad",
        base_card_id="word:the",
        direction="english_to_mirad",
        card_type="word",
        submitted_answer="te",
        expected_answer="te",
        correct=True,
        answered_at=STALE_AT,
    )
    app.state.storage.append_answer_event(
        username="admin",
        card_id="word:the#mirad-to-english",
        base_card_id="word:the",
        direction="mirad_to_english",
        card_type="word",
        submitted_answer="the",
        expected_answer="the",
        correct=True,
        answered_at=STALE_AT,
    )
    app.state.storage.append_answer_event(
        username="admin",
        card_id="word:be#english-to-mirad",
        base_card_id="word:be",
        direction="english_to_mirad",
        card_type="word",
        submitted_answer="bi",
        expected_answer="bi",
        correct=True,
        answered_at=NOW,
    )

    response = client.get("/practice/queue?mode=revision&limit=10")

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "revision"
    assert payload["mode_detail"] == "stale_only"
    assert payload["event_count"] == 3
    assert [card["id"] for card in payload["cards"]] == [
        "word:the#english-to-mirad",
        "word:the#mirad-to-english",
    ]
    assert all(card["scheduler_reason"] == "stale_mastered_review" for card in payload["cards"])
    assert payload["repeat_gap"] == 10
    assert payload["repeat_gap_satisfied"] is False


def test_practice_queue_build_vocabulary_mode_returns_only_new_word_base_cards(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: {"the": "te", "be": "bi"}.get(english_word))
    app = _app(tmp_path)
    client = TestClient(app)
    _login(client)

    answered = client.post("/practice/answers", json={"card_id": "word:the", "correct": False})
    assert answered.status_code == 200

    response = client.get("/practice/queue?mode=build_vocabulary&limit=10")

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "build_vocabulary"
    assert payload["mode_detail"] == "new_words_only"
    assert payload["event_count"] == 1
    assert {card["base_card_id"] for card in payload["cards"]} == {"word:be"}
    assert [card["id"] for card in payload["cards"]] == [
        "word:be#english-to-mirad",
        "word:be#mirad-to-english",
    ]
    assert all(card["type"] == "word" for card in payload["cards"])
    assert all(card["scheduler_reason"] == "new_item" for card in payload["cards"])
    assert payload["repeat_gap"] == 10
    assert payload["repeat_gap_satisfied"] is False


def test_practice_answer_persists_event_in_signed_session_and_prioritizes_weak_card(monkeypatch, tmp_path: Path) -> None:
    def fake_lookup(english_word: str) -> str | None:
        return {"the": "te", "be": "bi"}.get(english_word)

    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", fake_lookup)
    client = TestClient(_app(tmp_path))
    _login(client)

    submit = client.post("/practice/answers", json={"card_id": "word:the", "correct": False})
    queue = client.get("/practice/queue?limit=2")

    assert submit.status_code == 200
    submit_payload = submit.json()
    assert submit_payload["ok"] is True
    assert submit_payload["phase"] == "practice_answer"
    assert submit_payload["card_id"] == "word:the#english-to-mirad"
    assert submit_payload["base_card_id"] == "word:the"
    assert submit_payload["direction"] == "english_to_mirad"
    assert submit_payload["card_type"] == "word"
    assert submit_payload["correct"] is False
    assert submit_payload["event_count"] == 1
    assert submit_payload["scheduler_reason"] == "weak_recent_performance"
    assert submit_payload["mastery"] == {"attempts": 1, "correct": 0, "incorrect": 1, "accuracy": 0.0}
    assert submit_payload["latest_event"]["card_id"] == "word:the#english-to-mirad"
    assert submit_payload["latest_event"]["direction"] == "english_to_mirad"
    assert submit_payload["latest_event"]["correct"] is False

    assert queue.status_code == 200
    assert queue.json()["event_count"] == 1
    assert queue.json()["cards"][0]["id"] == "word:the#english-to-mirad"
    assert queue.json()["cards"][0]["scheduler_reason"] == "weak_recent_performance"


def test_practice_answer_requires_authenticated_session(tmp_path: Path) -> None:
    client = TestClient(_app(tmp_path))

    response = client.post("/practice/answers", json={"card_id": "phrase:hello-world", "correct": True})

    assert response.status_code == 401
    assert response.json() == {
        "ok": False,
        "error": "unauthenticated",
        "phase": "practice_answer",
        "detail": "Login is required to submit a practice answer.",
    }


def test_practice_answer_unknown_card_returns_404_without_appending_event(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: None)
    client = TestClient(_app(tmp_path))
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


def test_practice_answer_typed_submission_infers_correctness_and_persists_answers(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: {"the": "te", "be": "bi"}.get(english_word))
    app = _app(tmp_path)
    client = TestClient(app)
    _login(client)

    response = client.post(
        "/practice/answers",
        json={"card_id": "word:the#english-to-mirad", "answer": "  te  "},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["phase"] == "practice_answer"
    assert payload["card_id"] == "word:the#english-to-mirad"
    assert payload["base_card_id"] == "word:the"
    assert payload["direction"] == "english_to_mirad"
    assert payload["card_type"] == "word"
    assert payload["correct"] is True
    assert payload["event_count"] == 1
    assert payload["latest_event"] == {
        "card_id": "word:the#english-to-mirad",
        "base_card_id": "word:the",
        "direction": "english_to_mirad",
        "card_type": "word",
        "correct": True,
        "answered_at": payload["latest_event"]["answered_at"],
    }

    events = app.state.storage.list_answer_events(username="admin", phase="practice_answer")
    assert len(events) == 1
    assert events[0].submitted_answer == "te"
    assert events[0].expected_answer == "te"
    assert events[0].correct is True


def test_practice_answer_accepts_comma_separated_expected_answers(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: {"the": "te, tay", "be": "bi"}.get(english_word))
    app = _app(tmp_path)
    client = TestClient(app)
    _login(client)

    response = client.post(
        "/practice/answers",
        json={"card_id": "word:the#english-to-mirad", "answer": "  TAY  "},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["correct"] is True

    events = app.state.storage.list_answer_events(username="admin", phase="practice_answer")
    assert len(events) == 1
    assert events[0].submitted_answer == "TAY"
    assert events[0].expected_answer == "te, tay"
    assert events[0].correct is True


def test_practice_answer_typed_submission_records_wrong_answer_without_correct_flag(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: {"the": "te", "be": "bi"}.get(english_word))
    app = _app(tmp_path)
    client = TestClient(app)
    _login(client)

    response = client.post(
        "/practice/answers",
        json={"card_id": "word:the#english-to-mirad", "answer": "wrong answer"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["phase"] == "practice_answer"
    assert payload["correct"] is False
    assert payload["scheduler_reason"] == "weak_recent_performance"
    assert payload["latest_event"]["card_id"] == "word:the#english-to-mirad"
    assert payload["latest_event"]["correct"] is False

    events = app.state.storage.list_answer_events(username="admin", phase="practice_answer")
    assert len(events) == 1
    assert events[0].submitted_answer == "wrong answer"
    assert events[0].expected_answer == "te"
    assert events[0].correct is False


def test_practice_answer_invalid_payload_returns_structured_practice_validation(tmp_path: Path) -> None:
    client = TestClient(_app(tmp_path))
    _login(client)

    response = client.post("/practice/answers", json={"answer": "te"})

    assert response.status_code == 422
    assert response.json() == {
        "ok": False,
        "error": "invalid_practice_payload",
        "phase": "practice_validation",
        "detail": "Practice request payload or query parameters failed validation.",
    }


def test_practice_answer_storage_failure_returns_structured_practice_answer_payload(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: {"the": "te", "be": "bi"}.get(english_word))
    app = _app(tmp_path)
    client = TestClient(app)
    _login(client)

    def fail_append(**_kwargs):
        raise StorageError(phase="practice_answer", detail="Could not append practice answer.")

    app.state.storage.append_answer_event = fail_append
    response = client.post(
        "/practice/answers",
        json={"card_id": "word:the#english-to-mirad", "answer": "te"},
    )

    assert response.status_code == 503
    assert response.json() == {
        "ok": False,
        "error": "storage_error",
        "phase": "practice_answer",
        "detail": "Could not append practice answer.",
    }


def test_practice_invalid_limit_returns_practice_validation_payload(tmp_path: Path) -> None:
    client = TestClient(_app(tmp_path))
    _login(client)

    response = client.get("/practice/queue?limit=0")

    assert response.status_code == 422
    assert response.json() == {
        "ok": False,
        "error": "invalid_practice_payload",
        "phase": "practice_validation",
        "detail": "Practice request payload or query parameters failed validation.",
    }


def test_practice_invalid_mode_returns_practice_validation_and_does_not_record_cards(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: {"the": "te", "be": "bi"}.get(english_word))
    app = _app(tmp_path)
    client = TestClient(app)
    _login(client)

    called = False

    def fail_if_called(*, username: str, cards: list[dict]):
        nonlocal called
        called = True
        raise AssertionError("record_cards_shown should not be called for invalid mode")

    app.state.storage.record_cards_shown = fail_if_called
    response = client.get("/practice/queue?mode=surprise")

    assert response.status_code == 422
    assert response.json() == {
        "ok": False,
        "error": "invalid_practice_payload",
        "phase": "practice_validation",
        "detail": "Practice request payload or query parameters failed validation.",
    }
    assert called is False
    with sqlite3.connect(tmp_path / "miralingo.sqlite3") as connection:
        assert connection.execute("SELECT COUNT(*) FROM shown_cards").fetchone()[0] == 0


def test_practice_queue_missing_content_source_returns_structured_payload(tmp_path: Path) -> None:
    missing_csv = tmp_path / "missing.csv"
    app = create_app(Settings(session_secret="test-secret", database_path=tmp_path / "miralingo.sqlite3", phrase_csv_path=missing_csv))
    client = TestClient(app)
    _login(client)

    response = client.get("/practice/queue?mode=mixed")

    assert response.status_code == 404
    payload = response.json()
    assert payload["ok"] is False
    assert payload["error"] == "source_missing"
    assert payload["phase"] == "phrase_import"
    assert payload["source_type"] == "phrase_csv"
    assert payload["source_path"] == str(missing_csv)
    assert payload["practice_phase"] == "practice_queue"


def test_practice_queue_storage_failure_does_not_claim_persistence(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: {"the": "te", "be": "bi"}.get(english_word))
    app = _app(tmp_path)
    client = TestClient(app)
    _login(client)

    def fail_record(*, username: str, cards: list[dict]):
        raise StorageError(phase="practice_queue", detail="Could not record shown cards.")

    app.state.storage.record_cards_shown = fail_record
    response = client.get("/practice/queue?mode=mixed&limit=1")

    assert response.status_code == 503
    assert response.json() == {
        "ok": False,
        "error": "storage_error",
        "phase": "practice_queue",
        "detail": "Could not record shown cards.",
    }
    with sqlite3.connect(tmp_path / "miralingo.sqlite3") as connection:
        assert connection.execute("SELECT COUNT(*) FROM shown_cards").fetchone()[0] == 0
