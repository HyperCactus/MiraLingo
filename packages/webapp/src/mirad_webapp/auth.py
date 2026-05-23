"""Authentication primitives for the MiraLingo web application."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from secrets import compare_digest, token_bytes
from typing import Any

from .config import Settings

LOCAL_ADMIN_USERNAME = "admin"
LOCAL_ADMIN_PASSWORD = "admin"
SESSION_USER_KEY = "user"
LEARNER_ROLE = "learner"
_MIN_USERNAME_LENGTH = 3
_MIN_PASSWORD_LENGTH = 8
_PBKDF2_ITERATIONS = 200_000


@dataclass(frozen=True)
class AuthUser:
    """Authenticated user state stored in the signed session cookie."""

    username: str
    role: str = "admin"

    def public_dict(self) -> dict[str, str]:
        """Return a password-free user representation for JSON responses."""
        return {"username": self.username, "role": self.role}


@dataclass(frozen=True)
class StoredAccount:
    """Password-hash-only account record held in the process-local store."""

    username: str
    role: str
    salt: bytes
    password_hash: bytes


class AccountStore:
    """Small process-local learner account store for S07 tests and dev sessions.

    The store is intentionally non-durable and O(1) by normalized username. S08
    is responsible for replacing it with SQLite persistence.
    """

    def __init__(self) -> None:
        self._accounts: dict[str, StoredAccount] = {}

    def register(
        self, *, username: str, password: str
    ) -> tuple[AuthUser | None, dict[str, Any] | None, int | None]:
        """Register a learner account or return a structured auth error."""
        normalized_username, validation_error, validation_status = validate_registration_inputs(
            username=username,
            password=password,
        )
        if normalized_username is None:
            return None, validation_error, validation_status

        if normalized_username in self._accounts:
            return (
                None,
                {
                    "authenticated": False,
                    "error": "username_unavailable",
                    "phase": "auth_register",
                    "detail": "Username is already registered.",
                },
                409,
            )

        salt = token_bytes(16)
        account = StoredAccount(
            username=normalized_username,
            role=LEARNER_ROLE,
            salt=salt,
            password_hash=_hash_password(password=password, salt=salt),
        )
        self._accounts[normalized_username] = account
        return AuthUser(username=account.username, role=account.role), None, None

    def authenticate(self, *, username: str, password: str) -> AuthUser | None:
        """Authenticate a registered learner without exposing secret material."""
        normalized_username = normalize_username(username)
        if normalized_username is None:
            return None
        account = self._accounts.get(normalized_username)
        if account is None:
            return None
        candidate_hash = _hash_password(password=password, salt=account.salt)
        if not compare_digest(candidate_hash, account.password_hash):
            return None
        return AuthUser(username=account.username, role=account.role)


def normalize_username(username: str) -> str | None:
    """Normalize a username for case-insensitive lookup, rejecting blank values."""
    normalized = username.strip().lower()
    return normalized or None


def validate_registration_inputs(
    *, username: str, password: str
) -> tuple[str | None, dict[str, Any] | None, int | None]:
    """Validate the S07 username/password policy for self-service registration."""
    normalized_username = normalize_username(username)
    if normalized_username is None or len(normalized_username) < _MIN_USERNAME_LENGTH:
        return (
            None,
            {
                "authenticated": False,
                "error": "invalid_username",
                "phase": "auth_register",
                "detail": f"Username must be at least {_MIN_USERNAME_LENGTH} characters.",
            },
            400,
        )
    if normalized_username == LOCAL_ADMIN_USERNAME:
        return (
            None,
            {
                "authenticated": False,
                "error": "reserved_username",
                "phase": "auth_register",
                "detail": "The admin username is reserved.",
            },
            400,
        )
    if len(password) < _MIN_PASSWORD_LENGTH:
        return (
            None,
            {
                "authenticated": False,
                "error": "invalid_password",
                "phase": "auth_register",
                "detail": f"Password must be at least {_MIN_PASSWORD_LENGTH} characters.",
            },
            400,
        )
    return normalized_username, None, None


def registered_login_error() -> tuple[dict[str, Any], int]:
    """Return the stable learner-login invalid credentials payload."""
    return (
        {
            "authenticated": False,
            "error": "invalid_credentials",
            "phase": "auth_login",
            "detail": "Invalid username or password.",
        },
        401,
    )


def _hash_password(*, password: str, salt: bytes) -> bytes:
    """Hash one password with a per-account salt using stdlib PBKDF2-HMAC."""
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        _PBKDF2_ITERATIONS,
    )


def authenticate_local_admin(
    *, username: str, password: str, settings: Settings
) -> tuple[AuthUser | None, dict[str, Any] | None, int | None]:
    """Authenticate the development-only local admin.

    Returns (user, error_payload, status_code). Error payloads are structured
    and intentionally avoid echoing credentials.
    """
    if not settings.local_admin_bootstrap_enabled:
        return (
            None,
            {
                "authenticated": False,
                "error": "local_admin_disabled",
                "detail": "Local admin bootstrap is disabled for this environment.",
            },
            403,
        )

    valid_username = compare_digest(username, LOCAL_ADMIN_USERNAME)
    valid_password = compare_digest(password, LOCAL_ADMIN_PASSWORD)
    if not (valid_username and valid_password):
        return (
            None,
            {
                "authenticated": False,
                "error": "invalid_credentials",
                "detail": "Invalid username or password.",
            },
            401,
        )

    return AuthUser(username=LOCAL_ADMIN_USERNAME), None, None


def serialize_user(user: AuthUser) -> dict[str, str]:
    """Serialize user state for storage in the signed session."""
    return user.public_dict()


def user_from_session(value: Any) -> AuthUser | None:
    """Parse password-free user state from a session value."""
    if not isinstance(value, dict):
        return None
    username = value.get("username")
    role = value.get("role", "admin")
    if not isinstance(username, str) or not username:
        return None
    if not isinstance(role, str) or not role:
        return None
    return AuthUser(username=username, role=role)
