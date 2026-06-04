from __future__ import annotations

import sqlite3
import sys
import types
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from mirad_webapp.api import create_app
from mirad_webapp.config import Settings


LEARNER_USERNAME = "m005learner"
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


def _settings(tmp_path: Path, *, database_name: str = "miralingo.sqlite3") -> Settings:
    return Settings(
        session_secret="m005-final-learner-flow-secret",
        phrase_csv_path=_write_phrase_csv(tmp_path / "phrases.csv"),
        database_path=tmp_path / database_name,
    )


def _install_deterministic_content(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        "mirad_webapp.card_content._default_lexicon_lookup",
        lambda english_word: {"the": "te", "be": "bi"}.get(english_word),
    )


def _install_fake_mbrola(monkeypatch: Any, *, behavior: str) -> None:
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
            output.write_bytes(b"RIFF$\x00\x00\x00WAVEfmt m005-final-flow")
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


def _assert_no_secret_or_stacktrace(payload: dict[str, Any]) -> None:
    rendered = repr(payload)
    assert "Traceback" not in rendered
    assert LEARNER_PASSWORD not in rendered
    assert "password_hash" not in rendered
    assert "salt" not in rendered


def _rows_for_user(database_path: Path, table: str, *, username: str) -> list[sqlite3.Row]:
    order_by = {
        "shown_cards": "id",
        "answer_events": "id",
        "users": "username",
        "user_settings": "username",
    }[table]
    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        return connection.execute(
            f"SELECT * FROM {table} WHERE username = ? ORDER BY {order_by}",
            (username,),
        ).fetchall()


