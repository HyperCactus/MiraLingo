"""Runtime configuration for the MiraLingo web application."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


_TRUE_VALUES = {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """Process-local settings used by the FastAPI app."""

    environment: str = "development"
    enable_local_admin: bool = True
    session_secret: str = "miralingo-dev-session-secret"
    phrase_csv_path: Path = Path("data/phrases/english-mirad-sentence-pairs.csv")

    @property
    def local_admin_bootstrap_enabled(self) -> bool:
        """Return whether the development admin/admin bootstrap may be used."""
        return self.environment == "development" and self.enable_local_admin


def load_settings() -> Settings:
    """Load settings from environment variables.

    Local admin bootstrap is intentionally explicit: it only works when the
    environment is development and MIRALINGO_ENABLE_LOCAL_ADMIN is truthy.
    """
    environment = os.getenv("MIRALINGO_ENV", "development").strip().lower()
    enable_local_admin = (
        os.getenv("MIRALINGO_ENABLE_LOCAL_ADMIN", "true").strip().lower() in _TRUE_VALUES
    )
    session_secret = os.getenv("MIRALINGO_SESSION_SECRET", "miralingo-dev-session-secret")
    phrase_csv_path = Path(
        os.getenv("MIRALINGO_PHRASE_CSV_PATH", "data/phrases/english-mirad-sentence-pairs.csv")
    )
    return Settings(
        environment=environment,
        enable_local_admin=enable_local_admin,
        session_secret=session_secret,
        phrase_csv_path=phrase_csv_path,
    )
