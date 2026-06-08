"""SQLite-backed storage boundary for MiraLingo learners and practice history."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from secrets import token_bytes, token_urlsafe
from typing import Any

from .auth import AuthUser, LEARNER_ROLE, LOCAL_ADMIN_EMAIL, LOCAL_ADMIN_USERNAME, hash_password, normalize_email, normalize_username, token_hash, validate_registration_inputs, verify_password
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
    sfx_mode: str = "on_answer"
    voice_id: str = DEFAULT_VOICE_ID

    def public_dict(self) -> dict[str, Any]:
        return {
            "theme": self.theme,
            "tts_speed": self.tts_speed,
            "tts_autoplay": self.tts_autoplay,
            "sfx_enabled": self.sfx_enabled,
            "sfx_mode": self.sfx_mode,
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
        self, *, email: str | None = None, password: str, name: str | None = None, username: str | None = None
    ) -> tuple[AuthUser | None, dict[str, Any] | None, int | None]:
        """Register an email/password learner account."""
        validated, validation_error, validation_status = validate_registration_inputs(
            email=email,
            username=username,
            password=password,
            name=name,
        )
        if validated is None:
            return None, validation_error, validation_status

        user_id = normalize_username(username) if username and not email and "@" not in username else _new_user_id()
        if user_id is None:
            user_id = _new_user_id()
        now = _utcnow_iso()
        try:
            with self._connect("auth_register") as connection:
                connection.execute(
                    """
                    INSERT INTO users (username, id, email, name, role, salt, password_hash, email_verified, disabled, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?)
                    """,
                    (
                        user_id,
                        user_id,
                        validated["email"],
                        validated["name"],
                        LEARNER_ROLE,
                        token_bytes(16),
                        hash_password(password),
                        now,
                        now,
                    ),
                )
        except sqlite3.IntegrityError:
            return None, _email_unavailable_payload(), 409
        except sqlite3.Error as exc:
            raise StorageError(phase="auth_register", detail="Could not register account in storage.") from exc

        return AuthUser(id=user_id, email=validated["email"], name=validated["name"], role=LEARNER_ROLE), None, None

    def authenticate_account(self, *, email: str | None = None, password: str, username: str | None = None) -> AuthUser | None:
        """Authenticate a durable learner account without exposing secret material."""
        raw_email = email or username or ""
        if not email and username and "@" not in username:
            raw_email = f"{str(username).strip().lower()}@legacy.local"
        normalized_email = normalize_email(raw_email)
        if normalized_email is None:
            return None
        try:
            with self._connect("auth_login") as connection:
                row = connection.execute(
                    """
                    SELECT id, username, email, name, role, password_hash, google_sub, email_verified, disabled
                    FROM users
                    WHERE email = ?
                    """,
                    (normalized_email,),
                ).fetchone()
        except sqlite3.Error as exc:
            raise StorageError(phase="auth_login", detail="Could not read account from storage.") from exc

        if row is None or bool(row["disabled"]):
            return None
        if not verify_password(password, row["password_hash"]):
            return None
        return _auth_user_from_row(row)

    def ensure_session_user(self, *, username: str, role: str, phase: str) -> AuthUser:
        """Ensure a session-authenticated user exists for legacy practice foreign keys."""
        normalized_username = _require_username(username, phase=phase)
        now = _utcnow_iso()
        email = LOCAL_ADMIN_EMAIL if normalized_username in {"local-admin", LOCAL_ADMIN_USERNAME} else f"{normalized_username}@legacy.local"
        name = "Local Admin" if normalized_username in {"local-admin", LOCAL_ADMIN_USERNAME} else None
        normalized_role = str(role or LEARNER_ROLE)
        if normalized_role == "local_admin":
            normalized_role = "admin"
        if normalized_role == "learner":
            normalized_role = LEARNER_ROLE
        try:
            with self._connect(phase) as connection:
                if normalized_username == LOCAL_ADMIN_USERNAME:
                    connection.execute("DELETE FROM users WHERE email = ? AND username != ?", (LOCAL_ADMIN_EMAIL, LOCAL_ADMIN_USERNAME))
                connection.execute(
                    """
                    INSERT INTO users (username, id, email, name, role, salt, password_hash, email_verified, disabled, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1, 0, ?, ?)
                    ON CONFLICT(username) DO NOTHING
                    """,
                    (normalized_username, normalized_username, email, name, normalized_role, token_bytes(16), token_urlsafe(24), now, now),
                )
                if normalized_username == LOCAL_ADMIN_USERNAME:
                    connection.execute(
                        "UPDATE users SET email = ?, name = ?, role = ?, email_verified = 1, disabled = 0, updated_at = ? WHERE username = ?",
                        (LOCAL_ADMIN_EMAIL, "Local Admin", "admin", now, LOCAL_ADMIN_USERNAME),
                    )
                row = connection.execute(
                    "SELECT id, username, email, name, role, password_hash, google_sub, email_verified, disabled FROM users WHERE username = ?",
                    (normalized_username,),
                ).fetchone()
        except sqlite3.Error as exc:
            raise StorageError(phase=phase, detail="Could not prepare user practice storage.") from exc
        if row is None:
            raise StorageError(phase=phase, detail="Could not read prepared user practice storage.")
        return _auth_user_from_row(row)

    def get_user_by_id(self, *, user_id: str, phase: str = "auth_session") -> AuthUser | None:
        """Return a safe user object by immutable id."""
        normalized_id = _require_username(user_id, phase=phase)
        try:
            with self._connect(phase) as connection:
                row = connection.execute(
                    "SELECT id, username, email, name, role, password_hash, google_sub, email_verified, disabled FROM users WHERE id = ? OR username = ?",
                    (normalized_id, normalized_id),
                ).fetchone()
        except sqlite3.Error as exc:
            raise StorageError(phase=phase, detail="Could not read user from storage.") from exc
        if row is None or bool(row["disabled"]):
            return None
        return _auth_user_from_row(row)

    def create_session(self, *, user_id: str, secret: str, ttl_seconds: int) -> tuple[str, str]:
        """Create an opaque server-side session and return raw token plus expiry."""
        raw_token = token_urlsafe(32)
        session_id = token_urlsafe(24)
        now = datetime.now(timezone.utc)
        expires_at = (now + _seconds_delta(ttl_seconds)).isoformat()
        try:
            with self._connect("auth_session") as connection:
                connection.execute(
                    """
                    INSERT INTO auth_sessions (id, token_hash, user_id, created_at, expires_at, revoked_at)
                    VALUES (?, ?, ?, ?, ?, NULL)
                    """,
                    (session_id, token_hash(raw_token, secret=secret), user_id, now.isoformat(), expires_at),
                )
        except sqlite3.Error as exc:
            raise StorageError(phase="auth_session", detail="Could not create session in storage.") from exc
        return raw_token, expires_at

    def user_from_session_token(self, *, raw_token: str | None, secret: str) -> AuthUser | None:
        """Resolve a raw session cookie token to a safe user object."""
        if not raw_token:
            return None
        now = _utcnow_iso()
        try:
            with self._connect("auth_session") as connection:
                row = connection.execute(
                    """
                    SELECT u.id, u.username, u.email, u.name, u.role, u.password_hash, u.google_sub, u.email_verified, u.disabled
                    FROM auth_sessions s
                    JOIN users u ON u.id = s.user_id OR u.username = s.user_id
                    WHERE s.token_hash = ? AND s.revoked_at IS NULL AND s.expires_at > ?
                    """,
                    (token_hash(raw_token, secret=secret), now),
                ).fetchone()
        except sqlite3.Error as exc:
            raise StorageError(phase="auth_session", detail="Could not resolve session from storage.") from exc
        if row is None or bool(row["disabled"]):
            return None
        return _auth_user_from_row(row)

    def revoke_session(self, *, raw_token: str | None, secret: str) -> None:
        """Revoke one current session token if present."""
        if not raw_token:
            return
        try:
            with self._connect("auth_logout") as connection:
                connection.execute(
                    "UPDATE auth_sessions SET revoked_at = ? WHERE token_hash = ? AND revoked_at IS NULL",
                    (_utcnow_iso(), token_hash(raw_token, secret=secret)),
                )
        except sqlite3.Error as exc:
            raise StorageError(phase="auth_logout", detail="Could not revoke session in storage.") from exc

    def revoke_user_sessions(self, *, user_id: str, phase: str = "auth_session") -> None:
        """Revoke all sessions for one user."""
        try:
            with self._connect(phase) as connection:
                connection.execute(
                    "UPDATE auth_sessions SET revoked_at = ? WHERE user_id = ? AND revoked_at IS NULL",
                    (_utcnow_iso(), user_id),
                )
        except sqlite3.Error as exc:
            raise StorageError(phase=phase, detail="Could not revoke user sessions in storage.") from exc

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

    def end_active_practice_session(self, *, username: str, ended_at: datetime | str | None = None) -> dict[str, Any] | None:
        """Mark the active practice session as ended and return its public record.

        Returns None when no active session exists.
        """
        normalized_username = _require_username(username, phase="practice_session")
        timestamp = _coerce_timestamp(ended_at)
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
                if row is None:
                    return None
                connection.execute(
                    "UPDATE practice_sessions SET ended_at = ? WHERE session_id = ?",
                    (timestamp, str(row["session_id"])),
                )
        except sqlite3.Error as exc:
            raise StorageError(phase="practice_session", detail="Could not end active practice session.") from exc
        return {
            "session_id": str(row["session_id"]),
            "username": str(row["username"]),
            "started_at": row["started_at"],
            "ended_at": timestamp,
        }

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
                    if lifecycle != "revision" and consecutive >= 3:
                        # Check accuracy: at least 80% across all attempts for this
                        # (username, base_card_id, direction) triple.
                        acc_row = connection.execute(
                            """SELECT COUNT(*) AS total,
                                      SUM(CASE WHEN correct = 1 THEN 1 ELSE 0 END) AS correct_count
                               FROM answer_events
                               WHERE username=? AND base_card_id=? AND direction=?""",
                            (normalized_username, normalized_base_card_id, normalized_direction),
                        ).fetchone()
                        total_attempts = int(acc_row["total"]) if acc_row else 0
                        correct_count = int(acc_row["correct_count"]) if acc_row else 0
                        accuracy = (correct_count / total_attempts) if total_attempts > 0 else 0.0
                        if accuracy >= 0.80:
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

    def list_practice_sessions(self, *, username: str, limit: int = MAX_EVENTS, phase: str = "practice_analytics") -> list[PracticeSessionRecord]:
        """Return newest bounded practice sessions in chronological order."""
        normalized_username = _require_username(username, phase=phase)
        bounded_limit = _bounded_limit(limit)
        try:
            with self._connect(phase) as connection:
                rows = connection.execute(
                    """
                    SELECT session_id, username, started_at, ended_at
                    FROM practice_sessions
                    WHERE username = ?
                    ORDER BY started_at DESC
                    LIMIT ?
                    """,
                    (normalized_username, bounded_limit),
                ).fetchall()
        except sqlite3.Error as exc:
            raise StorageError(phase=phase, detail="Could not list practice sessions.") from exc
        return [
            PracticeSessionRecord(
                session_id=str(row["session_id"]),
                username=str(row["username"]),
                started_at=str(row["started_at"]),
                ended_at=row["ended_at"],
            )
            for row in reversed(rows)
        ]

    def list_practice_lifecycle(self, *, username: str) -> list[PracticeLifecycleRecord]:
        """Return all lifecycle rows for a learner in a queue-ready shape."""
        normalized_username = _require_username(username, phase="practice_queue")
        try:
            with self._connect("practice_queue") as connection:
                rows = connection.execute(
                    """
                    SELECT username, base_card_id, direction, lifecycle,
                           first_seen_at, last_seen_at, consecutive_correct,
                           correct_session_streak, promoted_at, regression_count,
                           last_regressed_at
                    FROM practice_lifecycle
                    WHERE username = ?
                    """,
                    (normalized_username,),
                ).fetchall()
        except sqlite3.Error as exc:
            raise StorageError(phase="practice_queue", detail="Could not list practice lifecycle rows.") from exc
        return [
            PracticeLifecycleRecord(
                username=str(row["username"]),
                base_card_id=str(row["base_card_id"]),
                direction=str(row["direction"]),
                lifecycle=str(row["lifecycle"]),
                first_seen_at=str(row["first_seen_at"]),
                last_seen_at=str(row["last_seen_at"]),
                correct_streak=int(row["consecutive_correct"]),
                session_streak=int(row["correct_session_streak"]),
                promoted_at=row["promoted_at"],
                regression_count=int(row["regression_count"]),
                last_regressed_at=row["last_regressed_at"],
            )
            for row in rows
        ]

    def exposure_summary(self, *, username: str) -> dict[str, int]:
        """Return shown-card exposure counts keyed by '<base_card_id>#<direction>'."""
        normalized_username = _require_username(username, phase="practice_queue")
        try:
            with self._connect("practice_queue") as connection:
                rows = connection.execute(
                    """
                    SELECT base_card_id, direction, COUNT(*) AS shown_count
                    FROM shown_cards
                    WHERE username = ?
                    GROUP BY base_card_id, direction
                    """,
                    (normalized_username,),
                ).fetchall()
        except sqlite3.Error as exc:
            raise StorageError(phase="practice_queue", detail="Could not summarize shown-card exposure.") from exc
        return {f"{row['base_card_id']}#{row['direction']}": int(row["shown_count"]) for row in rows}

    def list_answer_events(
        self, *, username: str, limit: int | None = MAX_EVENTS, phase: str = "practice_progress"
    ) -> list[AnswerEventRecord]:
        """Return answer events in chronological order, skipping malformed rows.

        When limit is None, returns full learner history.
        """
        normalized_username = _require_username(username, phase=phase)
        try:
            with self._connect(phase) as connection:
                if limit is None:
                    rows = connection.execute(
                        """
                        SELECT username, card_id, base_card_id, direction, card_type,
                               submitted_answer, expected_answer, correct, answered_at
                        FROM answer_events
                        WHERE username = ?
                        ORDER BY answered_at DESC, id DESC
                        """,
                        (normalized_username,),
                    ).fetchall()
                else:
                    bounded_limit = _bounded_limit(limit)
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

    def practice_summary(self, *, username: str, phase: str = "practice_summary") -> dict[str, Any]:
        """Return fast dashboard metrics without expanding all practice cards.

        mastered_count reflects cards where is_mastered=True:
          - lifecycle='revision', OR
          - lifecycle='active' with consecutive_correct >= 3 AND accuracy >= 0.80
        This is identical to build_practice_analytics() so both endpoints agree.
        """
        normalized_username = _require_username(username, phase=phase)
        try:
            with self._connect(phase) as connection:
                totals = connection.execute(
                    """
                    SELECT COUNT(*) AS event_count,
                           COALESCE(SUM(CASE WHEN correct THEN 1 ELSE 0 END), 0) AS correct_count,
                           MAX(answered_at) AS latest_answered_at
                    FROM answer_events
                    WHERE username = ?
                    """,
                    (normalized_username,),
                ).fetchone()
                day_rows = connection.execute(
                    """
                    SELECT DISTINCT substr(answered_at, 1, 10) AS practiced_day
                    FROM answer_events
                    WHERE username = ? AND answered_at IS NOT NULL
                    ORDER BY practiced_day DESC
                    """,
                    (normalized_username,),
                ).fetchall()
                # Per-(base_card_id, direction) aggregates for accuracy + final streak.
                # Only covers cards that have had at least one answer event.
                agg_rows = connection.execute(
                    """
                    SELECT
                        base_card_id,
                        direction,
                        COUNT(*) AS attempts,
                        SUM(CASE WHEN correct THEN 1 ELSE 0 END) AS correct,
                        MAX(id) AS last_id
                    FROM answer_events
                    WHERE username = ?
                    GROUP BY base_card_id, direction
                    """,
                    (normalized_username,),
                ).fetchall()
                # Fetch full lifecycle rows to check consecutive_correct + lifecycle state
                # for every card, including those with zero events.
                lifecycle_rows = connection.execute(
                    """
                    SELECT base_card_id, direction, lifecycle, consecutive_correct
                    FROM practice_lifecycle
                    WHERE username = ?
                    """,
                    (normalized_username,),
                ).fetchall()
        except sqlite3.Error as exc:
            raise StorageError(phase=phase, detail="Could not build practice summary.") from exc

        event_count = int(totals["event_count"] or 0) if totals else 0
        correct_count = int(totals["correct_count"] or 0) if totals else 0
        streak = _practice_day_streak([str(row["practiced_day"] or "") for row in day_rows])

        # Build per-card aggregate lookup keyed by (base_card_id, direction).
        agg: dict[tuple[str, str], dict[str, int]] = {
            (str(r["base_card_id"]), str(r["direction"])): {
                "attempts": int(r["attempts"]),
                "correct": int(r["correct"]),
            }
            for r in agg_rows
        }

        # Compute is_mastered for each lifecycle row, matching build_practice_analytics.
        mastered_count = 0
        active_count = 0
        for row in lifecycle_rows:
            lc = str(row["lifecycle"] or "active").lower()
            consecutive = int(row["consecutive_correct"] or 0)
            if lc == "revision":
                mastered_count += 1
            else:
                # Check scheduler mastery criteria: consecutive_correct >= 3 AND accuracy >= 80%.
                stats = agg.get((str(row["base_card_id"]), str(row["direction"])))
                if stats and stats["attempts"] > 0:
                    accuracy = stats["correct"] / stats["attempts"]
                    if consecutive >= 3 and accuracy >= 0.80:
                        mastered_count += 1
                    else:
                        active_count += 1
                else:
                    active_count += 1

        return {
            "ok": True,
            "phase": "practice_summary",
            "event_count": event_count,
            "total": event_count,
            "correct": correct_count,
            "incorrect": max(0, event_count - correct_count),
            "accuracy": None if event_count == 0 else round(correct_count / event_count, 4),
            "latest_event_at": str(totals["latest_answered_at"] or "") if totals else "",
            "streak": streak,
            "mastered_count": mastered_count,
            "active_count": active_count,
            "lifecycle_count": len(lifecycle_rows),
        }

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
                    SELECT username, theme, tts_speed, tts_autoplay, sfx_enabled, sfx_mode, voice_id
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
            sfx_mode=str(row["sfx_mode"] or ("on_answer" if bool(row["sfx_enabled"]) else "off")),
            voice_id=str(row["voice_id"] or DEFAULT_VOICE_ID),
        )

    def upsert_user_settings(self, *, username: str, theme: str, tts_speed: float, tts_autoplay: bool = True, sfx_enabled: bool = True, sfx_mode: str | None = None) -> UserSettingsRecord:
        """Create or update durable learner settings for supported theme/speed values."""
        normalized_username = _require_username(username, phase="settings_update")
        normalized_theme = _require_theme(theme, phase="settings_update")
        normalized_speed = _require_tts_speed(tts_speed, phase="settings_update")
        normalized_tts_autoplay = bool(tts_autoplay)
        normalized_sfx_enabled = bool(sfx_enabled)
        normalized_sfx_mode = _require_sfx_mode(sfx_mode if sfx_mode is not None else ("on_answer" if normalized_sfx_enabled else "off"), phase="settings_update")
        if not normalized_sfx_enabled and normalized_sfx_mode in {"all", "on_answer"}:
            normalized_sfx_mode = "off"
        try:
            with self._connect("settings_update") as connection:
                self._ensure_user_settings_row(connection, normalized_username)
                connection.execute(
                    """
                    UPDATE user_settings
                    SET theme = ?, tts_speed = ?, tts_autoplay = ?, sfx_enabled = ?, sfx_mode = ?, voice_id = ?
                    WHERE username = ?
                    """,
                    (normalized_theme, normalized_speed, 1 if normalized_tts_autoplay else 0, 1 if normalized_sfx_enabled else 0, normalized_sfx_mode, DEFAULT_VOICE_ID, normalized_username),
                )
        except sqlite3.Error as exc:
            raise StorageError(phase="settings_update", detail="Could not update settings.") from exc
        return UserSettingsRecord(
            username=normalized_username,
            theme=normalized_theme,
            tts_speed=normalized_speed,
            tts_autoplay=normalized_tts_autoplay,
            sfx_enabled=normalized_sfx_enabled,
            sfx_mode=normalized_sfx_mode,
            voice_id=DEFAULT_VOICE_ID,
        )

    def create_password_reset_token(self, *, email: str, secret: str, ttl_seconds: int) -> str | None:
        """Create a short-lived reset token for an existing active local account."""
        normalized_email = normalize_email(email)
        if normalized_email is None:
            return None
        raw_token = token_urlsafe(32)
        now = datetime.now(timezone.utc)
        expires_at = (now + _seconds_delta(ttl_seconds)).isoformat()
        try:
            with self._connect("password_reset_request") as connection:
                row = connection.execute("SELECT id, username, disabled FROM users WHERE email = ?", (normalized_email,)).fetchone()
                if row is None or bool(row["disabled"]):
                    return None
                connection.execute(
                    """
                    INSERT INTO password_reset_tokens (id, token_hash, user_id, created_at, expires_at, used_at)
                    VALUES (?, ?, ?, ?, ?, NULL)
                    """,
                    (token_urlsafe(18), token_hash(raw_token, secret=secret), str(row["id"] or row["username"]), now.isoformat(), expires_at),
                )
        except sqlite3.Error as exc:
            raise StorageError(phase="password_reset_request", detail="Could not create password reset token.") from exc
        return raw_token

    def reset_password_with_token(self, *, raw_token: str, new_password: str, secret: str) -> AuthUser | None:
        """Consume one reset token and update the user's password hash."""
        now = _utcnow_iso()
        try:
            with self._connect("password_reset_confirm") as connection:
                row = connection.execute(
                    """
                    SELECT t.id AS token_id, t.user_id, u.id, u.username, u.email, u.name, u.role, u.password_hash, u.google_sub, u.email_verified, u.disabled
                    FROM password_reset_tokens t
                    JOIN users u ON u.id = t.user_id OR u.username = t.user_id
                    WHERE t.token_hash = ? AND t.used_at IS NULL AND t.expires_at > ?
                    """,
                    (token_hash(raw_token, secret=secret), now),
                ).fetchone()
                if row is None or bool(row["disabled"]):
                    return None
                user_id = str(row["id"] or row["username"])
                connection.execute("UPDATE password_reset_tokens SET used_at = ? WHERE id = ?", (now, row["token_id"]))
                connection.execute("UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ? OR username = ?", (hash_password(new_password), now, user_id, user_id))
                connection.execute("UPDATE auth_sessions SET revoked_at = ? WHERE user_id = ? AND revoked_at IS NULL", (now, user_id))
        except sqlite3.Error as exc:
            raise StorageError(phase="password_reset_confirm", detail="Could not reset password in storage.") from exc
        return self.get_user_by_id(user_id=user_id, phase="password_reset_confirm")

    def create_oauth_state(self, *, state: str, secret: str, ttl_seconds: int, next_path: str = "/") -> None:
        """Persist a single-use OAuth state token hash."""
        now = datetime.now(timezone.utc)
        try:
            with self._connect("auth_google_login") as connection:
                connection.execute(
                    "INSERT INTO oauth_states (state_hash, created_at, expires_at, used_at, next_path) VALUES (?, ?, ?, NULL, ?)",
                    (token_hash(state, secret=secret), now.isoformat(), (now + _seconds_delta(ttl_seconds)).isoformat(), next_path or "/"),
                )
        except sqlite3.Error as exc:
            raise StorageError(phase="auth_google_login", detail="Could not create OAuth state.") from exc

    def consume_oauth_state(self, *, state: str, secret: str) -> str | None:
        """Consume a Google OAuth state token and return the intended next path."""
        now = _utcnow_iso()
        try:
            with self._connect("auth_google_callback") as connection:
                row = connection.execute(
                    "SELECT state_hash, next_path FROM oauth_states WHERE state_hash = ? AND used_at IS NULL AND expires_at > ?",
                    (token_hash(state, secret=secret), now),
                ).fetchone()
                if row is None:
                    return None
                connection.execute("UPDATE oauth_states SET used_at = ? WHERE state_hash = ?", (now, row["state_hash"]))
                return str(row["next_path"] or "/")
        except sqlite3.Error as exc:
            raise StorageError(phase="auth_google_callback", detail="Could not consume OAuth state.") from exc

    def upsert_google_user(self, *, email: str, google_sub: str, name: str | None, email_verified: bool) -> AuthUser:
        """Create or link a Google identity to a local user."""
        normalized_email = normalize_email(email)
        if normalized_email is None or not google_sub:
            raise StorageError(phase="auth_google_callback", detail="Google account did not provide a usable email.", error="invalid_google_profile")
        now = _utcnow_iso()
        try:
            with self._connect("auth_google_callback") as connection:
                row = connection.execute(
                    "SELECT id, username, email, name, role, password_hash, google_sub, email_verified, disabled FROM users WHERE google_sub = ?",
                    (google_sub,),
                ).fetchone()
                if row is None:
                    row = connection.execute(
                        "SELECT id, username, email, name, role, password_hash, google_sub, email_verified, disabled FROM users WHERE email = ?",
                        (normalized_email,),
                    ).fetchone()
                    if row is None:
                        user_id = _new_user_id()
                        connection.execute(
                            """
                            INSERT INTO users (username, id, email, name, role, password_hash, google_sub, email_verified, disabled, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, NULL, ?, ?, 0, ?, ?)
                            """,
                            (user_id, user_id, normalized_email, str(name or "").strip() or None, LEARNER_ROLE, google_sub, 1 if email_verified else 0, now, now),
                        )
                        row = connection.execute(
                            "SELECT id, username, email, name, role, password_hash, google_sub, email_verified, disabled FROM users WHERE id = ?",
                            (user_id,),
                        ).fetchone()
                    elif not row["google_sub"]:
                        connection.execute(
                            "UPDATE users SET google_sub = ?, email_verified = CASE WHEN ? THEN 1 ELSE email_verified END, updated_at = ? WHERE username = ?",
                            (google_sub, 1 if email_verified else 0, now, row["username"]),
                        )
                        row = connection.execute(
                            "SELECT id, username, email, name, role, password_hash, google_sub, email_verified, disabled FROM users WHERE username = ?",
                            (row["username"],),
                        ).fetchone()
        except sqlite3.Error as exc:
            raise StorageError(phase="auth_google_callback", detail="Could not upsert Google account.") from exc
        if row is None or bool(row["disabled"]):
            raise StorageError(phase="auth_google_callback", detail="Google account is disabled.", error="disabled_user")
        return _auth_user_from_row(row)

    def delete_user_account(self, *, username: str | None = None, user_id: str | None = None) -> bool:
        """Delete a learner account and owned rows via foreign-key cascades."""
        normalized_username = _require_username(user_id or username or "", phase="account_delete")
        if normalized_username in {LOCAL_ADMIN_USERNAME, "local-admin"}:
            raise StorageError(
                phase="account_delete",
                detail="The local admin account cannot be deleted.",
                error="protected_account",
            )
        try:
            with self._connect("account_delete") as connection:
                connection.execute(
                    "UPDATE auth_sessions SET revoked_at = ? WHERE user_id = ? AND revoked_at IS NULL",
                    (_utcnow_iso(), normalized_username),
                )
                deleted = connection.execute(
                    "DELETE FROM users WHERE username = ? OR id = ?",
                    (normalized_username, normalized_username),
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
                        id TEXT UNIQUE,
                        email TEXT UNIQUE,
                        name TEXT,
                        role TEXT NOT NULL DEFAULT 'user' CHECK(role IN ('admin', 'test_user', 'user')),
                        salt BLOB,
                        password_hash TEXT,
                        google_sub TEXT UNIQUE,
                        email_verified INTEGER NOT NULL DEFAULT 0 CHECK(email_verified IN (0, 1)),
                        disabled INTEGER NOT NULL DEFAULT 0 CHECK(disabled IN (0, 1)),
                        created_at TEXT NOT NULL,
                        updated_at TEXT
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

                    CREATE TABLE IF NOT EXISTS auth_sessions (
                        id TEXT PRIMARY KEY,
                        token_hash TEXT NOT NULL UNIQUE,
                        user_id TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        expires_at TEXT NOT NULL,
                        revoked_at TEXT,
                        FOREIGN KEY(user_id) REFERENCES users(username) ON DELETE CASCADE
                    );

                    CREATE TABLE IF NOT EXISTS password_reset_tokens (
                        id TEXT PRIMARY KEY,
                        token_hash TEXT NOT NULL UNIQUE,
                        user_id TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        expires_at TEXT NOT NULL,
                        used_at TEXT,
                        FOREIGN KEY(user_id) REFERENCES users(username) ON DELETE CASCADE
                    );

                    CREATE TABLE IF NOT EXISTS oauth_states (
                        state_hash TEXT PRIMARY KEY,
                        created_at TEXT NOT NULL,
                        expires_at TEXT NOT NULL,
                        used_at TEXT,
                        next_path TEXT NOT NULL DEFAULT '/'
                    );

                    CREATE INDEX IF NOT EXISTS idx_auth_sessions_hash ON auth_sessions(token_hash);
                    CREATE INDEX IF NOT EXISTS idx_auth_sessions_user ON auth_sessions(user_id);
                    """
                )
                _ensure_column(connection, "shown_cards", "prompt_language", "TEXT NOT NULL DEFAULT ''")
                _ensure_column(connection, "shown_cards", "answer_language", "TEXT NOT NULL DEFAULT ''")
                _ensure_column(connection, "user_settings", "tts_autoplay", "INTEGER NOT NULL DEFAULT 1 CHECK(tts_autoplay IN (0, 1))")
                _ensure_column(connection, "user_settings", "sfx_enabled", "INTEGER NOT NULL DEFAULT 1 CHECK(sfx_enabled IN (0, 1))")
                _ensure_column(connection, "user_settings", "sfx_mode", "TEXT NOT NULL DEFAULT 'on_answer' CHECK(sfx_mode IN ('all', 'on_answer', 'ui_only', 'off'))")
                _ensure_column(connection, "user_settings", "voice_id", "TEXT NOT NULL DEFAULT 'de6'")
                _ensure_column(connection, "users", "id", "TEXT")
                _ensure_column(connection, "users", "email", "TEXT")
                _ensure_column(connection, "users", "name", "TEXT")
                _ensure_column(connection, "users", "google_sub", "TEXT")
                _ensure_column(connection, "users", "email_verified", "INTEGER NOT NULL DEFAULT 0 CHECK(email_verified IN (0, 1))")
                _ensure_column(connection, "users", "disabled", "INTEGER NOT NULL DEFAULT 0 CHECK(disabled IN (0, 1))")
                _ensure_column(connection, "users", "updated_at", "TEXT")
                _ensure_users_password_columns_nullable(connection)
                _ensure_users_auth_columns(connection)
                _ensure_user_settings_sfx_mode_accepts_ui_only(connection)
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


def _new_user_id() -> str:
    return f"usr_{token_urlsafe(18)}"


def _seconds_delta(seconds: int) -> timedelta:
    return timedelta(seconds=max(1, int(seconds)))


def _auth_user_from_row(row: sqlite3.Row) -> AuthUser:
    user_id = str(row["id"] or row["username"])
    email = str(row["email"] or f"{user_id}@legacy.local")
    role = str(row["role"] or LEARNER_ROLE)
    if role == "learner":
        role = LEARNER_ROLE
    return AuthUser(
        id=user_id,
        email=email,
        name=str(row["name"]) if row["name"] is not None else None,
        role=role,
        email_verified=bool(row["email_verified"]),
        disabled=bool(row["disabled"]),
        google_sub=str(row["google_sub"]) if row["google_sub"] is not None else None,
    )


def _ensure_users_auth_columns(connection: sqlite3.Connection) -> None:
    now = _utcnow_iso()
    rows = connection.execute("SELECT username, id, email, role, updated_at FROM users").fetchall()
    for row in rows:
        username = str(row["username"])
        user_id = str(row["id"] or username)
        email = row["email"]
        role = str(row["role"] or LEARNER_ROLE)
        if role == "learner":
            role = LEARNER_ROLE
        if email is None:
            email = username if normalize_email(username) else f"{username}@legacy.local"
        connection.execute(
            "UPDATE users SET id = ?, email = ?, role = ?, updated_at = COALESCE(updated_at, ?) WHERE username = ?",
            (user_id, str(email).lower(), role, now, username),
        )
    connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_id ON users(id)")
    connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_google_sub ON users(google_sub)")

def _ensure_users_password_columns_nullable(connection: sqlite3.Connection) -> None:
    """Relax legacy NOT NULL password columns so OAuth-only users can exist."""
    columns = connection.execute("PRAGMA table_info(users)").fetchall()
    not_null_by_name = {str(row[1]): bool(row[3]) for row in columns}
    if not not_null_by_name.get("salt", False) and not not_null_by_name.get("password_hash", False):
        return

    connection.execute("PRAGMA foreign_keys = OFF")
    try:
        connection.executescript(
            """
            CREATE TABLE users_new (
                username TEXT PRIMARY KEY,
                id TEXT UNIQUE,
                email TEXT UNIQUE,
                name TEXT,
                role TEXT NOT NULL DEFAULT 'user' CHECK(role IN ('admin', 'test_user', 'user')),
                salt BLOB,
                password_hash TEXT,
                google_sub TEXT UNIQUE,
                email_verified INTEGER NOT NULL DEFAULT 0 CHECK(email_verified IN (0, 1)),
                disabled INTEGER NOT NULL DEFAULT 0 CHECK(disabled IN (0, 1)),
                created_at TEXT NOT NULL,
                updated_at TEXT
            );
            INSERT INTO users_new (username, id, email, name, role, salt, password_hash, google_sub, email_verified, disabled, created_at, updated_at)
            SELECT username, id, email, name, role, salt, password_hash, google_sub, email_verified, disabled, created_at, updated_at
            FROM users;
            DROP TABLE users;
            ALTER TABLE users_new RENAME TO users;
            CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
            """
        )
    finally:
        connection.execute("PRAGMA foreign_keys = ON")


def _ensure_column(connection: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    existing = {str(row[1]) for row in connection.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in existing:
        connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def _ensure_user_settings_sfx_mode_accepts_ui_only(connection: sqlite3.Connection) -> None:
    row = connection.execute("SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'user_settings'").fetchone()
    table_sql = str(row[0] if row else "")
    if "ui_only" in table_sql:
        return

    connection.executescript(
        """
        ALTER TABLE user_settings RENAME TO user_settings_old;
        CREATE TABLE user_settings (
            username TEXT PRIMARY KEY,
            theme TEXT NOT NULL DEFAULT 'system' CHECK(theme IN ('light', 'dark', 'system')),
            tts_speed REAL NOT NULL DEFAULT 0.8 CHECK(tts_speed > 0 AND tts_speed <= 2.0),
            voice_id TEXT NOT NULL DEFAULT 'de6',
            tts_autoplay INTEGER NOT NULL DEFAULT 1 CHECK(tts_autoplay IN (0, 1)),
            sfx_enabled INTEGER NOT NULL DEFAULT 1 CHECK(sfx_enabled IN (0, 1)),
            sfx_mode TEXT NOT NULL DEFAULT 'on_answer' CHECK(sfx_mode IN ('all', 'on_answer', 'ui_only', 'off')),
            FOREIGN KEY(username) REFERENCES users(username) ON DELETE CASCADE
        );
        INSERT INTO user_settings (username, theme, tts_speed, voice_id, tts_autoplay, sfx_enabled, sfx_mode)
        SELECT username, theme, tts_speed, voice_id, tts_autoplay, sfx_enabled, sfx_mode
        FROM user_settings_old;
        DROP TABLE user_settings_old;
        """
    )


def _email_unavailable_payload() -> dict[str, Any]:
    return {
        "authenticated": False,
        "error": "email_unavailable",
        "phase": "auth_register",
        "detail": "Email is already registered.",
    }


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


def _require_sfx_mode(sfx_mode: str, *, phase: str) -> str:
    normalized = str(sfx_mode or "").strip().lower()
    if normalized not in {"all", "on_answer", "ui_only", "off"}:
        raise StorageError(phase=phase, detail="SFX mode must be one of: all, on_answer, ui_only, off.", error="invalid_sfx_mode")
    return normalized


def _practice_day_streak(day_values: list[str], *, today: datetime | None = None) -> dict[str, Any]:
    days = set()
    for value in day_values:
        try:
            days.add(datetime.fromisoformat(str(value)[:10]).date())
        except Exception:
            continue
    if not days:
        return {"current_days": 0, "best_days": 0, "trajectory": []}

    current_date = (today or datetime.now(timezone.utc)).date()
    latest_allowed = current_date if current_date in days else current_date - timedelta(days=1)
    current_streak = 0
    cursor = latest_allowed
    while cursor in days:
        current_streak += 1
        cursor -= timedelta(days=1)

    best_streak = 0
    run = 0
    previous = None
    for day in sorted(days):
        if previous is not None and (day - previous).days == 1:
            run += 1
        else:
            run = 1
        best_streak = max(best_streak, run)
        previous = day

    return {
        "current_days": current_streak,
        "best_days": best_streak,
        "trajectory": [day.isoformat() for day in sorted(days)],
    }


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