def test_m005_final_learner_flow_covers_auth_settings_modes_answers_audio_progress_and_account_deletion(
    monkeypatch: Any, tmp_path: Path
) -> None:
    _install_deterministic_content(monkeypatch)
    _install_fake_mbrola(monkeypatch, behavior="success")
    settings = _settings(tmp_path)
    client = TestClient(create_app(settings))

    unauthenticated_settings = client.get("/settings")
    unauthenticated_progress = client.get("/practice/progress")
    unauthenticated_current_user = client.get("/auth/current-user")

    assert unauthenticated_settings.status_code == 401
    assert unauthenticated_settings.json() == {
        "ok": False,
        "error": "unauthenticated",
        "phase": "settings_get",
        "detail": "Login is required to view settings.",
    }
    assert unauthenticated_progress.status_code == 401
    assert unauthenticated_progress.json() == {
        "ok": False,
        "error": "unauthenticated",
        "phase": "practice_progress",
        "detail": "Login is required to request practice progress.",
    }
    assert unauthenticated_current_user.status_code == 401
    assert unauthenticated_current_user.json() == {
        "authenticated": False,
        "user": None,
        "detail": "No active user session.",
    }
    _assert_no_secret_or_stacktrace(unauthenticated_settings.json())
    _assert_no_secret_or_stacktrace(unauthenticated_progress.json())
    _assert_no_secret_or_stacktrace(unauthenticated_current_user.json())

    registration = client.post(
        "/auth/register",
        json={"username": LEARNER_USERNAME, "password": LEARNER_PASSWORD},
    )
    assert registration.status_code == 201
    assert registration.json() == {
        "authenticated": True,
        "user": {"username": LEARNER_USERNAME, "role": "learner"},
    }
    _assert_no_secret_or_stacktrace(registration.json())

    current_user = client.get("/auth/current-user")
    assert current_user.status_code == 200
    assert current_user.json() == {
        "authenticated": True,
        "user": {"username": LEARNER_USERNAME, "role": "learner"},
    }

    default_settings = client.get("/settings")
    assert default_settings.status_code == 200
    assert default_settings.json() == {
        "ok": True,
        "phase": "settings_get",
        "settings": {
            "theme": "system",
            "tts_speed": 0.8,
            "tts_autoplay": True,
            "sfx_enabled": True,
            "sfx_mode": "all",
            "voice": {
                "id": "de6",
                "label": "Mirad de6",
                "provider": "mbrola",
                "mutable": False,
            },
        },
    }

    updated_settings = client.put("/settings", json={"theme": "dark", "tts_speed": 0.8})
    assert updated_settings.status_code == 200
    assert updated_settings.json() == {
        "ok": True,
        "phase": "settings_update",
        "settings": {
            "theme": "dark",
            "tts_speed": 0.8,
            "tts_autoplay": True,
            "sfx_enabled": True,
            "sfx_mode": "all",
            "voice": {
                "id": "de6",
                "label": "Mirad de6",
                "provider": "mbrola",
                "mutable": False,
            },
        },
    }

    recreated = TestClient(create_app(_settings(tmp_path)))
    relogin = recreated.post(
        "/auth/login",
        json={"username": LEARNER_USERNAME, "password": LEARNER_PASSWORD},
    )
    assert relogin.status_code == 200
    persisted_settings = recreated.get("/settings")
    assert persisted_settings.status_code == 200
    assert persisted_settings.json()["settings"] == {
        "theme": "dark",
        "tts_speed": 0.8,
        "tts_autoplay": True,
        "sfx_enabled": True,
        "sfx_mode": "all",
        "voice": {
            "id": "de6",
            "label": "Mirad de6",
            "provider": "mbrola",
            "mutable": False,
        },
    }

    mixed_queue = recreated.get("/practice/queue?mode=mixed&limit=6")
    assert mixed_queue.status_code == 200
    mixed_payload = mixed_queue.json()
    assert mixed_payload["ok"] is True
    assert mixed_payload["phase"] == "practice_queue"
    assert mixed_payload["mode"] == "mixed"
    assert mixed_payload["mode_detail"] == "default_mixed"
    assert mixed_payload["repeat_gap"] == 3
    assert mixed_payload["repeat_gap_satisfied"] is False
    assert mixed_payload["limit"] == 4
    assert mixed_payload["card_count"] == 4
    assert mixed_payload["base_card_count"] == 4
    assert mixed_payload["event_count"] == 0
    assert {card["type"] for card in mixed_payload["cards"]} == {"phrase", "word"}
    assert {card["direction"] for card in mixed_payload["cards"]} == {"english_to_mirad", "mirad_to_english"}

    phrase_card = next(
        card
        for card in mixed_payload["cards"]
        if card["type"] == "phrase"
    )
    word_card = next(
        card
        for card in mixed_payload["cards"]
        if card["type"] == "word"
    )

    revision_before_answers = recreated.get("/practice/queue?mode=revision&limit=10")
    assert revision_before_answers.status_code == 200
    assert revision_before_answers.json()["mode"] == "revision"
    assert revision_before_answers.json()["mode_detail"] == "empty_pool"
    assert revision_before_answers.json()["cards"] == []

    build_vocab_before_answers = recreated.get("/practice/queue?mode=build_vocabulary&limit=10")
    assert build_vocab_before_answers.status_code == 200
    build_vocab_before_payload = build_vocab_before_answers.json()
    assert build_vocab_before_payload["mode"] == "build_vocabulary"
    assert build_vocab_before_payload["mode_detail"] == "new_words_only"
    assert build_vocab_before_payload["event_count"] == 0
    assert {card["base_card_id"] for card in build_vocab_before_payload["cards"]} == {"word:the", "word:be"}
    assert all(card["type"] == "word" for card in build_vocab_before_payload["cards"])

    audio = recreated.get(f"/practice/audio/{phrase_card['audio_card_id']}")
    assert audio.status_code == 200
    assert audio.content.startswith(b"RIFF")
    assert audio.headers["content-type"].startswith("audio/wav")
    assert audio.headers["cache-control"] == "no-store"
    assert audio.headers["x-miralingo-audio-phase"] == "audio_synthesis"
    assert audio.headers["x-miralingo-audio-backend"] == "mbrola"
    assert audio.headers["x-miralingo-card-id"] == phrase_card["audio_card_id"]
    assert audio.headers["x-miralingo-tts-speed"] == "0.8"
    assert audio.headers["x-miralingo-voice-id"] == "de6"

    correct_answer = recreated.post(
        "/practice/answers",
        json={"card_id": phrase_card["id"], "answer": phrase_card["answer"]},
    )
    wrong_answer = recreated.post(
        "/practice/answers",
        json={"card_id": word_card["id"], "answer": "definitely wrong"},
    )

    assert correct_answer.status_code == 200
    assert correct_answer.json()["phase"] == "practice_answer"
    assert correct_answer.json()["correct"] is True
    assert correct_answer.json()["event_count"] == 1
    assert correct_answer.json()["latest_event"]["card_id"] == phrase_card["id"]
    assert correct_answer.json()["latest_event"]["correct"] is True

    assert wrong_answer.status_code == 200
    wrong_payload = wrong_answer.json()
    assert wrong_payload["phase"] == "practice_answer"
    assert wrong_payload["correct"] is False
    assert wrong_payload["event_count"] == 2
    assert wrong_payload["latest_event"]["card_id"] == word_card["id"]
    assert wrong_payload["latest_event"]["correct"] is False
    _assert_no_secret_or_stacktrace(wrong_payload)

    progress = recreated.get("/practice/progress")
    assert progress.status_code == 200
    progress_payload = progress.json()
    assert progress_payload["ok"] is True
    assert progress_payload["phase"] == "practice_progress"
    assert progress_payload["event_count"] == 2
    assert progress_payload["total"] == 2
    assert progress_payload["correct"] == 1
    assert progress_payload["incorrect"] == 1
    assert progress_payload["accuracy"] == 0.5
    assert progress_payload["per_type"]["phrase"] == {
        "attempts": 1,
        "correct": 1,
        "incorrect": 0,
        "accuracy": 1.0,
    }
    assert progress_payload["per_type"]["word"] == {
        "attempts": 1,
        "correct": 0,
        "incorrect": 1,
        "accuracy": 0.0,
    }
    assert progress_payload["latest_event"]["card_id"] == word_card["id"]
    assert progress_payload["latest_event"]["base_card_id"] == word_card["base_card_id"]
    assert progress_payload["latest_event"]["direction"] == word_card["direction"]
    assert progress_payload["latest_event"]["card_type"] == "word"
    assert progress_payload["latest_event"]["correct"] is False
    assert progress_payload["weak_count"] == 1
    assert progress_payload["mastered_count"] == 0
    assert progress_payload["weak_count"] + progress_payload["mastered_count"] + progress_payload["stale_count"] + progress_payload["new_count"] == progress_payload["card_count"]
    assert word_card["id"] in progress_payload["weak_cards"]
    assert phrase_card["id"] not in progress_payload["mastered_cards"]

    build_vocab_after_answers = recreated.get("/practice/queue?mode=build_vocabulary&limit=10")
    assert build_vocab_after_answers.status_code == 200
    build_vocab_after_payload = build_vocab_after_answers.json()
    assert build_vocab_after_payload["mode"] == "build_vocabulary"
    assert build_vocab_after_payload["event_count"] == 2
    assert {card["base_card_id"] for card in build_vocab_after_payload["cards"]} == ({"word:the", "word:be"} - {word_card["base_card_id"]})
    assert len(build_vocab_after_payload["cards"]) == 1

    revision_after_answers = recreated.get("/practice/queue?mode=revision&limit=10")
    assert revision_after_answers.status_code == 200
    assert revision_after_answers.json()["mode"] == "revision"
    assert revision_after_answers.json()["mode_detail"] == "seen_only"
    assert revision_after_answers.json()["event_count"] == 2
    assert revision_after_answers.json()["cards"]

    shown_rows_before_delete = _rows_for_user(settings.database_path, "shown_cards", username=LEARNER_USERNAME)
    answer_rows_before_delete = _rows_for_user(settings.database_path, "answer_events", username=LEARNER_USERNAME)
    settings_rows_before_delete = _rows_for_user(settings.database_path, "user_settings", username=LEARNER_USERNAME)
    user_rows_before_delete = _rows_for_user(settings.database_path, "users", username=LEARNER_USERNAME)

    assert len(shown_rows_before_delete) == 8
    assert len(answer_rows_before_delete) == 2
    assert len(settings_rows_before_delete) == 1
    assert len(user_rows_before_delete) == 1
    assert settings_rows_before_delete[0]["theme"] == "dark"
    assert settings_rows_before_delete[0]["tts_speed"] == 0.8
    assert settings_rows_before_delete[0]["tts_autoplay"] == 1
    assert {row["card_type"] for row in shown_rows_before_delete} == {"word", "phrase"}
    assert {row["direction"] for row in shown_rows_before_delete} == {"english_to_mirad", "mirad_to_english"}
    assert [row["card_id"] for row in answer_rows_before_delete] == [phrase_card["id"], word_card["id"]]
    assert [row["correct"] for row in answer_rows_before_delete] == [1, 0]

    bad_deletion = recreated.request(
        "DELETE",
        "/auth/account",
        json={"username": LEARNER_USERNAME, "confirmation": "KEEP"},
    )
    assert bad_deletion.status_code == 400
    assert bad_deletion.json() == {
        "ok": False,
        "error": "invalid_confirmation",
        "phase": "account_delete",
        "detail": "Account deletion requires the current username plus the exact confirmation phrase '<username> DELETE'.",
    }
    _assert_no_secret_or_stacktrace(bad_deletion.json())
    assert recreated.get("/auth/current-user").status_code == 200

    unavailable_client = TestClient(create_app(_settings(tmp_path, database_name="audio-unavailable.sqlite3")))
    unavailable_register = unavailable_client.post(
        "/auth/register",
        json={"username": LEARNER_USERNAME, "password": LEARNER_PASSWORD},
    )
    assert unavailable_register.status_code == 201
    _install_fake_mbrola(monkeypatch, behavior="missing_binary")

    unavailable_audio = unavailable_client.get(f"/practice/audio/{phrase_card['audio_card_id']}")
    assert unavailable_audio.status_code == 503
    unavailable_payload = unavailable_audio.json()
    assert unavailable_payload["ok"] is False
    assert unavailable_payload["error"] == "mbrola_unavailable"
    assert unavailable_payload["phase"] == "audio_synthesis"
    assert unavailable_payload["backend"] == "mbrola"
    assert unavailable_payload["card_id"] == phrase_card["audio_card_id"]
    assert unavailable_payload["detail"] == "MbrolaNotFoundError: mbrola binary not found on PATH"
    _assert_no_secret_or_stacktrace(unavailable_payload)

    deleted = recreated.request(
        "DELETE",
        "/auth/account",
        json={"username": LEARNER_USERNAME, "confirmation": f"{LEARNER_USERNAME} DELETE"},
    )
    assert deleted.status_code == 200
    assert deleted.json() == {
        "ok": True,
        "phase": "account_delete",
        "deleted_username": LEARNER_USERNAME,
        "authenticated": False,
    }

    current_user_after_delete = recreated.get("/auth/current-user")
    assert current_user_after_delete.status_code == 401
    assert current_user_after_delete.json() == {
        "authenticated": False,
        "user": None,
        "detail": "No active user session.",
    }

    relogin_after_delete = recreated.post(
        "/auth/login",
        json={"username": LEARNER_USERNAME, "password": LEARNER_PASSWORD},
    )
    assert relogin_after_delete.status_code == 401
    assert relogin_after_delete.json() == {
        "authenticated": False,
        "error": "invalid_credentials",
        "phase": "auth_login",
        "detail": "Invalid username or password.",
    }
    _assert_no_secret_or_stacktrace(relogin_after_delete.json())

    assert _rows_for_user(settings.database_path, "users", username=LEARNER_USERNAME) == []
    assert _rows_for_user(settings.database_path, "user_settings", username=LEARNER_USERNAME) == []
    assert _rows_for_user(settings.database_path, "shown_cards", username=LEARNER_USERNAME) == []
    assert _rows_for_user(settings.database_path, "answer_events", username=LEARNER_USERNAME) == []
