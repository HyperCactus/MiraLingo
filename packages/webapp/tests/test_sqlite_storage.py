from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from mirad_webapp.config import Settings, load_settings
from mirad_webapp.storage import MiraLingoStorage, StorageError


NOW = datetime(2026, 5, 24, 12, 0, tzinfo=timezone.utc)


def assert_no_secret_material(payload: object, *secrets: str) -> None:
    text = repr(payload)
    for secret in secrets:
        assert secret not in text
    assert "password_hash" not in text
    assert "salt" not in text


def test_settings_loads_database_path_from_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    database_path = tmp_path / "configured.sqlite3"
    monkeypatch.setenv("MIRALINGO_DATABASE_PATH", str(database_path))

    settings = load_settings()

    assert settings.database_path == database_path
    assert Settings().database_path == Path(".miralingo/miralingo.sqlite3")


def test_registration_duplicate_rejection_and_authentication_are_file_backed(tmp_path: Path) -> None:
    database_path = tmp_path / "nested" / "learners.sqlite3"
    first = MiraLingoStorage(database_path)
    password = "correct-password"

    user, error_payload, error_status = first.register_account(username=" Mira ", password=password)
    duplicate_user, duplicate_error, duplicate_status = first.register_account(
        username="MIRA",
        password="replacement-password",
    )

    assert user is not None
    assert user.public_dict()["id"] == "mira"
    assert user.public_dict()["email"] == "mira@legacy.local"
    assert user.public_dict()["role"] == "user"
    assert error_payload is None
    assert error_status is None
    assert duplicate_user is None
    assert duplicate_status == 409
    assert duplicate_error == {
        "authenticated": False,
        "error": "email_unavailable",
        "phase": "auth_register",
        "detail": "Email is already registered.",
    }
    assert_no_secret_material(user.public_dict(), password)
    assert_no_secret_material(duplicate_error, "replacement-password")

    second = MiraLingoStorage(database_path)
    authenticated = second.authenticate_account(username="MIRA", password=password)

    assert authenticated is not None
    assert authenticated.public_dict()["email"] == "mira@legacy.local"
    assert authenticated.public_dict()["role"] == "user"
    assert second.authenticate_account(username="mira", password="wrong-password") is None
    assert second.authenticate_account(username="   ", password=password) is None

    with sqlite3.connect(database_path) as connection:
        rows = connection.execute("SELECT username, role, password_hash FROM users").fetchall()

    assert len(rows) == 1
    stored_username, stored_role, stored_hash = rows[0]
    assert stored_username == "mira"
    assert stored_role == "user"
    assert isinstance(stored_hash, str)
    assert stored_hash.startswith("$2")
    assert password not in stored_hash


def test_registration_validation_keeps_existing_public_auth_shapes(tmp_path: Path) -> None:
    storage = MiraLingoStorage(tmp_path / "learners.sqlite3")

    blank_user, blank_error, blank_status = storage.register_account(username=" ", password="valid-pass")
    short_password_user, short_password_error, short_password_status = storage.register_account(
        username="mira",
        password="short",
    )
    admin_user, admin_error, admin_status = storage.register_account(
        username="admin",
        password="valid-password",
    )

    assert blank_user is None
    assert blank_status == 400
    assert blank_error == {
        "authenticated": False,
        "error": "invalid_email",
        "phase": "auth_register",
        "detail": "A valid email address is required.",
    }
    assert short_password_user is None
    assert short_password_status == 400
    assert short_password_error == {
        "authenticated": False,
        "error": "invalid_password",
        "phase": "auth_register",
        "detail": "Password must be at least 8 characters.",
    }
    assert admin_user is None
    assert admin_status == 400
    assert admin_error == {
        "authenticated": False,
        "error": "reserved_email",
        "phase": "auth_register",
        "detail": "The local admin email is reserved.",
    }


def test_shown_cards_and_answer_events_persist_across_storage_instances_with_bounds(tmp_path: Path) -> None:
    database_path = tmp_path / "practice.sqlite3"
    first = MiraLingoStorage(database_path)
    assert first.register_account(username="mira", password="correct-password")[0] is not None

    shown = first.record_card_shown(
        username="MIRA",
        card_id="word:the#english-to-mirad",
        base_card_id="word:the",
        direction="english_to_mirad",
        card_type="word",
        shown_at=NOW,
    )
    for index in range(3):
        first.append_answer_event(
            username="mira",
            card_id="word:the#english-to-mirad",
            base_card_id="word:the",
            direction="english_to_mirad",
            card_type="word",
            submitted_answer=f"answer-{index}",
            expected_answer="te",
            correct=index % 2 == 0,
            answered_at=NOW + timedelta(seconds=index),
        )

    second = MiraLingoStorage(database_path)
    shown_cards = second.list_shown_cards(username="mira")
    bounded_events = second.list_answer_events(username="mira", limit=2)

    assert shown_cards == [shown]
    assert [event.submitted_answer for event in bounded_events] == ["answer-1", "answer-2"]
    assert [event.correct for event in bounded_events] == [False, True]
    assert bounded_events[-1].public_dict() == {
        "username": "mira",
        "card_id": "word:the#english-to-mirad",
        "base_card_id": "word:the",
        "direction": "english_to_mirad",
        "card_type": "word",
        "submitted_answer": "answer-2",
        "expected_answer": "te",
        "correct": True,
        "answered_at": "2026-05-24T12:00:02+00:00",
    }
    assert bounded_events[-1].practice_event() == {
        "card_id": "word:the#english-to-mirad",
        "base_card_id": "word:the",
        "direction": "english_to_mirad",
        "card_type": "word",
        "submitted_answer": "answer-2",
        "expected_answer": "te",
        "correct": True,
        "answered_at": "2026-05-24T12:00:02+00:00",
    }


