"""FastAPI entrypoint for the Mirad learning web application."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from .auth import SESSION_USER_KEY, authenticate_local_admin, serialize_user, user_from_session
from .config import Settings, load_settings

APP_NAME = "MiraLingo"


class LoginRequest(BaseModel):
    """Password-bearing login request body.

    Do not log or echo instances of this model because it contains credentials.
    """

    username: str
    password: str


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create the MiraLingo API application."""
    runtime_settings = settings or load_settings()
    app = FastAPI(title=f"{APP_NAME} API")
    app.add_middleware(SessionMiddleware, secret_key=runtime_settings.session_secret)

    @app.get("/health", tags=["diagnostics"])
    def health() -> dict[str, str]:
        """Return process-local health for smoke tests and operators."""
        return {"status": "ok", "service": "mirad-webapp"}

    @app.get("/auth/current-user", tags=["auth"])
    def current_user(request: Request) -> JSONResponse:
        """Return the current authenticated user or an explicit logged-out state."""
        user = user_from_session(request.session.get(SESSION_USER_KEY))
        if user is None:
            payload: dict[str, Any] = {
                "authenticated": False,
                "user": None,
                "detail": "No active user session.",
            }
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=payload)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"authenticated": True, "user": user.public_dict()},
        )

    @app.post("/auth/login", tags=["auth"])
    def login(request: Request, credentials: LoginRequest) -> JSONResponse:
        """Log in through the guarded development local-admin bootstrap."""
        user, error_payload, error_status = authenticate_local_admin(
            username=credentials.username,
            password=credentials.password,
            settings=runtime_settings,
        )
        if user is None:
            return JSONResponse(status_code=error_status or 401, content=error_payload or {})

        request.session[SESSION_USER_KEY] = serialize_user(user)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"authenticated": True, "user": user.public_dict()},
        )

    @app.post("/auth/logout", tags=["auth"])
    def logout(request: Request) -> dict[str, bool]:
        """Clear the active session."""
        request.session.pop(SESSION_USER_KEY, None)
        return {"authenticated": False}

    return app


app = create_app()
