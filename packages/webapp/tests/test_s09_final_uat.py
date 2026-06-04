from __future__ import annotations

import sqlite3
import sys
import types
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from mirad_webapp.api import create_app
from mirad_webapp.config import Settings


LEARNER_USERNAME = "finaluat"
LEARNER_PASSWORD = "correct horse battery staple"


def _write_phrase_csv(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "english,mirad\n"
        "hello world,ha world\n"
        "good morning,gud morgen\n",
        encoding="utf-8",
    )
    return path


def _settings(tmp_path: Path, *, environment: str = "development", enable_local_admin: bool = True) -> Settings:
    return Settings(
        environment=environment,
        enable_local_admin=enable_local_admin,
        session_secret="s09-final-uat-secret",
        phrase_csv_path=_write_phrase_csv(tmp_path / "phrases.csv"),
        database_path=tmp_path / "miralingo.sqlite3",
    )


def _install_fake_mbrola(monkeypatch: Any, *, behavior: str = "success") -> None:
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
        output = Path(output_path)
        if behavior == "success":
            assert text in {"ha world", "gud morgen", "te", "bi"}
            output.write_bytes(b"RIFF$\x00\x00\x00WAVEfmt final-uat-wav")
            return output
        if behavior == "missing_binary":
            raise MbrolaNotFoundError("mbrola binary not found on PATH")
        raise AssertionError(f"unknown fake MBROLA behavior: {behavior}")

    module.MbrolaError = MbrolaError
    module.MbrolaNotFoundError = MbrolaNotFoundError
    module.MbrolaVoiceNotFoundError = MbrolaVoiceNotFoundError
    module.MbrolaSynthesisError = MbrolaSynthesisError
    module.synthesize_to_wav = synthesize_to_wav
    monkeypatch.setitem(sys.modules, "mirad_tts.mbrola_backend", module)


def _install_deterministic_content(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        "mirad_webapp.card_content._default_lexicon_lookup",
        lambda english_word: {"the": "te", "be": "bi"}.get(english_word),
    )


def _assert_no_secret_or_stacktrace(payload: dict[str, Any]) -> None:
    rendered = repr(payload)
    assert "Traceback" not in rendered
    assert LEARNER_PASSWORD not in rendered
    assert "password_hash" not in rendered
    assert "salt" not in rendered


def _sqlite_rows(database_path: Path, table: str) -> list[sqlite3.Row]:
    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        return connection.execute(f"SELECT * FROM {table} ORDER BY id").fetchall()


def test_s09_final_uat_registration_practice_audio_progress_and_sqlite(monkeypatch: Any, tmp_path: Path) -> None:
    _install_deterministic_content(monkeypatch)
    _install_fake_mbrola(monkeypatch, behavior="success")
    settings = _settings(tmp_path)
    client = TestClient(create_app(settings))

    unauthenticated_progress = client.get("/practice/progress")
    assert unauthenticated_progress.status_code == 401
    assert unauthenticated_progress.json() == {
        "ok": False,
        "error": "unauthenticated",
        "phase": "practice_progress",
        "detail": "Login is required to request practice progress.",
    }

    registration = client.post(
        "/auth/register",
        json={"username": LEARNER_USERNAME, "password": LEARNER_PASSWORD},
    )
    assert registration.status_code == 201
    assert registration.json() == {
        "authenticated": True,
        "user": {"username": LEARNER_USERNAME, "role": "learner"},
    }
    assert LEARNER_PASSWORD not in repr(registration.json())

    queue = client.get("/practice/queue?limit=6")
    assert queue.status_code == 200
    queue_payload = queue.json()
    assert queue_payload["ok"] is True
    assert queue_payload["phase"] == "practice_queue"
    assert queue_payload["card_count"] == 4
    assert queue_payload["base_card_count"] == 4
    assert queue_payload["event_count"] == 0
    assert {card["type"] for card in queue_payload["cards"]} == {"word", "phrase"}
    assert len({card["base_card_id"] for card in queue_payload["cards"]}) == 4
    assert {card["direction"] for card in queue_payload["cards"]}.issubset({"english_to_mirad", "mirad_to_english"})

    phrase_card = next(card for card in queue_payload["cards"] if card["type"] == "phrase")
    word_card = next(card for card in queue_payload["cards"] if card["type"] == "word")

    audio = client.get(f"/practice/audio/{phrase_card['audio_card_id']}")
    assert audio.status_code == 200
    assert audio.headers["content-type"].startswith("audio/wav")
    assert audio.headers["cache-control"] == "no-store"
    assert audio.headers["x-miralingo-audio-phase"] == "audio_synthesis"
    assert audio.headers["x-miralingo-audio-backend"] == "mbrola"
    assert audio.headers["x-miralingo-card-id"] == phrase_card["audio_card_id"]
    assert audio.content.startswith(b"RIFF")

    correct = client.post("/practice/answers", json={"card_id": phrase_card["id"], "answer": phrase_card["answer"]})
    incorrect = client.post("/practice/answers", json={"card_id": word_card["id"], "answer": "definitely wrong"})
    assert correct.status_code == 200
    assert correct.json()["phase"] == "practice_answer"
    assert correct.json()["correct"] is True
    assert correct.json()["event_count"] == 1
    assert incorrect.status_code == 200
    assert incorrect.json()["phase"] == "practice_answer"
    assert incorrect.json()["correct"] is False
    assert incorrect.json()["event_count"] == 2

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
    assert progress_payload["latest_event"]["card_id"] == word_card["id"]
    assert progress_payload["latest_event"]["base_card_id"] == word_card["base_card_id"]
    assert progress_payload["latest_event"]["direction"] == word_card["direction"]
    assert progress_payload["latest_event"]["card_type"] == "word"
    assert progress_payload["latest_event"]["correct"] is False
    assert progress_payload["weak_count"] == 1
    assert progress_payload["mastered_count"] == 0
    assert word_card["id"] in progress_payload["weak_cards"]
    assert phrase_card["id"] in progress_payload["new_cards"]

    shown_rows = _sqlite_rows(settings.database_path, "shown_cards")
    answer_rows = _sqlite_rows(settings.database_path, "answer_events")
    assert len(shown_rows) == 4
    assert len(answer_rows) == 2
    assert {row["username"] for row in shown_rows + answer_rows} == {LEARNER_USERNAME}
    assert {row["card_type"] for row in shown_rows} == {"word", "phrase"}
    shown_directions = {row["direction"] for row in shown_rows}
    assert shown_directions.issubset({"english_to_mirad", "mirad_to_english"})
    assert "english_to_mirad" in shown_directions
    assert [row["card_id"] for row in answer_rows] == [phrase_card["id"], word_card["id"]]
    assert [row["correct"] for row in answer_rows] == [1, 0]


