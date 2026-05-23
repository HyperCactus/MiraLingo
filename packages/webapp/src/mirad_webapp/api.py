"""FastAPI entrypoint for the Mirad learning web application."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from .audio import AudioFailure, synthesize_card_audio
from .auth import SESSION_USER_KEY, authenticate_local_admin, serialize_user, user_from_session
from .card_content import CardContentImportError, CardContentSourceMissingError, import_card_content
from .config import Settings, load_settings
from .content_cli import error_to_payload, result_to_payload
from .practice import answer_summary, build_practice_progress, build_practice_queue, record_practice_answer

APP_NAME = "MiraLingo"


class PracticeAnswerRequest(BaseModel):
    """Practice answer submission request body."""

    card_id: str
    correct: bool | None = None
    answer: str | None = None


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

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Return structured practice diagnostics for invalid JSON or query payloads."""
        if request.url.path.startswith("/practice/"):
            return JSONResponse(
                status_code=422,
                content={
                    "ok": False,
                    "error": "invalid_practice_payload",
                    "phase": "practice_validation",
                    "detail": "Practice request payload or query parameters failed validation.",
                },
            )
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.get("/health", tags=["diagnostics"])
    def health() -> dict[str, str]:
        """Return process-local health for smoke tests and operators."""
        return {"status": "ok", "service": "mirad-webapp"}

    @app.get("/content/import/preview", tags=["content"])
    def content_import_preview(
        word_limit: int = Query(default=500, ge=0, le=5000),
        source: str = Query(default="configured", pattern="^configured$"),
    ) -> JSONResponse:
        """Preview deterministic card import counts from configured project sources.

        The endpoint is intentionally non-mutating and accepts no filesystem path
        parameters; callers can only choose the configured source alias and a
        bounded word-candidate limit.
        """
        try:
            result = import_card_content(
                phrase_csv_path=runtime_settings.phrase_csv_path,
                word_limit=word_limit,
            )
        except CardContentSourceMissingError as exc:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=error_to_payload(exc))
        except CardContentImportError as exc:
            return JSONResponse(status_code=status.HTTP_502_BAD_GATEWAY, content=error_to_payload(exc))

        payload = result_to_payload(result)
        payload["auth_required"] = False
        payload["source"] = source
        return JSONResponse(status_code=status.HTTP_200_OK, content=payload)

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

    def practice_events_from_session(request: Request) -> list[dict[str, Any]]:
        """Return bounded practice events, treating corrupted session data as empty."""
        events = request.session.get("practice_events", [])
        return events if isinstance(events, list) else []

    @app.get("/practice/queue", tags=["practice"])
    def practice_queue(request: Request, limit: int = Query(default=10, ge=1, le=50)) -> JSONResponse:
        """Return an adaptive practice queue for the authenticated session."""
        user = user_from_session(request.session.get(SESSION_USER_KEY))
        if user is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "ok": False,
                    "error": "unauthenticated",
                    "phase": "practice_queue",
                    "detail": "Login is required to request a practice queue.",
                },
            )
        try:
            result = import_card_content(phrase_csv_path=runtime_settings.phrase_csv_path)
        except CardContentSourceMissingError as exc:
            payload = error_to_payload(exc)
            payload["practice_phase"] = "practice_queue"
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=payload)
        except CardContentImportError as exc:
            payload = error_to_payload(exc)
            payload["practice_phase"] = "practice_queue"
            return JSONResponse(status_code=status.HTTP_502_BAD_GATEWAY, content=payload)

        payload = build_practice_queue(
            cards=result.cards,
            events=practice_events_from_session(request),
            limit=limit,
        )
        return JSONResponse(status_code=status.HTTP_200_OK, content=payload)

    @app.get("/practice/progress", tags=["practice"])
    def practice_progress(request: Request) -> JSONResponse:
        """Return progress diagnostics for the authenticated session's bounded practice history."""
        user = user_from_session(request.session.get(SESSION_USER_KEY))
        if user is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "ok": False,
                    "error": "unauthenticated",
                    "phase": "practice_progress",
                    "detail": "Login is required to request practice progress.",
                },
            )
        try:
            result = import_card_content(phrase_csv_path=runtime_settings.phrase_csv_path)
        except CardContentSourceMissingError as exc:
            payload = error_to_payload(exc)
            payload["practice_phase"] = "practice_progress"
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=payload)
        except CardContentImportError as exc:
            payload = error_to_payload(exc)
            payload["practice_phase"] = "practice_progress"
            return JSONResponse(status_code=status.HTTP_502_BAD_GATEWAY, content=payload)

        payload = build_practice_progress(
            cards=result.cards,
            events=practice_events_from_session(request),
        )
        return JSONResponse(status_code=status.HTTP_200_OK, content=payload)

    @app.get("/practice/audio/{card_id:path}", tags=["practice"])
    def practice_audio(request: Request, card_id: str):
        """Return MBROLA WAV audio for one authenticated configured practice card."""
        user = user_from_session(request.session.get(SESSION_USER_KEY))
        if user is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "ok": False,
                    "error": "unauthenticated",
                    "phase": "audio_synthesis",
                    "backend": "mbrola",
                    "card_id": card_id,
                    "detail": "Login is required to request practice audio.",
                },
            )
        try:
            result = import_card_content(phrase_csv_path=runtime_settings.phrase_csv_path)
        except CardContentSourceMissingError as exc:
            payload = error_to_payload(exc)
            payload.update({"phase": "audio_synthesis", "backend": "mbrola", "card_id": card_id})
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=payload)
        except CardContentImportError as exc:
            payload = error_to_payload(exc)
            payload.update({"phase": "audio_synthesis", "backend": "mbrola", "card_id": card_id})
            return JSONResponse(status_code=status.HTTP_502_BAD_GATEWAY, content=payload)

        audio_result = synthesize_card_audio(card_id=card_id, cards=result.cards)
        if isinstance(audio_result, AudioFailure):
            return JSONResponse(status_code=audio_result.status_code, content=audio_result.payload)

        headers = {
            "Cache-Control": "no-store",
            "X-MiraLingo-Audio-Phase": audio_result.diagnostics["phase"],
            "X-MiraLingo-Audio-Backend": audio_result.diagnostics["backend"],
            "X-MiraLingo-Card-Id": audio_result.diagnostics["card_id"],
        }
        return Response(
            content=audio_result.wav_bytes,
            media_type=audio_result.content_type,
            headers=headers,
        )

    @app.post("/practice/answers", tags=["practice"])
    @app.post("/practice/answer", tags=["practice"], include_in_schema=False)
    def practice_answer(request: Request, submission: PracticeAnswerRequest) -> JSONResponse:
        """Record one practice answer in the signed session."""
        user = user_from_session(request.session.get(SESSION_USER_KEY))
        if user is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "ok": False,
                    "error": "unauthenticated",
                    "phase": "practice_answer",
                    "detail": "Login is required to submit a practice answer.",
                },
            )
        try:
            result = import_card_content(phrase_csv_path=runtime_settings.phrase_csv_path)
        except CardContentSourceMissingError as exc:
            payload = error_to_payload(exc)
            payload["practice_phase"] = "practice_answer"
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=payload)
        except CardContentImportError as exc:
            payload = error_to_payload(exc)
            payload["practice_phase"] = "practice_answer"
            return JSONResponse(status_code=status.HTTP_502_BAD_GATEWAY, content=payload)

        prior_events = practice_events_from_session(request)
        updated_events = record_practice_answer(
            cards=result.cards,
            events=prior_events,
            card_id=submission.card_id,
            submitted_answer=submission.answer or "",
            correct=submission.correct,
        )
        if isinstance(updated_events, dict) and updated_events.get("ok") is False:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=updated_events)

        request.session["practice_events"] = updated_events
        payload = answer_summary(result.cards, updated_events, submission.card_id)
        return JSONResponse(status_code=status.HTTP_200_OK, content=payload)

    return app


app = create_app()
