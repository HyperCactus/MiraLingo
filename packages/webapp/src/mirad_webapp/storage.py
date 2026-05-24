"""SQLite-backed storage boundary for MiraLingo learners and practice history."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from secrets import compare_digest, token_bytes
from typing import Any

from .auth import AuthUser, LEARNER_ROLE, _hash_password, normalize_username, validate_registration_inputs
from .practice import MAX_EVENTS


class StorageError(RuntimeError):
    """Storage-layer failure with API-safe diagnostic metadata."""

    def __init__(self, *, phase: str, detail: str, error: str = "storage_error") -> None:
        super().__init__(detail)
        self.phase = phase
        self.detail = detail
        self.error = error

    def public_payload(self) -> dict[str, str]:
        """Return a stable, secret-free JSON payload for API handlers."""
        return {"ok": False, "error": self.error, "phase": self.phase, "detail": self.detail}


@dataclass(frozen=True)
class ShownCardRecord:
    """One durable record of a card shown to a learner."""

    username: str
    card_id: str
    base_card_id: str
    direction: str
    card_type: str
    shown_at: str

    def public_dict(self) -> dict[str, str]:
        return {
            "username": self.username,
            "card_id": self.card_id,
            "base_card_id": self.base_card_id,
            "direction": self.direction,
            "card_type": self.card_type,
            "shown_at": self.shown_at,
        }


@dataclass(frozen=True)
class AnswerEventRecord:
    """One durable answer event for a learner practice item."""

    username: str
    card_id: str
    base_card_id: str
    direction: str
    card_type: str
    submitted_answer: str
    expected_answer: str
    correct: bool
    answered_at: str

    def public_dict(self) -> dict[str, Any]:
        return {
            "username": self.username,
            "card_id": self.card_id,
            "base_card_id": self.base_card_id,
            "direction": self.direction,
            "card_type": self.card_type,
            "submitted_answer": self.submitted_answer,
            "expected_answer": self.expected_answer,
            "correct": self.correct,
            "answered_at": self.answered_at,
        }

    def practice_event(self) -> dict[str, Any]:
        """Return the event shape consumed by the practice scheduler."""
        return {
            "card_id": self.card_id,
            "base_card_id": self.base_card_id,
            "direction": self.direction,
            "card_type": self.card_type,
            "submitted_answer": self.submitted_answer,
            "expected_answer": self.expected_answer,
            "correct": self.correct,
            "answered_at": self.answered_at,
        }


class MiraLingoStorage:
    """Short-lived SQLite connection boundary for learner and practice persistence."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self._initialize_schema()

    def register_account(
        self, *, username: str, password: str
    ) -> tuple[AuthUser | None, dict[str, Any] | None, int | None]:
        """Register a learner account or return the existing public auth error shape."""
        normalized_username, validation_error, validation_status = validate_registration_inputs(
            username=username,
            password=password,
        )
        if normalized_username is None:
            return None, validation_error, validation_status

        salt = token_bytes(16)
        try:
            with self._connect("auth_register") as connection:
                connection.execute(
                    """
                    INSERT INTO users (username, role, salt, password_hash, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        normalized_username,
                        LEARNER_ROLE,
                        salt,
                        _hash_password(password=password, salt=salt),
                        _utcnow_iso(),
                    ),
                )
        except sqlite3.IntegrityError:
            return None, _username_unavailable_payload(), 409
        except sqlite3.Error as exc:
            raise StorageError(
                phase="auth_register",
                detail="Could not register account in storage.",
            ) from exc

        return AuthUser(username=normalized_username, role=LEARNER_ROLE), None, None

    def authenticate_account(self, *, username: str, password: str) -> AuthUser | None:
        """Authenticate a durable learner account without exposing secret material."""
        normalized_username = normalize_username(username)
        if normalized_username is None:
            return None
        try:
            with self._connect("auth_login") as connection:
                row = connection.execute(
                    "SELECT username, role, salt, password_hash FROM users WHERE username = ?",
                    (normalized_username,),
                ).fetchone()
        except sqlite3.Error as exc:
            raise StorageError(phase="auth_login", detail="Could not read account from storage.") from exc

        if row is None:
            return None
        salt = _bytes_from_row(row["salt"])
        password_hash = _bytes_from_row(row["password_hash"])
        if salt is None or password_hash is None:
            return None
        candidate_hash = _hash_password(password=password, salt=salt)
        if not compare_digest(candidate_hash, password_hash):
            return None
        return AuthUser(username=str(row["username"]), role=str(row["role"] or LEARNER_ROLE))

    def record_card_shown(
        self,
        *,
        username: str,
        card_id: str,
        base_card_id: str,
        direction: str,
        card_type: str,
        shown_at: datetime | str | None = None,
    ) -> ShownCardRecord:
        """Persist that one practice card was shown to a learner."""
        normalized_username = _require_username(username, phase="practice_queue")
        timestamp = _coerce_timestamp(shown_at)
        values = (
            normalized_username,
            str(card_id),
            str(base_card_id),
            str(direction),
            str(card_type),
            timestamp,
        )
        try:
            with self._connect("practice_queue") as connection:
                connection.execute(
                    """
                    INSERT INTO shown_cards
                        (username, card_id, base_card_id, direction, card_type, shown_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    values,
                )
        except sqlite3.Error as exc:
            raise StorageError(phase="practice_queue", detail="Could not record shown card.") from exc
        return ShownCardRecord(*values)

    def append_answer_event(
        self,
        *,
        username: str,
        card_id: str,
        base_card_id: str,
        direction: str,
        card_type: str,
        submitted_answer: str,
        expected_answer: str,
        correct: bool,
        answered_at: datetime | str | None = None,
    ) -> AnswerEventRecord:
        """Persist one practice answer event."""
        normalized_username = _require_username(username, phase="practice_answer")
        timestamp = _coerce_timestamp(answered_at)
        values = (
            normalized_username,
            str(card_id),
            str(base_card_id),
            str(direction),
            str(card_type),
            str(submitted_answer),
            str(expected_answer),
            1 if bool(correct) else 0,
            timestamp,
        )
        try:
            with self._connect("practice_answer") as connection:
                connection.execute(
                    """
                    INSERT INTO answer_events
                        (username, card_id, base_card_id, direction, card_type,
                         submitted_answer, expected_answer, correct, answered_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    values,
                )
        except sqlite3.Error as exc:
            raise StorageError(phase="practice_answer", detail="Could not record answer event.") from exc
        return AnswerEventRecord(
            username=values[0],
            card_id=values[1],
            base_card_id=values[2],
            direction=values[3],
            card_type=values[4],
            submitted_answer=values[5],
            expected_answer=values[6],
            correct=bool(values[7]),
            answered_at=values[8],
        )

    def list_answer_events(self, *, username: str, limit: int = MAX_EVENTS) -> list[AnswerEventRecord]:
        """Return newest bounded answer events in chronological order, skipping malformed rows."""
        normalized_username = _require_username(username, phase="practice_progress")
        bounded_limit = _bounded_limit(limit)
        try:
            with self._connect("practice_progress") as connection:
                rows = connection.execute(
                    """
                    SELECT username, card_id, base_card_id, direction, card_type,
                           submitted_answer, expected_answer, correct, answered_at
                    FROM answer_events
                    WHERE username = ?
                    ORDER BY answered_at DESC, id DESC
                    LIMIT ?
                    """,
                    (normalized_username, bounded_limit),
                ).fetchall()
        except sqlite3.Error as exc:
            raise StorageError(phase="practice_progress", detail="Could not list answer events.") from exc
        return list(reversed([record for row in rows if (record := _answer_event_from_row(row)) is not None]))

    def list_shown_cards(self, *, username: str, limit: int = MAX_EVENTS) -> list[ShownCardRecord]:
        """Return newest bounded shown-card rows in chronological order, skipping malformed rows."""
        normalized_username = _require_username(username, phase="practice_progress")
        bounded_limit = _bounded_limit(limit)
        try:
            with self._connect("practice_progress") as connection:
                rows = connection.execute(
                    """
                    SELECT username, card_id, base_card_id, direction, card_type, shown_at
                    FROM shown_cards
                    WHERE username = ?
                    ORDER BY shown_at DESC, id DESC
                    LIMIT ?
                    """,
                    (normalized_username, bounded_limit),
                ).fetchall()
        except sqlite3.Error as exc:
            raise StorageError(phase="practice_progress", detail="Could not list shown cards.") from exc
        return list(reversed([record for row in rows if (record := _shown_card_from_row(row)) is not None]))

    def _initialize_schema(self) -> None:
        try:
            self.database_path.parent.mkdir(parents=True, exist_ok=True)
            with self._connect("storage_init") as connection:
                connection.executescript(
                    """
                    PRAGMA foreign_keys = ON;

                    CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        role TEXT NOT NULL,
                        salt BLOB NOT NULL,
                        password_hash BLOB NOT NULL,
                        created_at TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS shown_cards (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        card_id TEXT NOT NULL,
                        base_card_id TEXT NOT NULL,
                        direction TEXT NOT NULL,
                        card_type TEXT NOT NULL,
                        shown_at TEXT NOT NULL,
                        FOREIGN KEY(username) REFERENCES users(username) ON DELETE CASCADE
                    );

                    CREATE TABLE IF NOT EXISTS answer_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        card_id TEXT NOT NULL,
                        base_card_id TEXT NOT NULL,
                        direction TEXT NOT NULL,
                        card_type TEXT NOT NULL,
                        submitted_answer TEXT NOT NULL,
                        expected_answer TEXT NOT NULL,
                        correct INTEGER NOT NULL CHECK(correct IN (0, 1)),
                        answered_at TEXT NOT NULL,
                        FOREIGN KEY(username) REFERENCES users(username) ON DELETE CASCADE
                    );

                    CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
                    CREATE INDEX IF NOT EXISTS idx_shown_cards_user_time ON shown_cards(username, shown_at);
                    CREATE INDEX IF NOT EXISTS idx_shown_cards_user_card ON shown_cards(username, card_id);
                    CREATE INDEX IF NOT EXISTS idx_answer_events_user_time ON answer_events(username, answered_at);
                    CREATE INDEX IF NOT EXISTS idx_answer_events_user_card ON answer_events(username, card_id);
                    """
                )
        except sqlite3.Error as exc:
            raise StorageError(phase="storage_init", detail="Could not initialize SQLite storage.") from exc
        except OSError as exc:
            raise StorageError(phase="storage_init", detail="Could not create SQLite storage directory.") from exc

    def _connect(self, phase: str) -> sqlite3.Connection:
        try:
            connection = sqlite3.connect(self.database_path)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            return connection
        except sqlite3.Error as exc:
            raise StorageError(phase=phase, detail="Could not open SQLite storage.") from exc


def _username_unavailable_payload() -> dict[str, Any]:
    return {
        "authenticated": False,
        "error": "username_unavailable",
        "phase": "auth_register",
        "detail": "Username is already registered.",
    }


def _require_username(username: str, *, phase: str) -> str:
    normalized = normalize_username(username)
    if normalized is None:
        raise StorageError(phase=phase, detail="A non-blank username is required.", error="invalid_username")
    return normalized


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_timestamp(value: datetime | str | None) -> str:
    if value is None:
        return _utcnow_iso()
    if isinstance(value, datetime):
        timestamp = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
        return timestamp.isoformat()
    return str(value)


def _bounded_limit(limit: int) -> int:
    try:
        numeric = int(limit)
    except (TypeError, ValueError):
        return MAX_EVENTS
    return max(0, min(numeric, MAX_EVENTS))


def _bytes_from_row(value: Any) -> bytes | None:
    if isinstance(value, bytes):
        return value
    if isinstance(value, memoryview):
        return value.tobytes()
    return None


def _answer_event_from_row(row: sqlite3.Row) -> AnswerEventRecord | None:
    try:
        username = str(row["username"]).strip().lower()
        card_id = str(row["card_id"])
        base_card_id = str(row["base_card_id"])
        direction = str(row["direction"])
        card_type = str(row["card_type"])
        submitted_answer = str(row["submitted_answer"])
        expected_answer = str(row["expected_answer"])
        correct_raw = row["correct"]
        answered_at = str(row["answered_at"])
    except (KeyError, TypeError, ValueError):
        return None
    if not all([username, card_id, base_card_id, direction, card_type, answered_at]):
        return None
    if correct_raw not in (0, 1, False, True):
        return None
    return AnswerEventRecord(
        username=username,
        card_id=card_id,
        base_card_id=base_card_id,
        direction=direction,
        card_type=card_type,
        submitted_answer=submitted_answer,
        expected_answer=expected_answer,
        correct=bool(correct_raw),
        answered_at=answered_at,
    )


def _shown_card_from_row(row: sqlite3.Row) -> ShownCardRecord | None:
    try:
        username = str(row["username"]).strip().lower()
        card_id = str(row["card_id"])
        base_card_id = str(row["base_card_id"])
        direction = str(row["direction"])
        card_type = str(row["card_type"])
        shown_at = str(row["shown_at"])
    except (KeyError, TypeError, ValueError):
        return None
    if not all([username, card_id, base_card_id, direction, card_type, shown_at]):
        return None
    return ShownCardRecord(
        username=username,
        card_id=card_id,
        base_card_id=base_card_id,
        direction=direction,
        card_type=card_type,
        shown_at=shown_at,
    )
