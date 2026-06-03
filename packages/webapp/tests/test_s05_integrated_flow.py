from __future__ import annotations

import json
import sys
import types
from base64 import b64encode
from pathlib import Path
from typing import Any

import itsdangerous
from fastapi.testclient import TestClient

from mirad_webapp.api import create_app
from mirad_webapp.config import Settings


APP_SOURCE = Path(__file__).parents[1] / "frontend" / "src" / "App.svelte"


def _write_phrase_csv(path: Path) -> Path:
    path.write_text(
        "english,mirad\n"
        "hello world,ha world\n"
        "good morning,gud morgen\n",
        encoding="utf-8",
    )
    return path


def _install_fake_mbrola(monkeypatch: Any, expected_texts: set[str] | None = None) -> None:
    module = types.ModuleType("mirad_tts.mbrola_backend")

    class MbrolaError(ValueError):
        pass

    class MbrolaNotFoundError(RuntimeError):
        pass

    class MbrolaVoiceNotFoundError(RuntimeError):
        pass

    class MbrolaSynthesisError(RuntimeError):
        pass

    def synthesize_to_wav(text: str, output_path: str | Path) -> Path:
        if expected_texts is not None:
            assert text in expected_texts
        output = Path(output_path)
        output.write_bytes(b"RIFF$\x00\x00\x00WAVEfmt fake-miralingo-wav")
        return output

    module.MbrolaError = MbrolaError
    module.MbrolaNotFoundError = MbrolaNotFoundError
    module.MbrolaVoiceNotFoundError = MbrolaVoiceNotFoundError
    module.MbrolaSynthesisError = MbrolaSynthesisError
    module.synthesize_to_wav = synthesize_to_wav
    monkeypatch.setitem(sys.modules, "mirad_tts.mbrola_backend", module)


def _app_with_deterministic_cards(monkeypatch: Any, tmp_path: Path):
    phrase_csv = _write_phrase_csv(tmp_path / "phrases.csv")

    def fake_lookup(english_word: str) -> str | None:
        return {"the": "te", "be": "bi"}.get(english_word)

    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", fake_lookup)
    _install_fake_mbrola(monkeypatch, {"ha world", "gud morgen", "te", "bi"})
    return create_app(Settings(session_secret="test-secret", phrase_csv_path=phrase_csv, database_path=tmp_path / "miralingo.sqlite3"))


def _signed_session_cookie(secret: str, payload: dict[str, Any]) -> str:
    data = b64encode(json.dumps(payload).encode("utf-8"))
    return itsdangerous.TimestampSigner(secret).sign(data).decode("utf-8")


def _login(client: TestClient) -> None:
    response = client.post("/auth/login", json={"username": "admin", "password": "admin"})
    assert response.status_code == 200
    payload = response.json()
    assert payload == {"authenticated": True, "user": {"username": "admin", "role": "admin"}}