def test_list_methods_skip_malformed_rows_when_possible(tmp_path: Path) -> None:
    database_path = tmp_path / "practice.sqlite3"
    storage = MiraLingoStorage(database_path)
    assert storage.register_account(username="mira", password="correct-password")[0] is not None
    valid_event = storage.append_answer_event(
        username="mira",
        card_id="word:the#english-to-mirad",
        base_card_id="word:the",
        direction="english_to_mirad",
        card_type="word",
        submitted_answer="te",
        expected_answer="te",
        correct=True,
        answered_at=NOW,
    )
    valid_shown = storage.record_card_shown(
        username="mira",
        card_id="word:the#english-to-mirad",
        base_card_id="word:the",
        direction="english_to_mirad",
        card_type="word",
        shown_at=NOW,
    )

    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            INSERT INTO answer_events
                (username, card_id, base_card_id, direction, card_type,
                 submitted_answer, expected_answer, correct, answered_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("mira", "", "word:bad", "english_to_mirad", "word", "", "te", 1, NOW.isoformat()),
        )
        connection.execute(
            """
            INSERT INTO shown_cards
                (username, card_id, base_card_id, direction, card_type, shown_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("mira", "", "word:bad", "english_to_mirad", "word", NOW.isoformat()),
        )

    assert storage.list_answer_events(username="mira") == [valid_event]
    assert storage.list_shown_cards(username="mira") == [valid_shown]


def test_storage_errors_carry_stable_phase_payloads(tmp_path: Path) -> None:
    storage = MiraLingoStorage(tmp_path / "practice.sqlite3")

    with pytest.raises(StorageError) as exc_info:
        storage.record_card_shown(
            username=" ",
            card_id="word:the#english-to-mirad",
            base_card_id="word:the",
            direction="english_to_mirad",
            card_type="word",
        )

    assert exc_info.value.phase == "practice_queue"
    assert exc_info.value.public_payload() == {
        "ok": False,
        "error": "invalid_username",
        "phase": "practice_queue",
        "detail": "A non-blank username is required.",
    }


def test_storage_user_settings_default_update_and_delete_cascade(tmp_path: Path) -> None:
    database_path = tmp_path / "settings.sqlite3"
    storage = MiraLingoStorage(database_path)
    assert storage.register_account(username="mira", password="correct-password")[0] is not None
    assert storage.register_account(username="sara", password="correct-password")[0] is not None

    defaults = storage.get_user_settings(username="mira")
    updated = storage.upsert_user_settings(username="mira", theme="dark", tts_speed=0.9)
    storage.record_card_shown(
        username="mira",
        card_id="phrase:hello-world#english-to-mirad",
        base_card_id="phrase:hello-world",
        direction="english_to_mirad",
        card_type="phrase",
        shown_at=NOW,
    )
    storage.append_answer_event(
        username="mira",
        card_id="phrase:hello-world#english-to-mirad",
        base_card_id="phrase:hello-world",
        direction="english_to_mirad",
        card_type="phrase",
        submitted_answer="ha world",
        expected_answer="ha world",
        correct=True,
        answered_at=NOW,
    )
    storage.upsert_user_settings(username="sara", theme="light", tts_speed=1.0)

    assert defaults.public_dict() == {
        "theme": "system",
        "tts_speed": 0.8,
        "tts_autoplay": True,
        "sfx_enabled": True,
        "sfx_mode": "on_answer",
        "voice": {"id": "de6", "label": "Mirad de6", "provider": "mbrola", "mutable": False},
    }
    assert updated.public_dict()["theme"] == "dark"
    assert updated.public_dict()["tts_speed"] == 0.9
    assert storage.delete_user_account(username="mira") is True
    assert storage.delete_user_account(username="ghost") is False

    with sqlite3.connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM users WHERE username = 'mira'").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM user_settings WHERE username = 'mira'").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM shown_cards WHERE username = 'mira'").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM answer_events WHERE username = 'mira'").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM users WHERE username = 'sara'").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM user_settings WHERE username = 'sara'").fetchone()[0] == 1


def test_delete_user_account_rejects_local_admin(tmp_path: Path) -> None:
    storage = MiraLingoStorage(tmp_path / "settings.sqlite3")
    storage.ensure_session_user(username="admin", role="admin", phase="settings_get")

    with pytest.raises(StorageError) as exc_info:
        storage.delete_user_account(username="admin")

    assert exc_info.value.public_payload() == {
        "ok": False,
        "error": "protected_account",
        "phase": "account_delete",
        "detail": "The local admin account cannot be deleted.",
    }


def test_storage_init_error_uses_storage_init_phase(tmp_path: Path) -> None:
    database_directory = tmp_path / "directory.sqlite3"
    database_directory.mkdir()

    with pytest.raises(StorageError) as exc_info:
        MiraLingoStorage(database_directory)

    assert exc_info.value.phase == "storage_init"
    assert exc_info.value.public_payload()["phase"] == "storage_init"
