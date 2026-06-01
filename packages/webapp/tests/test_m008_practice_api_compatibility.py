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


def _app(tmp_path: Path):
    settings = Settings(
        session_secret="test-secret",
        database_path=tmp_path / "miralingo.sqlite3",
        phrase_csv_path=_write_phrase_csv(tmp_path / "phrases.csv"),
    )
    return create_app(settings)


def _login(client: TestClient) -> None:
    response = client.post("/auth/login", json={"username": "admin", "password": "admin"})
    assert response.status_code == 200


def test_session_control_requires_authentication(tmp_path: Path) -> None:
    client = TestClient(_app(tmp_path))

    response = client.get("/practice/sessions")

    assert response.status_code == 401
    assert response.json() == {
        "ok": False,
        "error": "unauthenticated",
        "phase": "practice_session",
        "detail": "Login is required to inspect practice sessions.",
    }


def test_session_inspect_is_idempotent_for_active_session(tmp_path: Path) -> None:
    app = _app(tmp_path)
    client = TestClient(app)
    _login(client)

    first = client.get("/practice/sessions")
    second = client.get("/practice/sessions")

    assert first.status_code == 200
    assert second.status_code == 200
    first_payload = first.json()
    second_payload = second.json()

    assert first_payload["ok"] is True
    assert first_payload["phase"] == "practice_session"
    assert second_payload["ok"] is True
    assert second_payload["phase"] == "practice_session"
    assert first_payload["active_session"]["session_id"] == second_payload["active_session"]["session_id"]
    assert first_payload["active_session"]["ended_at"] is None

    # Contract pin: no duplicate active rows for repeated inspect/continue style calls.
    with app.state.storage._connect("practice_session") as connection:  # pragma: no branch
        active_count = connection.execute(
            "SELECT COUNT(*) FROM practice_sessions WHERE username = ? AND ended_at IS NULL",
            ("admin",),
        ).fetchone()[0]
    assert active_count == 1


def test_queue_answer_aliases_progress_and_audio_contract_remain_compatible(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: {"the": "te", "be": "bi"}.get(english_word))
    app = _app(tmp_path)
    client = TestClient(app)
    _login(client)

    session_before = client.get("/practice/sessions")
    queue = client.get("/practice/queue?limit=1")

    assert session_before.status_code == 200
    assert queue.status_code == 200
    queue_payload = queue.json()
    assert queue_payload["ok"] is True
    assert queue_payload["phase"] == "practice_queue"
    assert queue_payload["cards"]

    card = queue_payload["cards"][0]
    for key in [
        "id",
        "base_card_id",
        "audio_card_id",
        "direction",
        "prompt",
        "answer",
        "scheduler_reason",
        "mastery",
        "recency",
    ]:
        assert key in card

    answer_payload = {"card_id": card["id"], "answer": card["answer"]}
    via_answers = client.post("/practice/answers", json=answer_payload)
    via_answer_alias = client.post("/practice/answer", json=answer_payload)

    assert via_answers.status_code == 200
    assert via_answer_alias.status_code == 200

    for response in (via_answers, via_answer_alias):
        payload = response.json()
        assert payload["ok"] is True
        assert payload["phase"] == "practice_answer"
        assert payload["card_id"] == card["id"]
        assert payload["base_card_id"] == card["base_card_id"]
        assert payload["direction"] == card["direction"]
        assert isinstance(payload["event_count"], int)
        assert "latest_event" in payload

    progress = client.get("/practice/progress")
    assert progress.status_code == 200
    progress_payload = progress.json()
    assert progress_payload["ok"] is True
    assert progress_payload["phase"] == "practice_progress"
    assert progress_payload["event_count"] >= 2
    assert "latest_event" in progress_payload

    # Audio contract pin: either binary WAV with compatibility headers, or deterministic JSON failure payload.
    audio = client.get(f"/practice/audio/{card['audio_card_id']}")
    if audio.status_code == 200:
        assert audio.headers.get("x-miralingo-audio-phase") == "audio_synthesis"
        assert audio.headers.get("x-miralingo-audio-backend") == "mbrola"
        assert audio.headers.get("x-miralingo-card-id") == card["audio_card_id"]
        assert audio.headers.get("content-type", "").startswith("audio/")
    else:
        assert audio.status_code in (400, 404, 422, 502, 503)
        payload = audio.json()
        assert payload["phase"] == "audio_synthesis"
        assert payload["backend"] == "mbrola"
        assert payload["card_id"] == card["audio_card_id"]
        assert "traceback" not in str(payload).lower()


def test_failed_answer_does_not_create_practice_lifecycle_row(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: None)
    app = _app(tmp_path)
    client = TestClient(app)
    _login(client)

    response = client.post("/practice/answers", json={"card_id": "word:missing", "correct": False})

    assert response.status_code == 404
    payload = response.json()
    assert payload["phase"] == "practice_answer"

    lifecycle = app.state.storage.get_practice_lifecycle(
        username="admin",
        base_card_id="word:missing",
        direction="english_to_mirad",
    )
    assert lifecycle["first_seen_at"] is None
    assert lifecycle["correct_streak"] == 0


def test_ending_active_session_then_answer_uses_new_active_session(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: {"the": "te", "be": "bi"}.get(english_word))
    app = _app(tmp_path)
    client = TestClient(app)
    _login(client)

    before = client.get("/practice/sessions")
    assert before.status_code == 200
    first_session_id = before.json()["active_session"]["session_id"]

    # Simulate lifecycle end semantics via storage boundary (API end route may be added later).
    with app.state.storage._connect("practice_session") as connection:
        connection.execute(
            "UPDATE practice_sessions SET ended_at = datetime('now') WHERE session_id = ?",
            (first_session_id,),
        )

    queued = client.get("/practice/queue?limit=1")
    assert queued.status_code == 200
    card = queued.json()["cards"][0]

    answered = client.post("/practice/answers", json={"card_id": card["id"], "answer": card["answer"]})
    assert answered.status_code == 200

    after = client.get("/practice/sessions")
    assert after.status_code == 200
    second_session_id = after.json()["active_session"]["session_id"]

    assert second_session_id != first_session_id

    with app.state.storage._connect("practice_session") as connection:
        active_count = connection.execute(
            "SELECT COUNT(*) FROM practice_sessions WHERE username = ? AND ended_at IS NULL",
            ("admin",),
        ).fetchone()[0]
    assert active_count == 1