def test_s05_authenticated_learning_flow_end_to_end(monkeypatch: Any, tmp_path: Path) -> None:
    client = TestClient(_app_with_deterministic_cards(monkeypatch, tmp_path))

    logged_out = client.get("/auth/current-user")
    assert logged_out.status_code == 401
    assert logged_out.json() == {
        "authenticated": False,
        "user": None,
        "detail": "No active user session.",
    }

    _login(client)

    current_user = client.get("/auth/current-user")
    assert current_user.status_code == 200
    assert current_user.json()["authenticated"] is True

    initial_queue = client.get("/practice/queue?limit=4")
    assert initial_queue.status_code == 200
    queue_payload = initial_queue.json()
    assert queue_payload["ok"] is True
    assert queue_payload["phase"] == "practice_queue"
    assert queue_payload["card_count"] == 4
    assert queue_payload["base_card_count"] == 4
    assert queue_payload["event_count"] == 0
    assert {card["type"] for card in queue_payload["cards"]} == {"phrase", "word"}
    assert len({card["base_card_id"] for card in queue_payload["cards"]}) == 4

    current_card = queue_payload["cards"][0]
    audio = client.get(f"/practice/audio/{current_card['audio_card_id']}")
    assert audio.status_code == 200
    assert audio.headers["content-type"].startswith("audio/wav")
    assert audio.headers["cache-control"] == "no-store"
    assert audio.headers["x-miralingo-audio-phase"] == "audio_synthesis"
    assert audio.headers["x-miralingo-audio-backend"] == "mbrola"
    assert audio.headers["x-miralingo-card-id"] == current_card["audio_card_id"]
    assert audio.content.startswith(b"RIFF")

    correct = client.post("/practice/answers", json={"card_id": current_card["id"], "answer": current_card["answer"]})
    incorrect = client.post("/practice/answers", json={"card_id": "word:the", "answer": "wrong"})
    assert correct.status_code == 200
    assert correct.json()["correct"] is True
    assert correct.json()["event_count"] == 1
    assert incorrect.status_code == 200
    assert incorrect.json()["correct"] is False
    assert incorrect.json()["event_count"] == 2

    reprioritized_queue = client.get("/practice/queue?limit=3")
    assert reprioritized_queue.status_code == 200
    reprioritized_payload = reprioritized_queue.json()
    assert reprioritized_payload["event_count"] == 2
    assert reprioritized_payload["cards"][0]["base_card_id"] == "word:the"
    assert reprioritized_payload["cards"][0]["scheduler_reason"] == "weak_recent_performance"

    progress = client.get("/practice/progress")
    assert progress.status_code == 200
    progress_payload = progress.json()
    assert progress_payload["ok"] is True
    assert progress_payload["phase"] == "practice_progress"
    assert progress_payload["event_count"] == 2
    assert progress_payload["total"] == 2
    assert progress_payload["correct"] == 1
    assert progress_payload["incorrect"] == 1
    assert progress_payload["accuracy"] == 0.5
    assert progress_payload["per_type"]["phrase"] == {"attempts": 1, "correct": 1, "incorrect": 0, "accuracy": 1.0}
    assert progress_payload["per_type"]["word"] == {"attempts": 1, "correct": 0, "incorrect": 1, "accuracy": 0.0}
    assert progress_payload["latest_event"]["card_id"] == "word:the#english-to-mirad"
    assert progress_payload["latest_event"]["direction"] == "english_to_mirad"
    assert progress_payload["latest_event"]["card_type"] == "word"
    assert progress_payload["latest_event"]["correct"] is False
    assert progress_payload["weak_count"] == 1
    assert progress_payload["mastered_count"] == 1
    assert progress_payload["stale_count"] == 0
    assert progress_payload["new_count"] == 6
    assert progress_payload["weak_cards"] == ["word:the#english-to-mirad"]
    assert progress_payload["mastered_cards"] == [current_card["id"]]
    per_card = {card["id"]: card for card in progress_payload["per_card"]}
    assert per_card["word:the#english-to-mirad"]["state"] == "weak"
    assert per_card[current_card["id"]]["state"] == "mastered"

    unknown_answer = client.post("/practice/answers", json={"card_id": "word:missing", "correct": False})
    assert unknown_answer.status_code == 404
    assert unknown_answer.json() == {
        "ok": False,
        "error": "unknown_card",
        "phase": "practice_answer",
        "card_id": "word:missing",
        "event_count": 2,
        "detail": "Practice card was not found in the configured content source.",
    }

    logout = client.post("/auth/logout")
    assert logout.status_code == 200
    assert logout.json() == {"authenticated": False}
    assert client.get("/auth/current-user").status_code == 401

    post_logout_progress = client.get("/practice/progress")
    post_logout_audio = client.get(f"/practice/audio/{current_card['audio_card_id']}")
    post_logout_queue = client.get("/practice/queue")
    post_logout_answer = client.post("/practice/answers", json={"card_id": current_card["id"], "correct": True})
    assert post_logout_progress.status_code == 401
    assert post_logout_progress.json()["error"] == "unauthenticated"
    assert post_logout_progress.json()["phase"] == "practice_progress"
    assert post_logout_audio.status_code == 401
    assert post_logout_audio.json()["error"] == "unauthenticated"
    assert post_logout_audio.json()["phase"] == "audio_synthesis"
    assert post_logout_queue.status_code == 401
    assert post_logout_queue.json()["phase"] == "practice_queue"
    assert post_logout_answer.status_code == 401
    assert post_logout_answer.json()["phase"] == "practice_answer"


def test_s05_progress_treats_corrupt_session_events_as_empty(monkeypatch: Any, tmp_path: Path) -> None:
    client = TestClient(_app_with_deterministic_cards(monkeypatch, tmp_path))
    client.cookies.set(
        "session",
        _signed_session_cookie(
            "test-secret",
            {"user": {"username": "admin", "role": "admin"}, "practice_events": {"not": "a-list"}},
        ),
    )

    response = client.get("/practice/progress")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["phase"] == "practice_progress"
    assert payload["event_count"] == 0
    assert payload["accuracy"] is None
    assert payload["latest_event"] is None


def test_s05_browser_visible_source_affordances_exist() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")

    for expected_label in [
        "MiraLingo",
        "Practice Mirad pronunciation and translation.",
        "Create account",
        "Log in",
        "Continue Practice",
        "Hear Mirad",
        "Analytics",
        "Vocabulary",
        "Settings",
        "Log Out",
        "Skip",
    ]:
        assert expected_label in source
