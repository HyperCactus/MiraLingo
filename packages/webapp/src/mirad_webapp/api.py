"""FastAPI entrypoint for the Mirad learning web application."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

APP_NAME = "MiraLingo"


def create_app() -> FastAPI:
    """Create the MiraLingo API application."""
    app = FastAPI(title=f"{APP_NAME} API")

    @app.get("/health", tags=["diagnostics"])
    def health() -> dict[str, str]:
        """Return process-local health for smoke tests and operators."""
        return {"status": "ok", "service": "mirad-webapp"}

    @app.get("/auth/current-user", tags=["auth"])
    def current_user() -> JSONResponse:
        """Return an explicit unauthenticated state until auth is implemented."""
        payload: dict[str, Any] = {
            "authenticated": False,
            "user": None,
            "detail": "No active user session.",
        }
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=payload)

    return app


app = create_app()
