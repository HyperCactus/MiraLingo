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
    assert user.public_dict() == {"username": "mira", "role": "learner"}
    assert error_payload is None
    assert error_status is None
    assert duplicate_user is None
    assert duplicate_status == 409
    assert duplicate_error == {
        "authenticated": False,
        "error": "username_unavailable",
        "phase": "auth_register",
        "detail": "Username is already registered.",
    }
    assert_no_secret_material(user.public_dict(), password)
    assert_no_secret_material(duplicate_error, "replacement-password")

    second = MiraLingoStorage(database_path)
    authenticated = second.authenticate_account(username="MIRA", password=password)

    assert authenticated is not None
    assert authenticated.public_dict() == {"username": "mira", "role": "learner"}
    assert second.authenticate_account(username="mira", password="wrong-password") is None
    assert second.authenticate_account(username="   ", password=password) is None

    with sqlite3.connect(database_path) as connection:
        rows = connection.execute("SELECT username, role, salt, password_hash FROM users").fetchall()

    assert len(rows) == 1
    stored_username, stored_role, stored_salt, stored_hash = rows[0]
    assert stored_username == "mira"
    assert stored_role == "learner"
    assert isinstance(stored_salt, bytes)
    assert isinstance(stored_hash, bytes)
    assert password.encode("utf-8") not in stored_hash
    assert password.encode("utf-8") not in stored_salt


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
        "error": "invalid_username",
        "phase": "auth_register",
        "detail": "Username must be at least 3 characters.",
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
        "error": "reserved_username",
        "phase": "auth_register",
        "detail": "The admin username is reserved.",
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


def test_storage_init_error_uses_storage_init_phase(tmp_path: Path) -> None:
    database_directory = tmp_path / "directory.sqlite3"
    database_directory.mkdir()

    with pytest.raises(StorageError) as exc_info:
        MiraLingoStorage(database_directory)

    assert exc_info.value.phase == "storage_init"
    assert exc_info.value.public_payload()["phase"] == "storage_init"