def test_s09_final_uat_audio_unavailable_unknown_invalid_and_unauthenticated_are_structured(
    monkeypatch: Any, tmp_path: Path
) -> None:
    _install_deterministic_content(monkeypatch)
    _install_fake_mbrola(monkeypatch, behavior="missing_binary")
    settings = _settings(tmp_path)
    client = TestClient(create_app(settings))

    unauthenticated_audio = client.get("/practice/audio/phrase:hello-world")
    assert unauthenticated_audio.status_code == 401
    assert unauthenticated_audio.json()["phase"] == "audio_synthesis"
    assert unauthenticated_audio.json()["backend"] == "mbrola"
    _assert_no_secret_or_stacktrace(unauthenticated_audio.json())

    login = client.post("/auth/login", json={"username": "admin", "password": "admin"})
    assert login.status_code == 200

    unavailable = client.get("/practice/audio/phrase:hello-world")
    assert unavailable.status_code == 503
    unavailable_payload = unavailable.json()
    assert unavailable_payload["ok"] is False
    assert unavailable_payload["error"] == "mbrola_unavailable"
    assert unavailable_payload["phase"] == "audio_synthesis"
    assert unavailable_payload["backend"] == "mbrola"
    assert unavailable_payload["card_id"] == "phrase:hello-world"
    _assert_no_secret_or_stacktrace(unavailable_payload)

    unknown = client.get("/practice/audio/word:missing")
    assert unknown.status_code == 404
    assert unknown.json() == {
        "ok": False,
        "error": "unknown_card",
        "phase": "audio_synthesis",
        "backend": "mbrola",
        "card_id": "word:missing",
        "detail": "Practice card was not found in the configured content source.",
    }

    invalid = client.get("/practice/audio/phrase:..secret")
    assert invalid.status_code == 422
    invalid_payload = invalid.json()
    assert invalid_payload["error"] == "invalid_card_id"
    assert invalid_payload["phase"] == "audio_synthesis"
    assert invalid_payload["backend"] == "mbrola"
    _assert_no_secret_or_stacktrace(invalid_payload)


def test_s09_final_uat_source_and_auth_failures_are_diagnostic_without_credential_leakage(tmp_path: Path) -> None:
    production_client = TestClient(
        create_app(_settings(tmp_path / "prod", environment="production", enable_local_admin=False))
    )
    disabled_admin = production_client.post("/auth/login", json={"username": "admin", "password": "admin"})
    assert disabled_admin.status_code == 403
    assert disabled_admin.json() == {
        "authenticated": False,
        "error": "local_admin_disabled",
        "detail": "Local admin bootstrap is disabled for this environment.",
    }
    _assert_no_secret_or_stacktrace(disabled_admin.json())

    missing_csv = tmp_path / "missing.csv"
    source_client = TestClient(
        create_app(
            Settings(
                session_secret="s09-final-uat-source-secret",
                phrase_csv_path=missing_csv,
                database_path=tmp_path / "source" / "miralingo.sqlite3",
            )
        )
    )
    login = source_client.post("/auth/login", json={"username": "admin", "password": "admin"})
    assert login.status_code == 200

    queue = source_client.get("/practice/queue")
    assert queue.status_code == 404
    queue_payload = queue.json()
    assert queue_payload["ok"] is False
    assert queue_payload["error"] == "source_missing"
    assert queue_payload["phase"] == "phrase_import"
    assert queue_payload["source_type"] == "phrase_csv"
    assert queue_payload["source_path"] == str(missing_csv)
    assert queue_payload["practice_phase"] == "practice_queue"
    _assert_no_secret_or_stacktrace(queue_payload)

    audio = source_client.get("/practice/audio/phrase:hello-world")
    assert audio.status_code == 404
    audio_payload = audio.json()
    assert audio_payload["ok"] is False
    assert audio_payload["error"] == "source_missing"
    assert audio_payload["phase"] == "audio_synthesis"
    assert audio_payload["backend"] == "mbrola"
    assert audio_payload["card_id"] == "phrase:hello-world"
    assert audio_payload["source_type"] == "phrase_csv"
    assert audio_payload["source_path"] == str(missing_csv)
    _assert_no_secret_or_stacktrace(audio_payload)
