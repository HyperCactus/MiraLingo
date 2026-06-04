from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from mirad_webapp.api import create_app
from mirad_webapp.config import Settings


FRONTEND_APP = Path(__file__).parents[1] / "frontend" / "src" / "App.svelte"


def _write_phrase_csv(path: Path) -> Path:
    path.write_text(
        "english,mirad\n"
        "hello world,ha world\n"
        "good morning,gud morgen\n",
        encoding="utf-8",
    )
    return path


def test_s03_logged_in_user_can_request_queue_submit_answer_and_see_adaptation(monkeypatch, tmp_path: Path) -> None:
    phrase_csv = _write_phrase_csv(tmp_path / "phrases.csv")

    def fake_lookup(english_word: str) -> str | None:
        return {"the": "te", "be": "bi"}.get(english_word)

    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", fake_lookup)
    client = TestClient(
        create_app(
            Settings(
                environment="development",
                enable_local_admin=True,
                phrase_csv_path=phrase_csv,
                database_path=tmp_path / "miralingo.sqlite3",
            )
        )
    )

    login = client.post("/auth/login", json={"username": "admin", "password": "admin"})
    first_queue = client.get("/practice/queue?limit=3")
    submit = client.post("/practice/answer", json={"card_id": "word:the", "answer": "wrong"})
    adapted_queue = client.get("/practice/queue?limit=3")

    assert login.status_code == 200
    assert first_queue.status_code == 200
    assert first_queue.json()["ok"] is True
    assert first_queue.json()["phase"] == "practice_queue"
    assert first_queue.json()["event_count"] == 0
    assert {card["type"] for card in first_queue.json()["cards"]} == {"phrase", "word"}

    assert submit.status_code == 200
    assert submit.json()["ok"] is True
    assert submit.json()["phase"] == "practice_answer"
    assert submit.json()["correct"] is False
    assert submit.json()["event_count"] == 1

    assert adapted_queue.status_code == 200
    assert adapted_queue.json()["event_count"] == 1
    assert adapted_queue.json()["cards"][0]["base_card_id"] == "word:the"
    assert adapted_queue.json()["cards"][0]["scheduler_reason"] == "weak_recent_performance"


def test_s03_negative_paths_are_structured_and_do_not_expose_credentials(monkeypatch, tmp_path: Path) -> None:
    phrase_csv = _write_phrase_csv(tmp_path / "phrases.csv")
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: {"the": "te"}.get(english_word))
    client = TestClient(
        create_app(
            Settings(
                environment="development",
                enable_local_admin=True,
                phrase_csv_path=phrase_csv,
                database_path=tmp_path / "miralingo.sqlite3",
            )
        )
    )

    unauth_queue = client.get("/practice/queue")
    unauth_submit = client.post("/practice/answer", json={"card_id": "phrase:hello-world", "answer": "ha world"})
    client.post("/auth/login", json={"username": "admin", "password": "admin"})
    unknown = client.post("/practice/answer", json={"card_id": "phrase:nope", "answer": "x"})

    assert unauth_queue.status_code == 401
    assert unauth_queue.json()["error"] == "unauthenticated"
    assert unauth_queue.json()["phase"] == "practice_queue"
    assert "admin" not in unauth_queue.text
    assert "password" not in unauth_queue.text

    assert unauth_submit.status_code == 401
    assert unauth_submit.json()["error"] == "unauthenticated"
    assert unauth_submit.json()["phase"] == "practice_answer"
    assert "password" not in unauth_submit.text

    assert unknown.status_code == 404
    assert unknown.json() == {
        "ok": False,
        "error": "unknown_card",
        "phase": "practice_answer",
        "card_id": "phrase:nope",
        "event_count": 0,
        "detail": "Practice card was not found in the configured content source.",
    }


def test_s03_frontend_source_contains_current_practice_fetch_and_submit_affordances() -> None:
    frontend_source = FRONTEND_APP.read_text(encoding="utf-8")

    assert 'import { getPracticeQueue, submitPracticeAnswer } from "./lib/api/practice";' in frontend_source
    assert 'await getPracticeQueue(mode, mode === "revision" ? 30 : mode === "build_vocabulary" ? 12 : 8);' in frontend_source
    assert 'await submitPracticeAnswer(body);' in frontend_source
    assert 'ExerciseCard' in frontend_source
    assert 'on:submit={submitAnswer}' in frontend_source
    assert 'on:reveal={submitGiveUp}' in frontend_source
    assert 'playFeedbackSound' in frontend_source
    assert '/assets/sound_effects/correct_answer.wav' in frontend_source
    assert '/assets/sound_effects/incorrect_answer.wav' in frontend_source
