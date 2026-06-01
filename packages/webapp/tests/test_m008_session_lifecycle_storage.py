from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from mirad_webapp.storage import MiraLingoStorage, StorageError


def _count(connection: sqlite3.Connection, table: str, where: str = "", args: tuple[object, ...] = ()) -> int:
    query = f"SELECT COUNT(*) FROM {table}"
    if where:
        query += f" WHERE {where}"
    return int(connection.execute(query, args).fetchone()[0])


def test_lifecycle_contract_across_sessions_promotes_only_after_multi_session_streak(tmp_path: Path) -> None:
    storage = MiraLingoStorage(tmp_path / "m008.sqlite3")
    assert storage.register_account(username="mira", password="correct-password")[0] is not None

    session_one = storage.start_practice_session(username="mira")
    for _ in range(2):
        storage.record_practice_lifecycle_answer(
            username="mira",
            session_id=session_one["session_id"],
            base_card_id="word:hello",
            direction="english_to_mirad",
            correct=True,
        )

    state_after_one = storage.get_practice_lifecycle(
        username="mira",
        base_card_id="word:hello",
        direction="english_to_mirad",
    )
    assert state_after_one["lifecycle"] == "active"
    assert state_after_one["correct_streak"] == 2
    assert state_after_one["session_streak"] == 1

    session_two = storage.start_practice_session(username="mira")
    for _ in range(2):
        storage.record_practice_lifecycle_answer(
            username="mira",
            session_id=session_two["session_id"],
            base_card_id="word:hello",
            direction="english_to_mirad",
            correct=True,
        )

    promoted = storage.get_practice_lifecycle(
        username="mira",
        base_card_id="word:hello",
        direction="english_to_mirad",
    )
    assert promoted["lifecycle"] == "revision"
    assert promoted["correct_streak"] == 4
    assert promoted["session_streak"] == 2


def test_four_correct_in_single_session_does_not_promote(tmp_path: Path) -> None:
    storage = MiraLingoStorage(tmp_path / "m008.sqlite3")
    assert storage.register_account(username="mira", password="correct-password")[0] is not None

    session = storage.start_practice_session(username="mira")
    for _ in range(4):
        storage.record_practice_lifecycle_answer(
            username="mira",
            session_id=session["session_id"],
            base_card_id="word:tree",
            direction="english_to_mirad",
            correct=True,
        )

    state = storage.get_practice_lifecycle(
        username="mira",
        base_card_id="word:tree",
        direction="english_to_mirad",
    )
    assert state["lifecycle"] == "active"
    assert state["correct_streak"] == 4
    assert state["session_streak"] == 1


def test_wrong_answer_after_revision_demotes_and_resets_streaks(tmp_path: Path) -> None:
    storage = MiraLingoStorage(tmp_path / "m008.sqlite3")
    assert storage.register_account(username="mira", password="correct-password")[0] is not None

    for _ in range(2):
        session = storage.start_practice_session(username="mira")
        for _ in range(2):
            storage.record_practice_lifecycle_answer(
                username="mira",
                session_id=session["session_id"],
                base_card_id="word:moon",
                direction="english_to_mirad",
                correct=True,
            )

    before_wrong = storage.get_practice_lifecycle(
        username="mira",
        base_card_id="word:moon",
        direction="english_to_mirad",
    )
    assert before_wrong["lifecycle"] == "revision"

    session_three = storage.start_practice_session(username="mira")
    storage.record_practice_lifecycle_answer(
        username="mira",
        session_id=session_three["session_id"],
        base_card_id="word:moon",
        direction="english_to_mirad",
        correct=False,
    )

    after_wrong = storage.get_practice_lifecycle(
        username="mira",
        base_card_id="word:moon",
        direction="english_to_mirad",
    )
    assert after_wrong["lifecycle"] == "active"
    assert after_wrong["correct_streak"] == 0
    assert after_wrong["session_streak"] == 0


def test_lifecycle_is_independent_by_direction(tmp_path: Path) -> None:
    storage = MiraLingoStorage(tmp_path / "m008.sqlite3")
    assert storage.register_account(username="mira", password="correct-password")[0] is not None

    for _ in range(2):
        session = storage.start_practice_session(username="mira")
        for _ in range(2):
            storage.record_practice_lifecycle_answer(
                username="mira",
                session_id=session["session_id"],
                base_card_id="word:bird",
                direction="english_to_mirad",
                correct=True,
            )

    en_to_mirad = storage.get_practice_lifecycle(
        username="mira",
        base_card_id="word:bird",
        direction="english_to_mirad",
    )
    mirad_to_en = storage.get_practice_lifecycle(
        username="mira",
        base_card_id="word:bird",
        direction="mirad_to_english",
    )

    assert en_to_mirad["lifecycle"] == "revision"
    assert mirad_to_en["lifecycle"] == "active"
    assert mirad_to_en["correct_streak"] == 0
    assert mirad_to_en["session_streak"] == 0


def test_account_delete_cascades_practice_sessions_and_lifecycle_rows(tmp_path: Path) -> None:
    database_path = tmp_path / "m008.sqlite3"
    storage = MiraLingoStorage(database_path)
    assert storage.register_account(username="mira", password="correct-password")[0] is not None

    session = storage.start_practice_session(username="mira")
    storage.record_practice_lifecycle_answer(
        username="mira",
        session_id=session["session_id"],
        base_card_id="word:star",
        direction="english_to_mirad",
        correct=True,
    )

    assert storage.delete_user_account(username="mira") is True

    with sqlite3.connect(database_path) as connection:
        assert _count(connection, "practice_sessions") == 0
        assert _count(connection, "practice_lifecycle") == 0


def test_session_and_lifecycle_errors_expose_stable_public_payloads(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    storage = MiraLingoStorage(tmp_path / "m008.sqlite3")
    assert storage.register_account(username="mira", password="correct-password")[0] is not None

    with pytest.raises(StorageError) as invalid_user:
        storage.start_practice_session(username=" ")
    assert invalid_user.value.public_payload() == {
        "ok": False,
        "error": "invalid_username",
        "phase": "practice_session",
        "detail": "A non-blank username is required.",
    }

    with pytest.raises(StorageError) as blank_direction:
        storage.record_practice_lifecycle_answer(
            username="mira",
            session_id="session-1",
            base_card_id="word:test",
            direction="",
            correct=True,
        )
    assert blank_direction.value.public_payload()["phase"] == "practice_lifecycle"

    original_connect = storage._connect

    def broken_connect(phase: str):
        if phase == "practice_session":
            raise StorageError(phase="practice_session", detail="Could not open SQLite storage.")
        return original_connect(phase)

    monkeypatch.setattr(storage, "_connect", broken_connect)
    with pytest.raises(StorageError) as broken:
        storage.start_practice_session(username="mira")
    payload = broken.value.public_payload()
    assert payload["phase"] == "practice_session"
    assert "Traceback" not in repr(payload)
    assert "sqlite3" not in repr(payload)
