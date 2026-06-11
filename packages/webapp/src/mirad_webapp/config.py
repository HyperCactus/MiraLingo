"""Runtime configuration for the MiraLingo web application."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv


load_dotenv()


_TRUE_VALUES = {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """Process-local settings used by the FastAPI app."""

    environment: str = "development"
    enable_local_admin: bool = True
    session_secret: str = "miralingo-dev-session-secret"
    session_cookie_name: str = "miralingo_session"
    session_ttl_seconds: int = 60 * 60 * 24 * 14
    password_reset_ttl_seconds: int = 60 * 60
    frontend_base_url: str = "http://localhost:5173"
    email_provider: str | None = None
    email_from: str | None = None
    app_url: str = "http://localhost:5173"
    resend_api_key: str | None = None
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_redirect_uri: str | None = None
    enable_dev_password_reset_logging: bool = True
    phrase_csv_path: Path = Path("data/phrases/english-mirad-sentence-pairs.csv")
    beginner_json_path: Path | None = None
    numbers_json_path: Path | None = None
    database_path: Path = Path(".miralingo/miralingo.sqlite3")

    @property
    def local_admin_bootstrap_enabled(self) -> bool:
        """Return whether the development admin/admin bootstrap may be used."""
        return self.environment == "development" and self.enable_local_admin

    @property
    def session_cookie_secure(self) -> bool:
        """Only allow non-secure cookies for explicit local development."""
        return self.environment not in {"development", "local", "test"}

    @property
    def google_oauth_configured(self) -> bool:
        """Return whether Google OAuth has enough config to start a flow."""
        return bool(self.google_client_id and self.google_client_secret and self.google_redirect_uri)


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _optional_env(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None
    stripped = value.strip()
    if len(stripped) >= 2 and stripped[0] == stripped[-1] and stripped[0] in {"'", '"'}:
        stripped = stripped[1:-1].strip()
    return stripped or None


def _validated_app_url(raw: str, *, environment: str) -> str:
    value = str(raw or "").strip().rstrip("/")
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("APP_URL must be an absolute http(s) URL.")
    if parsed.query or parsed.fragment:
        raise ValueError("APP_URL must not include query parameters or fragments.")
    if environment == "production" and parsed.scheme != "https":
        raise ValueError("APP_URL must use https in production.")
    return value


def load_settings() -> Settings:
    """Load settings from environment variables.

    Local admin bootstrap is intentionally explicit: it only works when the
    environment is development and MIRALINGO_ENABLE_LOCAL_ADMIN is truthy.
    """
    environment = os.getenv("MIRALINGO_ENV", "development").strip().lower()
    enable_local_admin = os.getenv("MIRALINGO_ENABLE_LOCAL_ADMIN", "true").strip().lower() in _TRUE_VALUES
    session_secret = os.getenv("MIRALINGO_SESSION_SECRET", "miralingo-dev-session-secret")
    phrase_csv_path = Path(os.getenv("MIRALINGO_PHRASE_CSV_PATH", "data/phrases/english-mirad-sentence-pairs.csv"))
    beginner_json_raw = os.getenv("MIRALINGO_BEGINNER_JSON_PATH", "data/miralingo_modules/beginner.json").strip()
    beginner_json_path = Path(beginner_json_raw) if beginner_json_raw else None
    numbers_json_raw = os.getenv("MIRALINGO_NUMBERS_JSON_PATH", "data/miralingo_modules/numbers.json").strip()
    numbers_json_path = Path(numbers_json_raw) if numbers_json_raw else None
    database_path = Path(os.getenv("MIRALINGO_DATABASE_PATH", ".miralingo/miralingo.sqlite3"))
    frontend_base_url = os.getenv("MIRALINGO_FRONTEND_BASE_URL", "http://localhost:5173").rstrip("/")
    app_url = _validated_app_url(os.getenv("APP_URL", frontend_base_url), environment=environment)
    return Settings(
        environment=environment,
        enable_local_admin=enable_local_admin,
        session_secret=session_secret,
        session_cookie_name=os.getenv("MIRALINGO_SESSION_COOKIE_NAME", "miralingo_session"),
        session_ttl_seconds=_int_env("MIRALINGO_SESSION_TTL_SECONDS", 60 * 60 * 24 * 14),
        password_reset_ttl_seconds=_int_env("MIRALINGO_PASSWORD_RESET_TTL_SECONDS", 60 * 60),
        frontend_base_url=frontend_base_url,
        email_provider=_optional_env("EMAIL_PROVIDER"),
        email_from=_optional_env("EMAIL_FROM"),
        app_url=app_url,
        resend_api_key=_optional_env("RESEND_API_KEY"),
        google_client_id=_optional_env("MIRALINGO_GOOGLE_CLIENT_ID"),
        google_client_secret=_optional_env("MIRALINGO_GOOGLE_CLIENT_SECRET"),
        google_redirect_uri=_optional_env("MIRALINGO_GOOGLE_REDIRECT_URI"),
        enable_dev_password_reset_logging=os.getenv("MIRALINGO_ENABLE_DEV_RESET_LOGGING", "true").strip().lower() in _TRUE_VALUES,
        phrase_csv_path=phrase_csv_path,
        beginner_json_path=beginner_json_path,
        numbers_json_path=numbers_json_path,
        database_path=database_path,
    )
