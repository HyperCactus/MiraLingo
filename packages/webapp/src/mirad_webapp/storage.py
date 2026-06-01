"""SQLite-backed storage boundary for MiraLingo learners and practice history."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from secrets import compare_digest, token_bytes
from typing import Any

from .auth import AuthUser, LEARNER_ROLE, LOCAL_ADMIN_USERNAME, _hash_password, normalize_username, validate_registration_inputs
from .practice import MAX_EVENTS
from .practice_engine import ENGLISH_TO_MIRAD, MIRAD_TO_ENGLISH

SUPPORTED_THEMES = ("light", "dark", "system")
DEFAULT_THEME = "system"
DEFAULT_TTS_SPEED = 0.8
DEFAULT_VOICE_ID = "de6"
DEFAULT_VOICE_LABEL = "Mirad de6"
DEFAULT_VOICE_PROVIDER = "mbrola"


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
    prompt_language: str
    answer_language: str
    shown_at: str

    def public_dict(self) -> dict[str, str]:
        return {
            "username": self.username,
            "card_id": self.card_id,
            "base_card_id": self.base_card_id,
            "direction": self.direction,
            "card_type": self.card_type,
            "prompt_language": self.prompt_language,
            "answer_language": self.answer_language,
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


@dataclass(frozen=True)
class UserSettingsRecord:
    """Durable learner settings plus fixed voice metadata."""

    username: str
    theme: str = DEFAULT_THEME
    tts_speed: float = DEFAULT_TTS_SPEED
    tts_autoplay: bool = True
    sfx_enabled: bool = True
    voice_id: str = DEFAULT_VOICE_ID

    def public_dict(self) -> dict[str, Any]:
        return {
            "theme": self.theme,
            "tts_speed": self.tts_speed,
            "voice": {
                "id": self.voice_id,
                "label": DEFAULT_VOICE_LABEL,
                "provider": DEFAULT_VOICE_PROVIDER,
                "mutable": False,
            },
        }


VALID_PRACTICE_DIRECTIONS = {ENGLISH_TO_MIRAD, MIRAD_TO_ENGLISH}


@dataclass(frozen=True)
class PracticeSessionRecord:
    session_id: str
    username: str
    started_at: str
    ended_at: str | None

    def public_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "username": self.username,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
        }


@dataclass(frozen=True)
class PracticeLifecycleRecord:
    username: str
    base_card_id: str
    direction: str
    lifecycle: str
    first_seen_at: str
    last_seen_at: str
    correct_streak: int
    session_streak: int
    promoted_at: str | None
    regression_count: int
    last_regressed_at: str | None

    def public_dict(self) -> dict[str, Any]:
        return {
            "username": self.username,
            "base_card_id": self.base_card_id,
            "direction": self.direction,
            "lifecycle": self.lifecycle,
            "first_seen_at": self.first_seen_at,
            "last_seen_at": self.last_seen_at,
            "correct_streak": self.correct_streak,
            "session_streak": self.session_streak,
            "promoted_at": self.promoted_at,
            "regression_count": self.regression_count,
            "last_regressed_at": self.last_regressed_at,
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

    def ensure_session_user(self, *, username: str, role: str, phase: str) -> AuthUser:
        """Ensure a session-authenticated user exists for practice foreign keys.

        Registered learners already have a users row. Local development admin
        sessions are not registered through learner auth, so this method creates a
        non-authenticating profile row only when needed for durable practice rows.
        """
        normalized_username = _require_username(username, phase=phase)
        salt = token_bytes(16)
        password_hash = token_bytes(32)
        try:
            with self._connect(phase) as connection:
                connection.execute(
                    """
                    INSERT INTO users (username, role, salt, password_hash, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(username) DO NOTHING
                    """,
                    (normalized_username, str(role or LEARNER_ROLE), salt, password_hash, _utcnow_iso()),
                )
        except sqlite3.Error as exc:
            raise StorageError(phase=phase, detail="Could not prepare user practice storage.") from exc
        return AuthUser(username=normalized_username, role=str(role or LEARNER_ROLE))

    def record_cards_shown(self, *, username: str, cards: list[dict[str, Any]]) -> list[ShownCardRecord]:
        """Persist a queue response's shown cards in one short transaction."""
        normalized_username = _require_username(username, phase="practice_queue")
        timestamp = _utcnow_iso()
        rows: list[tuple[str, str, str, str, str, str, str, str]] = []
        for card in cards:
            rows.append(
                (
                    normalized_username,
                    str(card.get("id") or ""),
                    str(card.get("base_card_id") or ""),
                    str(card.get("direction") or ""),
                    str(card.get("type") or ""),
                    str(card.get("prompt_language") or ""),
                    str(card.get("answer_language") or ""),
                    timestamp,
                )
            )
        try:
            with self._connect("practice_queue") as connection:
                connection.executemany(
                    """
                    INSERT INTO shown_cards
                        (username, card_id, base_card_id, direction, card_type,
                         prompt_language, answer_language, shown_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    rows,
                )
        except sqlite3.Error as exc:
            raise StorageError(phase="practice_queue", detail="Could not record shown cards.") from exc
        return [ShownCardRecord(*row) for row in rows]

    def record_card_shown(
        self,
        *,
        username: str,
        card_id: str,
        base_card_id: str,
        direction: str,
        card_type: str,
        prompt_language: str = "",
        answer_language: str = "",
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
            str(prompt_language),
            str(answer_language),
            timestamp,
        )
        try:
            with self._connect("practice_queue") as connection:
                connection.execute(
                    """
                    INSERT INTO shown_cards
                        (username, card_id, base_card_id, direction, card_type,
                         prompt_language, answer_language, shown_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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

    def start_practice_session(self, *, username: str, started_at: datetime | str | None = None) -> dict[str, Any]:
        normalized_username = _require_username(username, phase="practice_session")
        session_id = token_bytes(16).hex()
        timestamp = _coerce_timestamp(started_at)
        try:
            with self._connect("practice_session") as connection:
                connection.execute(
                    "INSERT INTO practice_sessions (session_id, username, started_at) VALUES (?, ?, ?)",
                    (session_id, normalized_username, timestamp),
                )
        except sqlite3.Error as exc:
            raise StorageError(phase="practice_session", detail="Could not start practice session.") from exc
        return {"session_id": session_id, "username": normalized_username, "started_at": timestamp, "ended_at": None}

    def get_or_start_active_practice_session(self, *, username: str) -> dict[str, Any]:
        normalized_username = _require_username(username, phase="practice_session")
        try:
            with self._connect("practice_session") as connection:
                row = connection.execute(
                    """
                    SELECT session_id, username, started_at, ended_at
                    FROM practice_sessions
                    WHERE username = ? AND ended_at IS NULL
                    ORDER BY started_at DESC
                    LIMIT 1
                    """,
                    (normalized_username,),
                ).fetchone()
                if row is not None:
                    return {
                        "session_id": str(row["session_id"]),
                        "username": str(row["username"]),
                        "started_at": row["started_at"],
                        "ended_at": row["ended_at"],
                    }
        except sqlite3.Error as exc:
            raise StorageError(phase="practice_session", detail="Could not read active practice session.") from exc
        return self.start_practice_session(username=normalized_username)

    def record_practice_lifecycle_answer(
        self,
        *,
        username: str,
        session_id: str,
        base_card_id: str,
        direction: str,
        correct: bool,
        card_id: str | None = None,
        card_type: str = "word",
        submitted_answer: str = "",
        expected_answer: str = "",
        answered_at: datetime | str | None = None,
    ) -> dict[str, Any]:
        normalized_username = _require_username(username, phase="practice_lifecycle")
        normalized_direction = _require_direction(direction, phase="practice_lifecycle")
        normalized_base_card_id = str(base_card_id or "").strip()
        normalized_session_id = str(session_id or "").strip()
        if not normalized_base_card_id or not normalized_session_id:
            raise StorageError(phase="practice_lifecycle", detail="A base_card_id and session_id are required.", error="invalid_practice_item")
        timestamp = _coerce_timestamp(answered_at)
        normalized_card_id = str(card_id or normalized_base_card_id)
        try:
            with self._connect("practice_lifecycle") as connection:
                session_row = connection.execute(
                    "SELECT session_id FROM practice_sessions WHERE session_id = ? AND username = ?",
                    (normalized_session_id, normalized_username),
                ).fetchone()
                if session_row is None:
                    raise StorageError(phase="practice_lifecycle", detail="Practice session not found.", error="invalid_session")
                connection.execute(
                    """
                    INSERT INTO answer_events (username, card_id, base_card_id, direction, card_type, submitted_answer, expected_answer, correct, answered_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (normalized_username, normalized_card_id, normalized_base_card_id, normalized_direction, str(card_type), str(submitted_answer), str(expected_answer), 1 if bool(correct) else 0, timestamp),
                )
                row = connection.execute(
                    "SELECT * FROM practice_lifecycle WHERE username=? AND base_card_id=? AND direction=?",
                    (normalized_username, normalized_base_card_id, normalized_direction),
                ).fetchone()
                if row is None:
                    connection.execute(
                        """INSERT INTO practice_lifecycle
                        (username, base_card_id, direction, lifecycle, first_seen_at, last_seen_at, consecutive_correct, correct_session_streak, promoted_at, regression_count, last_regressed_at, last_session_id_counted)
                        VALUES (?, ?, ?, 'active', ?, ?, 0, 0, NULL, 0, NULL, NULL)
                        """,
                        (normalized_username, normalized_base_card_id, normalized_direction, timestamp, timestamp),
                    )
                    row = connection.execute(
                        "SELECT * FROM practice_lifecycle WHERE username=? AND base_card_id=? AND direction=?",
                        (normalized_username, normalized_base_card_id, normalized_direction),
                    ).fetchone()
                lifecycle = str(row["lifecycle"])
                consecutive = int(row["consecutive_correct"])
                session_streak = int(row["correct_session_streak"])
                last_session_counted = row["last_session_id_counted"]
                regression_count = int(row["regression_count"])
                promoted_at = row["promoted_at"]
                last_regressed_at = row["last_regressed_at"]

                if bool(correct):
                    consecutive += 1
                    if last_session_counted != normalized_session_id:
                        session_streak += 1
                        last_session_counted = normalized_session_id
                    if lifecycle != "revision" and consecutive >= 4 and session_streak >= 2:
                        lifecycle = "revision"
                        promoted_at = timestamp
                else:
                    if lifecycle == "revision":
                        regression_count += 1
                        last_regressed_at = timestamp
                    lifecycle = "active"
                    consecutive = 0
                    session_streak = 0
                    last_session_counted = None
                    promoted_at = None

                connection.execute(
                    """UPDATE practice_lifecycle SET lifecycle=?, last_seen_at=?, consecutive_correct=?, correct_session_streak=?, promoted_at=?, regression_count=?, last_regressed_at=?, last_session_id_counted=?
                       WHERE username=? AND base_card_id=? AND direction=?""",
                    (lifecycle, timestamp, consecutive, session_streak, promoted_at, regression_count, last_regressed_at, last_session_counted, normalized_username, normalized_base_card_id, normalized_direction),
                )
        except StorageError:
            raise
        except sqlite3.Error as exc:
            raise StorageError(phase="practice_lifecycle", detail="Could not record practice lifecycle answer.") from exc

        return self.get_practice_lifecycle(username=normalized_username, base_card_id=normalized_base_card_id, direction=normalized_direction)

    def get_practice_lifecycle(self, *, username: str, base_card_id: str, direction: str) -> dict[str, Any]:
        normalized_username = _require_username(username, phase="practice_lifecycle")
        normalized_direction = _require_direction(direction, phase="practice_lifecycle")
        normalized_base_card_id = str(base_card_id or "").strip()
        if not normalized_base_card_id:
            raise StorageError(phase="practice_lifecycle", detail="A base_card_id is required.", error="invalid_practice_item")
        try:
            with self._connect("practice_lifecycle") as connection:
                row = connection.execute(
                    "SELECT * FROM practice_lifecycle WHERE username=? AND base_card_id=? AND direction=?",
                    (normalized_username, normalized_base_card_id, normalized_direction),
                ).fetchone()
        except sqlite3.Error as exc:
            raise StorageError(phase="practice_lifecycle", detail="Could not read practice lifecycle.") from exc
        if row is None:
            return {
                "username": normalized_username,
                "base_card_id": normalized_base_card_id,
                "direction": normalized_direction,
                "lifecycle": "active",
                "first_seen_at": None,
                "last_seen_at": None,
                "correct_streak": 0,
                "session_streak": 0,
                "promoted_at": None,
                "regression_count": 0,
                "last_regressed_at": None,
            }
        return {
            "username": str(row["username"]), "base_card_id": str(row["base_card_id"]), "direction": str(row["direction"]),
            "lifecycle": str(row["lifecycle"]), "first_seen_at": row["first_seen_at"], "last_seen_at": row["last_seen_at"],
            "correct_streak": int(row["consecutive_correct"]), "session_streak": int(row["correct_session_streak"]),
            "promoted_at": row["promoted_at"], "regression_count": int(row["regression_count"]), "last_regressed_at": row["last_regressed_at"],
        }

    def list_answer_events(
        self, *, username: str, limit: int = MAX_EVENTS, phase: str = "practice_progress"
    ) -> list[AnswerEventRecord]:
        """Return newest bounded answer events in chronological order, skipping malformed rows."""
        normalized_username = _require_username(username, phase=phase)
        bounded_limit = _bounded_limit(limit)
        try:
            with self._connect(phase) as connection:
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
            raise StorageError(phase=phase, detail="Could not list answer events.") from exc
        return list(reversed([record for row in rows if (record := _answer_event_from_row(row)) is not None]))

    def list_shown_cards(self, *, username: str, limit: int = MAX_EVENTS) -> list[ShownCardRecord]:
        """Return newest bounded shown-card rows in chronological order, skipping malformed rows."""
        normalized_username = _require_username(username, phase="practice_progress")
        bounded_limit = _bounded_limit(limit)
        try:
            with self._connect("practice_progress") as connection:
                rows = connection.execute(
                    """
                    SELECT username, card_id, base_card_id, direction, card_type,
                           prompt_language, answer_language, shown_at
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

    def list_shown_card_keys(self, *, username: str) -> set[tuple[str, str]]:
        """Return all seen (base_card_id, direction) pairs for one learner."""
        normalized_username = _require_username(username, phase="practice_queue")
        try:
            with self._connect("practice_queue") as connection:
                rows = connection.execute(
                    """
                    SELECT base_card_id, direction
                    FROM shown_cards
                    WHERE username = ?
                    """,
                    (normalized_username,),
                ).fetchall()
        except sqlite3.Error as exc:
            raise StorageError(phase="practice_queue", detail="Could not list shown card keys.") from exc
        return {
            (str(row["base_card_id"]), str(row["direction"]))
            for row in rows
            if row["base_card_id"] and row["direction"]
        }

    def get_user_settings(self, *, username: str) -> UserSettingsRecord:
        """Return one learner's durable settings, creating defaults on first access."""
        normalized_username = _require_username(username, phase="settings_get")
        try:
            with self._connect("settings_get") as connection:
                self._ensure_user_settings_row(connection, normalized_username)
                row = connection.execute(
                    """
                    SELECT username, theme, tts_speed, tts_autoplay, sfx_enabled, voice_id
                    FROM user_settings
                    WHERE username = ?
                    """,
                    (normalized_username,),
                ).fetchone()
        except sqlite3.Error as exc:
            raise StorageError(phase="settings_get", detail="Could not read settings.") from exc

        if row is None:
            return UserSettingsRecord(username=normalized_username)
        return UserSettingsRecord(
            username=str(row["username"]),
            theme=str(row["theme"] or DEFAULT_THEME),
            tts_speed=float(row["tts_speed"]),
            tts_autoplay=bool(row["tts_autoplay"]),
            sfx_enabled=bool(row["sfx_enabled"]),
            voice_id=str(row["voice_id"] or DEFAULT_VOICE_ID),
        )

    def upsert_user_settings(self, *, username: str, theme: str, tts_speed: float, tts_autoplay: bool = True, sfx_enabled: bool = True) -> UserSettingsRecord:
        """Create or update durable learner settings for supported theme/speed values."""
        normalized_username = _require_username(username, phase="settings_update")
        normalized_theme = _require_theme(theme, phase="settings_update")
        normalized_speed = _require_tts_speed(tts_speed, phase="settings_update")
        normalized_tts_autoplay = bool(tts_autoplay)
        normalized_sfx_enabled = bool(sfx_enabled)
        try:
            with self._connect("settings_update") as connection:
                self._ensure_user_settings_row(connection, normalized_username)
                connection.execute(
                    """
                    UPDATE user_settings
                    SET theme = ?, tts_speed = ?, tts_autoplay = ?, sfx_enabled = ?, voice_id = ?
                    WHERE username = ?
                    """,
                    (normalized_theme, normalized_speed, 1 if normalized_tts_autoplay else 0, 1 if normalized_sfx_enabled else 0, DEFAULT_VOICE_ID, normalized_username),
                )
        except sqlite3.Error as exc:
            raise StorageError(phase="settings_update", detail="Could not update settings.") from exc
        return UserSettingsRecord(
            username=normalized_username,
            theme=normalized_theme,
            tts_speed=normalized_speed,
            tts_autoplay=normalized_tts_autoplay,
            sfx_enabled=normalized_sfx_enabled,
            voice_id=DEFAULT_VOICE_ID,
        )

    def delete_user_account(self, *, username: str) -> bool:
        """Delete a learner account and owned rows via foreign-key cascades."""
        normalized_username = _require_username(username, phase="account_delete")
        if normalized_username == LOCAL_ADMIN_USERNAME:
            raise StorageError(
                phase="account_delete",
                detail="The local admin account cannot be deleted.",
                error="protected_account",
            )
        try:
            with self._connect("account_delete") as connection:
                deleted = connection.execute(
                    "DELETE FROM users WHERE username = ?",
                    (normalized_username,),
                ).rowcount
        except sqlite3.Error as exc:
            raise StorageError(phase="account_delete", detail="Could not delete account.") from exc
        return bool(deleted)

    def _ensure_user_settings_row(self, connection: sqlite3.Connection, username: str) -> None:
        connection.execute(
            """
            INSERT INTO user_settings (username, theme, tts_speed, voice_id)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(username) DO NOTHING
            """,
            (username, DEFAULT_THEME, DEFAULT_TTS_SPEED, DEFAULT_VOICE_ID),
        )

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
                        prompt_language TEXT NOT NULL DEFAULT '',
                        answer_language TEXT NOT NULL DEFAULT '',
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

                    CREATE TABLE IF NOT EXISTS user_settings (
                        username TEXT PRIMARY KEY,
                        theme TEXT NOT NULL DEFAULT 'system' CHECK(theme IN ('light', 'dark', 'system')),
                        tts_speed REAL NOT NULL DEFAULT 0.8 CHECK(tts_speed > 0 AND tts_speed <= 2.0),
                        voice_id TEXT NOT NULL DEFAULT 'de6',
                        FOREIGN KEY(username) REFERENCES users(username) ON DELETE CASCADE
                    );

                    CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
                    CREATE INDEX IF NOT EXISTS idx_shown_cards_user_time ON shown_cards(username, shown_at);
                    CREATE INDEX IF NOT EXISTS idx_shown_cards_user_card ON shown_cards(username, card_id);
                    CREATE INDEX IF NOT EXISTS idx_answer_events_user_time ON answer_events(username, answered_at);
                    CREATE INDEX IF NOT EXISTS idx_answer_events_user_card ON answer_events(username, card_id);

                    CREATE TABLE IF NOT EXISTS practice_sessions (
                        session_id TEXT PRIMARY KEY,
                        username TEXT NOT NULL,
                        started_at TEXT NOT NULL,
                        ended_at TEXT,
                        FOREIGN KEY(username) REFERENCES users(username) ON DELETE CASCADE
                    );

                    CREATE TABLE IF NOT EXISTS practice_lifecycle (
                        username TEXT NOT NULL,
                        base_card_id TEXT NOT NULL,
                        direction TEXT NOT NULL,
                        lifecycle TEXT NOT NULL DEFAULT 'active' CHECK(lifecycle IN ('active','revision')),
                        first_seen_at TEXT NOT NULL,
                        last_seen_at TEXT NOT NULL,
                        consecutive_correct INTEGER NOT NULL DEFAULT 0,
                        correct_session_streak INTEGER NOT NULL DEFAULT 0,
                        promoted_at TEXT,
                        regression_count INTEGER NOT NULL DEFAULT 0,
                        last_regressed_at TEXT,
                        last_session_id_counted TEXT,
                        PRIMARY KEY (username, base_card_id, direction),
                        FOREIGN KEY(username) REFERENCES users(username) ON DELETE CASCADE
                    );

                    CREATE INDEX IF NOT EXISTS idx_practice_sessions_user_started ON practice_sessions(username, started_at);
                    CREATE INDEX IF NOT EXISTS idx_practice_lifecycle_lookup ON practice_lifecycle(username, base_card_id, direction);
                    """
                )
                _ensure_column(connection, "shown_cards", "prompt_language", "TEXT NOT NULL DEFAULT ''")
                _ensure_column(connection, "shown_cards", "answer_language", "TEXT NOT NULL DEFAULT ''")
                _ensure_column(connection, "user_settings", "tts_autoplay", "INTEGER NOT NULL DEFAULT 1 CHECK(tts_autoplay IN (0, 1))")
                _ensure_column(connection, "user_settings", "sfx_enabled", "INTEGER NOT NULL DEFAULT 1 CHECK(sfx_enabled IN (0, 1))")
                _ensure_column(connection, "user_settings", "voice_id", "TEXT NOT NULL DEFAULT 'de6'")
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


def _ensure_column(connection: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    existing = {str(row[1]) for row in connection.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in existing:
        connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


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


def _require_direction(direction: str, *, phase: str) -> str:
    normalized = str(direction or "").strip().lower()
    if normalized not in VALID_PRACTICE_DIRECTIONS:
        raise StorageError(phase=phase, detail="Direction must be english_to_mirad or mirad_to_english.", error="invalid_direction")
    return normalized


def _require_theme(theme: str, *, phase: str) -> str:
    normalized = str(theme or "").strip().lower()
    if normalized not in SUPPORTED_THEMES:
        raise StorageError(phase=phase, detail="Theme must be one of: light, dark, system.", error="invalid_theme")
    return normalized


def _require_tts_speed(tts_speed: float, *, phase: str) -> float:
    try:
        numeric = float(tts_speed)
    except (TypeError, ValueError) as exc:
        raise StorageError(
            phase=phase,
            detail="TTS speed must be a number between 0 and 2.0.",
            error="invalid_tts_speed",
        ) from exc
    if numeric <= 0 or numeric > 2.0:
        raise StorageError(
            phase=phase,
            detail="TTS speed must be a number between 0 and 2.0.",
            error="invalid_tts_speed",
        )
    return numeric


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
        prompt_language = str(row["prompt_language"] if "prompt_language" in row.keys() else "")
        answer_language = str(row["answer_language"] if "answer_language" in row.keys() else "")
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
        prompt_language=prompt_language,
        answer_language=answer_language,
        shown_at=shown_at,
    )
