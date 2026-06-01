"""FastAPI entrypoint for the Mirad learning web application."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field
from starlette.middleware.sessions import SessionMiddleware

from .audio import AudioFailure, synthesize_card_audio, synthesize_text_audio
from .auth import (
    LOCAL_ADMIN_USERNAME,
    SESSION_USER_KEY,
    authenticate_local_admin,
    normalize_username,
    registered_login_error,
    serialize_user,
    user_from_session,
)
from .card_content import CardContentImportError, CardContentSourceMissingError, import_card_content
from .config import Settings, load_settings
from .content_cli import error_to_payload, result_to_payload
from .practice import answer_summary, build_practice_progress, build_practice_queue, record_practice_answer
from .storage import MiraLingoStorage, StorageError

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


class RegisterRequest(BaseModel):
    """Password-bearing registration request body.

    Do not log or echo instances of this model because it contains credentials.
    """

    username: str
    password: str


class UserSettingsUpdateRequest(BaseModel):
    """Validated learner settings update payload."""

    model_config = ConfigDict(extra="forbid")

    theme: Literal["light", "dark", "system"]
    tts_speed: float = Field(gt=0, le=2.0)
    tts_autoplay: bool = True
    sfx_enabled: bool = True


class DeleteAccountRequest(BaseModel):
    """Destructive account deletion confirmation payload."""

    model_config = ConfigDict(extra="forbid")

    username: str
    confirmation: str


class TextToSpeechRequest(BaseModel):
    """Authenticated arbitrary Mirad text preview request."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, max_length=500)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create the MiraLingo API application."""
    runtime_settings = settings or load_settings()
    app = FastAPI(title=f"{APP_NAME} API")
    app.add_middleware(SessionMiddleware, secret_key=runtime_settings.session_secret)
    app.state.storage = MiraLingoStorage(runtime_settings.database_path)
    app.state.card_content_cache = {"result": None, "phrase_mtime_ns": None}

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

    def storage_failure_response(exc: StorageError, status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE) -> JSONResponse:
        """Return a stable storage diagnostic without secret-bearing request fields."""
        return JSONResponse(status_code=status_code, content=exc.public_payload())

    def answer_events_for_user(username: str, phase: str) -> list[dict[str, Any]]:
        storage: MiraLingoStorage = app.state.storage
        return [record.practice_event() for record in storage.list_answer_events(username=username, phase=phase)]

    def ensure_practice_storage_user(user_phase: str, username: str, role: str) -> None:
        storage: MiraLingoStorage = app.state.storage
        storage.ensure_session_user(username=username, role=role, phase=user_phase)

    def imported_card_content(*, word_limit: int = 500, force_refresh: bool = False):
        phrase_path = Path(runtime_settings.phrase_csv_path)
        cache = app.state.card_content_cache
        phrase_mtime_ns = phrase_path.stat().st_mtime_ns if phrase_path.exists() else None
        cached_result = cache.get("result")

        if not force_refresh and cached_result is not None and cache.get("phrase_mtime_ns") == phrase_mtime_ns:
            return cached_result

        result = import_card_content(
            phrase_csv_path=runtime_settings.phrase_csv_path,
            word_limit=word_limit,
        )
        cache["result"] = result
        cache["phrase_mtime_ns"] = phrase_mtime_ns
        return result

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
            result = imported_card_content(
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

    @app.get("/lookup", tags=["lexicon"])
    def lookup(
        q: str = Query(..., min_length=1),
        direction: Literal["en_to_mir", "mir_to_en"] = Query(...),
        top_k: int = Query(default=3, ge=1),
    ) -> JSONResponse:
        """Return open semantic lexicon results for English or Mirad queries."""
        try:
            from mirad_translator.semantic_lexicon import semantic_lookup, semantic_lookup_mirad

            if direction == "en_to_mir":
                hits = semantic_lookup(
                    english_word=q,
                    top_k=top_k,
                    min_similarity=0.5,
                    include_exact=True,
                )
                payload = [
                    {
                        "english": hit["english"],
                        "mirad": hit["mirad"],
                        "cosine_similarity": hit["cosine_similarity"],
                        "is_exact": hit["is_exact"],
                    }
                    for hit in hits
                ]
            else:
                hits = semantic_lookup_mirad(
                    mirad_word=q,
                    top_k=top_k,
                    min_similarity=0.5,
                    include_exact=True,
                )
                payload = [
                    {
                        "mirad": hit["mirad"],
                        "english": hit["english"],
                        "cosine_similarity": hit["cosine_similarity"],
                        "is_exact": hit["is_exact"],
                    }
                    for hit in hits
                ]
        except (ImportError, ModuleNotFoundError, RuntimeError):
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"error": "semantic search unavailable"},
            )

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

    @app.get("/settings", tags=["settings"])
    def get_settings(request: Request) -> JSONResponse:
        """Return durable learner settings for the authenticated session."""
        user = user_from_session(request.session.get(SESSION_USER_KEY))
        if user is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "ok": False,
                    "error": "unauthenticated",
                    "phase": "settings_get",
                    "detail": "Login is required to view settings.",
                },
            )
        storage: MiraLingoStorage = request.app.state.storage
        try:
            storage.ensure_session_user(username=user.username, role=user.role, phase="settings_get")
            settings_record = storage.get_user_settings(username=user.username)
        except StorageError as exc:
            return storage_failure_response(exc)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"ok": True, "phase": "settings_get", "settings": settings_record.public_dict()},
        )

    @app.put("/settings", tags=["settings"])
    def update_settings(request: Request, payload: UserSettingsUpdateRequest) -> JSONResponse:
        """Persist durable learner settings for the authenticated session."""
        user = user_from_session(request.session.get(SESSION_USER_KEY))
        if user is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "ok": False,
                    "error": "unauthenticated",
                    "phase": "settings_update",
                    "detail": "Login is required to update settings.",
                },
            )
        storage: MiraLingoStorage = request.app.state.storage
        try:
            storage.ensure_session_user(username=user.username, role=user.role, phase="settings_update")
            settings_record = storage.upsert_user_settings(
                username=user.username,
                theme=payload.theme,
                tts_speed=payload.tts_speed,
                tts_autoplay=payload.tts_autoplay,
                sfx_enabled=payload.sfx_enabled,
            )
        except StorageError as exc:
            return storage_failure_response(exc)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"ok": True, "phase": "settings_update", "settings": settings_record.public_dict()},
        )

    @app.post("/auth/register", tags=["auth"])
    def register(request: Request, registration: RegisterRequest) -> JSONResponse:
        """Register a learner account in durable SQLite storage and log it in."""
        storage: MiraLingoStorage = request.app.state.storage
        try:
            user, error_payload, error_status = storage.register_account(
                username=registration.username,
                password=registration.password,
            )
        except StorageError as exc:
            return storage_failure_response(exc)
        if user is None:
            return JSONResponse(status_code=error_status or 400, content=error_payload or {})

        request.session[SESSION_USER_KEY] = serialize_user(user)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"authenticated": True, "user": user.public_dict()},
        )

    @app.post("/auth/login", tags=["auth"])
    def login(request: Request, credentials: LoginRequest) -> JSONResponse:
        """Log in as either a registered learner or the guarded development local admin."""
        storage: MiraLingoStorage = request.app.state.storage
        if credentials.username.strip().lower() != LOCAL_ADMIN_USERNAME:
            try:
                registered_user = storage.authenticate_account(
                    username=credentials.username,
                    password=credentials.password,
                )
            except StorageError as exc:
                return storage_failure_response(exc)
            if registered_user is None:
                error_payload, error_status = registered_login_error()
                return JSONResponse(status_code=error_status, content=error_payload)

            request.session[SESSION_USER_KEY] = serialize_user(registered_user)
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"authenticated": True, "user": registered_user.public_dict()},
            )

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

    @app.delete("/auth/account", tags=["auth"])
    def delete_account(request: Request, payload: DeleteAccountRequest) -> JSONResponse:
        """Delete the current learner account after explicit confirmation."""
        user = user_from_session(request.session.get(SESSION_USER_KEY))
        if user is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "ok": False,
                    "error": "unauthenticated",
                    "phase": "account_delete",
                    "detail": "Login is required to delete the current account.",
                },
            )
        if user.username == LOCAL_ADMIN_USERNAME:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "ok": False,
                    "error": "protected_account",
                    "phase": "account_delete",
                    "detail": "The local admin account cannot be deleted.",
                },
            )
        expected_confirmation = f"{user.username} DELETE"
        if payload.confirmation.strip() != expected_confirmation or normalize_username(payload.username) != user.username:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "ok": False,
                    "error": "invalid_confirmation",
                    "phase": "account_delete",
                    "detail": "Account deletion requires the current username plus the exact confirmation phrase '<username> DELETE'.",
                },
            )
        storage: MiraLingoStorage = request.app.state.storage
        try:
            storage.delete_user_account(username=user.username)
        except StorageError as exc:
            status_code = status.HTTP_403_FORBIDDEN if exc.error == "protected_account" else status.HTTP_503_SERVICE_UNAVAILABLE
            return storage_failure_response(exc, status_code=status_code)
        request.session.pop(SESSION_USER_KEY, None)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "ok": True,
                "phase": "account_delete",
                "deleted_username": user.username,
                "authenticated": False,
            },
        )

    @app.get("/practice/queue", tags=["practice"])
    def practice_queue(
        request: Request,
        limit: int = Query(default=10, ge=1, le=50),
        mode: Literal["mixed", "revision", "build_vocabulary"] = Query(default="mixed"),
    ) -> JSONResponse:
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
            result = imported_card_content()
        except CardContentSourceMissingError as exc:
            payload = error_to_payload(exc)
            payload["practice_phase"] = "practice_queue"
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=payload)
        except CardContentImportError as exc:
            payload = error_to_payload(exc)
            payload["practice_phase"] = "practice_queue"
            return JSONResponse(status_code=status.HTTP_502_BAD_GATEWAY, content=payload)

        try:
            ensure_practice_storage_user("practice_queue", user.username, user.role)
            events = answer_events_for_user(user.username, "practice_queue")
            payload = build_practice_queue(
                cards=result.cards,
                events=events,
                limit=limit,
                mode=mode,
            )
            if payload.get("ok") and mode == "build_vocabulary":
                seen_keys = request.app.state.storage.list_shown_card_keys(username=user.username)
                for card in payload.get("cards", []):
                    key = (str(card.get("base_card_id") or ""), str(card.get("direction") or ""))
                    card["intro_mode"] = key not in seen_keys
            request.app.state.storage.record_cards_shown(username=user.username, cards=payload["cards"])
        except StorageError as exc:
            return storage_failure_response(exc)
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
            result = imported_card_content()
        except CardContentSourceMissingError as exc:
            payload = error_to_payload(exc)
            payload["practice_phase"] = "practice_progress"
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=payload)
        except CardContentImportError as exc:
            payload = error_to_payload(exc)
            payload["practice_phase"] = "practice_progress"
            return JSONResponse(status_code=status.HTTP_502_BAD_GATEWAY, content=payload)

        try:
            ensure_practice_storage_user("practice_progress", user.username, user.role)
            events = answer_events_for_user(user.username, "practice_progress")
            payload = build_practice_progress(
                cards=result.cards,
                events=events,
            )
        except StorageError as exc:
            return storage_failure_response(exc)
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
            request.app.state.storage.ensure_session_user(username=user.username, role=user.role, phase="audio_synthesis")
            settings_record = request.app.state.storage.get_user_settings(username=user.username)
            result = imported_card_content()
        except StorageError as exc:
            return storage_failure_response(exc)
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
            "X-MiraLingo-TTS-Speed": str(settings_record.tts_speed),
            "X-MiraLingo-Voice-Id": settings_record.voice_id,
        }
        return Response(
            content=audio_result.wav_bytes,
            media_type=audio_result.content_type,
            headers=headers,
        )

    @app.post("/tts/mbrola", tags=["practice"])
    def mbrola_text_audio(request: Request, payload: TextToSpeechRequest):
        """Return MBROLA WAV audio for authenticated arbitrary Mirad text previews."""
        user = user_from_session(request.session.get(SESSION_USER_KEY))
        if user is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "ok": False,
                    "error": "unauthenticated",
                    "phase": "audio_synthesis",
                    "backend": "mbrola",
                    "detail": "Login is required to request text audio.",
                },
            )
        try:
            request.app.state.storage.ensure_session_user(username=user.username, role=user.role, phase="audio_synthesis")
            settings_record = request.app.state.storage.get_user_settings(username=user.username)
        except StorageError as exc:
            return storage_failure_response(exc)

        audio_result = synthesize_text_audio(payload.text)
        if isinstance(audio_result, AudioFailure):
            return JSONResponse(status_code=audio_result.status_code, content=audio_result.payload)

        headers = {
            "Cache-Control": "no-store",
            "X-MiraLingo-Audio-Phase": audio_result.diagnostics["phase"],
            "X-MiraLingo-Audio-Backend": audio_result.diagnostics["backend"],
            "X-MiraLingo-TTS-Speed": str(settings_record.tts_speed),
            "X-MiraLingo-Voice-Id": settings_record.voice_id,
        }
        return Response(content=audio_result.wav_bytes, media_type=audio_result.content_type, headers=headers)

    @app.post("/practice/answers", tags=["practice"])
    @app.post("/practice/answer", tags=["practice"], include_in_schema=False)
    def practice_answer(request: Request, submission: PracticeAnswerRequest) -> JSONResponse:
        """Record one practice answer in durable SQLite storage."""
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
            result = imported_card_content()
        except CardContentSourceMissingError as exc:
            payload = error_to_payload(exc)
            payload["practice_phase"] = "practice_answer"
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=payload)
        except CardContentImportError as exc:
            payload = error_to_payload(exc)
            payload["practice_phase"] = "practice_answer"
            return JSONResponse(status_code=status.HTTP_502_BAD_GATEWAY, content=payload)

        try:
            ensure_practice_storage_user("practice_answer", user.username, user.role)
            prior_events = answer_events_for_user(user.username, "practice_answer")
            updated_events = record_practice_answer(
                cards=result.cards,
                events=prior_events,
                card_id=submission.card_id,
                submitted_answer=submission.answer or "",
                correct=submission.correct,
            )
            if isinstance(updated_events, dict) and updated_events.get("ok") is False:
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=updated_events)

            latest_event = updated_events[-1]
            request.app.state.storage.append_answer_event(username=user.username, **latest_event)
            durable_events = answer_events_for_user(user.username, "practice_answer")
        except StorageError as exc:
            return storage_failure_response(exc)
        payload = answer_summary(result.cards, durable_events, submission.card_id)
        return JSONResponse(status_code=status.HTTP_200_OK, content=payload)

    return app


app = create_app()
