"""Authentication primitives for the MiraLingo web application."""

from __future__ import annotations

import base64
import hashlib
import hmac
import re
from dataclasses import dataclass
from secrets import compare_digest, token_bytes, token_urlsafe
from typing import Any

import bcrypt

from .config import Settings

LOCAL_ADMIN_EMAIL = "admin@local.miralingo"
LOCAL_ADMIN_USERNAME = "admin"
LOCAL_ADMIN_PASSWORD = "admin"
ADMIN_ACCOUNT_EMAIL = "sampollard888@gmail.com"
ADMIN_ROLE = "admin"
TEST_USER_ROLE = "test_user"
USER_ROLE = "user"
LEARNER_ROLE = USER_ROLE
SUPPORTED_ROLES = {ADMIN_ROLE, TEST_USER_ROLE, USER_ROLE}
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class AuthUser:
    """Authenticated user state resolved server-side from an opaque session."""

    id: str
    email: str
    role: str = USER_ROLE
    name: str | None = None
    email_verified: bool = False
    disabled: bool = False
    google_sub: str | None = None

    @property
    def username(self) -> str:
        """Compatibility key for legacy practice/storage tables."""
        return self.id

    def public_dict(self) -> dict[str, Any]:
        """Return a password-free user representation for JSON responses."""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "role": self.role,
            "email_verified": self.email_verified,
        }


def normalize_email(email: str) -> str | None:
    """Normalize an email address for case-insensitive account lookup."""
    normalized = str(email or "").strip().lower()
    if not normalized or not _EMAIL_RE.match(normalized):
        return None
    return normalized


def normalize_username(username: str) -> str | None:
    """Legacy compatibility: normalize historical username input."""
    normalized = str(username or "").strip().lower()
    return normalized or None


def validate_registration_inputs(
    *, email: str | None = None, password: str, name: str | None = None, username: str | None = None
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, int | None]:
    """Validate self-service email/password registration."""
    raw_email = email or username or ""
    if not email and username and "@" not in username:
        raw_email = f"{str(username).strip().lower()}@legacy.local"
    normalized_email = normalize_email(raw_email)
    if normalized_email is None:
        return (
            None,
            {
                "authenticated": False,
                "error": "invalid_email",
                "phase": "auth_register",
                "detail": "A valid email address is required.",
            },
            400,
        )
    if not email and username and str(username).strip().lower() == LOCAL_ADMIN_USERNAME:
        return (
            None,
            {
                "authenticated": False,
                "error": "reserved_email",
                "phase": "auth_register",
                "detail": "The local admin email is reserved.",
            },
            400,
        )
    if normalized_email == LOCAL_ADMIN_EMAIL:
        return (
            None,
            {
                "authenticated": False,
                "error": "reserved_email",
                "phase": "auth_register",
                "detail": "The local admin email is reserved.",
            },
            400,
        )
    password_error, password_status = validate_password(password=password, phase="auth_register")
    if password_error is not None:
        return None, password_error, password_status
    display_name = str(name or "").strip() or None
    return {"email": normalized_email, "name": display_name}, None, None


def validate_password(*, password: str, phase: str) -> tuple[dict[str, Any] | None, int | None]:
    """Validate password length without echoing credential material."""
    length = len(password or "")
    if length < MIN_PASSWORD_LENGTH or length > MAX_PASSWORD_LENGTH:
        return (
            {
                "authenticated": False,
                "error": "invalid_password",
                "phase": phase,
                "detail": f"Password must be {MIN_PASSWORD_LENGTH} to {MAX_PASSWORD_LENGTH} characters.",
            },
            400,
        )
    return None, None


def registered_login_error() -> tuple[dict[str, Any], int]:
    """Return the stable learner-login invalid credentials payload."""
    return (
        {
            "authenticated": False,
            "error": "invalid_credentials",
            "phase": "auth_login",
            "detail": "Invalid email or password.",
        },
        401,
    )


def hash_password(password: str) -> str:
    """Hash one password with bcrypt. The encoded hash includes salt and cost."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(password: str, password_hash: str | bytes | None) -> bool:
    """Verify a password against a bcrypt hash without exposing secret material."""
    if not password_hash:
        return False
    encoded_hash = password_hash if isinstance(password_hash, bytes) else str(password_hash).encode("utf-8")
    try:
        return bcrypt.checkpw(password.encode("utf-8"), encoded_hash)
    except ValueError:
        return False


def _hash_password(*, password: str, salt: bytes) -> bytes:
    """Legacy PBKDF2 helper retained so old imports/tests do not break."""
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)


def new_public_token() -> str:
    """Return a URL-safe raw token for sessions or password reset links."""
    return token_urlsafe(32)


def token_hash(token: str, *, secret: str) -> str:
    """Hash a raw bearer token before storing it server-side."""
    digest = hmac.new(secret.encode("utf-8"), token.encode("utf-8"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def authenticate_local_admin(
    *, email: str | None = None, username: str | None = None, password: str, settings: Settings
) -> tuple[AuthUser | None, dict[str, Any] | None, int | None]:
    """Authenticate the explicitly development-only local admin."""
    if not settings.local_admin_bootstrap_enabled:
        return (
            None,
            {
                "authenticated": False,
                "error": "local_admin_disabled",
                "phase": "auth_login",
                "detail": "Local admin bootstrap is disabled for this environment.",
            },
            403,
        )

    candidate = (email or username or "").strip().lower()
    valid_identity = compare_digest(candidate, LOCAL_ADMIN_EMAIL) or compare_digest(candidate, LOCAL_ADMIN_USERNAME)
    valid_password = compare_digest(password, LOCAL_ADMIN_PASSWORD)
    if not (valid_identity and valid_password):
        return (
            None,
            {
                "authenticated": False,
                "error": "invalid_credentials",
                "phase": "auth_login",
                "detail": "Invalid email or password.",
            },
            401,
        )

    return AuthUser(id=LOCAL_ADMIN_USERNAME, email=LOCAL_ADMIN_EMAIL, name="Local Admin", role=ADMIN_ROLE, email_verified=True), None, None


def has_any_role(user: AuthUser, roles: set[str] | tuple[str, ...] | list[str]) -> bool:
    """Return whether a resolved user has one of the allowed roles."""
    return user.role in set(roles)


def serialize_user(user: AuthUser) -> dict[str, Any]:
    """Return safe user fields. Not used for session storage."""
    return user.public_dict()


def user_from_session(value: Any) -> AuthUser | None:
    """No-op legacy parser; sessions are now opaque and server-side."""
    return None
