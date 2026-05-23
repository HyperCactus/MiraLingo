"""Authentication primitives for the MiraLingo web application."""

from __future__ import annotations

from dataclasses import dataclass
from secrets import compare_digest
from typing import Any

from .config import Settings

LOCAL_ADMIN_USERNAME = "admin"
LOCAL_ADMIN_PASSWORD = "admin"
SESSION_USER_KEY = "user"


@dataclass(frozen=True)
class AuthUser:
    """Authenticated user state stored in the signed session cookie."""

    username: str
    role: str = "admin"

    def public_dict(self) -> dict[str, str]:
        """Return a password-free user representation for JSON responses."""
        return {"username": self.username, "role": self.role}


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
