"""FastAPI entrypoint for the Mirad learning web application."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlencode
from typing import Any, Literal

from fastapi import FastAPI, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse, Response
from pydantic import BaseModel, ConfigDict, Field

from .analytics import build_practice_analytics
from .audio import AudioFailure, synthesize_card_audio, synthesize_text_audio
from .auth import (
    ADMIN_ROLE,
    LOCAL_ADMIN_EMAIL,
    LOCAL_ADMIN_USERNAME,
    authenticate_local_admin,
    new_public_token,
    normalize_email,
    registered_login_error,
)
from .card_content import CardContentImportError, CardContentSourceMissingError, import_card_content
from .config import Settings, load_settings
from .content_cli import error_to_payload, result_to_payload
from .practice import answer_summary, build_practice_achievements, build_practice_progress, build_practice_queue, record_practice_answer
from .storage import MiraLingoStorage, StorageError

APP_NAME = "MiraLingo"


def _achievement_display_name(user: Any) -> str:
    name = str(getattr(user, "name", "") or "").strip()
    if name:
        return name
    email = str(getattr(user, "email", "") or "").strip()
    if "@" in email:
        local_part = email.split("@", 1)[0].strip()
        if local_part:
            return local_part
    return str(getattr(user, "username", "") or getattr(user, "id", "") or "Learner").strip() or "Learner"


class PracticeAnswerRequest(BaseModel):
    """Practice answer submission request body."""

    card_id: str
    correct: bool | None = None
    answer: str | None = None


class LoginRequest(BaseModel):
    """Password-bearing login request body.

    Do not log or echo instances of this model because it contains credentials.
    """

    email: str | None = None
    username: str | None = None
    password: str


class RegisterRequest(BaseModel):
    """Password-bearing registration request body.

    Do not log or echo instances of this model because it contains credentials.
    """

    email: str | None = None
    username: str | None = None
    name: str | None = None
    nickname: str | None = None
    password: str


class PasswordForgotRequest(BaseModel):
    """Forgot-password request body. Do not reveal account existence."""

    email: str


class PasswordResetRequest(BaseModel):
    """Password reset confirmation body."""

    token: str
    password: str


class UserSettingsUpdateRequest(BaseModel):
    """Validated learner settings update payload."""

    model_config = ConfigDict(extra="forbid")

    theme: Literal["light", "dark", "system"]
    tts_speed: float = Field(gt=0, le=2.0)
    tts_autoplay: bool = True
    sfx_enabled: bool = True
    sfx_mode: Literal["all", "on_answer", "ui_only", "off"] = "on_answer"


class DeleteAccountRequest(BaseModel):
    """Destructive account deletion confirmation payload."""

    model_config = ConfigDict(extra="forbid")

    email: str | None = None
    username: str | None = None
    confirmation: str


class TextToSpeechRequest(BaseModel):
    """Authenticated arbitrary Mirad text preview request."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, max_length=500)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create the MiraLingo API application."""
    runtime_settings = settings or load_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Warm lexicon resources without blocking Docker health startup."""
        import asyncio

        app.state.semantic_warmup = {"status": "pending", "detail": "Semantic lexicon warmup queued."}

        def _load() -> int:
            from mirad_translator.semantic_lexicon import _get_embedder, _get_lexicon_collection

            embedder = _get_embedder()
            collection = _get_lexicon_collection()
            embedder.encode(["test"], show_progress_bar=False)
            return collection.count()

        async def _warm() -> None:
            app.state.semantic_warmup = {"status": "running", "detail": "Semantic lexicon warmup running."}
            try:
                loop = asyncio.get_running_loop()
                count = await loop.run_in_executor(None, _load)
                app.state.semantic_warmup = {"status": "ready", "detail": f"Semantic lexicon warm with {count} entries."}
            except Exception as exc:
                app.state.semantic_warmup = {"status": "error", "detail": f"{type(exc).__name__}: {exc}"[:300]}

        warmup_task = asyncio.create_task(_warm())
        try:
            yield
        finally:
            warmup_task.cancel()

    app = FastAPI(title=f"{APP_NAME} API", lifespan=lifespan)
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
    def health() -> dict[str, Any]:
        """Return process-local health for smoke tests and operators."""
        return {"status": "ok", "service": "mirad-webapp", "semantic_warmup": getattr(app.state, "semantic_warmup", {"status": "unknown"})}

    def storage_failure_response(exc: StorageError, status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE) -> JSONResponse:
        """Return a stable storage diagnostic without secret-bearing request fields."""
        return JSONResponse(status_code=status_code, content=exc.public_payload())

    def session_token_from_request(request: Request) -> str | None:
        return request.cookies.get(runtime_settings.session_cookie_name)

    def set_session_cookie(response: Response, token: str, expires_at: str) -> None:
        response.set_cookie(
            runtime_settings.session_cookie_name,
            token,
            httponly=True,
            secure=runtime_settings.session_cookie_secure,
            samesite="lax",
            expires=expires_at,
            path="/",
        )

    def clear_session_cookie(response: Response) -> None:
        response.delete_cookie(
            runtime_settings.session_cookie_name,
            httponly=True,
            secure=runtime_settings.session_cookie_secure,
            samesite="lax",
            path="/",
        )

    def authenticated_payload(user) -> dict[str, Any]:
        return {"authenticated": True, "user": user.public_dict()}

    def create_login_response(user, *, status_code: int = status.HTTP_200_OK) -> JSONResponse:
        storage: MiraLingoStorage = app.state.storage
        raw_token, expires_at = storage.create_session(user_id=user.id, secret=runtime_settings.session_secret, ttl_seconds=runtime_settings.session_ttl_seconds)
        response = JSONResponse(status_code=status_code, content=authenticated_payload(user))
        set_session_cookie(response, raw_token, expires_at)
        return response

    def resolve_current_user(request: Request, phase: str):
        storage: MiraLingoStorage = app.state.storage
        return storage.user_from_session_token(raw_token=session_token_from_request(request), secret=runtime_settings.session_secret)

    def unauthenticated_response(phase: str, detail: str) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"ok": False, "error": "unauthenticated", "phase": phase, "detail": detail})

    def forbidden_response(phase: str, detail: str = "You do not have permission to perform this action.") -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"ok": False, "error": "forbidden", "phase": phase, "detail": detail})

    def answer_events_for_user(username: str, phase: str) -> list[dict[str, Any]]:
        storage: MiraLingoStorage = app.state.storage
        return [record.practice_event() for record in storage.list_answer_events(username=username, phase=phase)]

    def ensure_practice_storage_user(user_phase: str, username: str, role: str) -> None:
        storage: MiraLingoStorage = app.state.storage
        storage.ensure_session_user(username=username, role=role, phase=user_phase)

    def imported_card_content(*, word_limit: int = 500, force_refresh: bool = False):
        phrase_path = Path(runtime_settings.phrase_csv_path)
        beginner_path = Path(runtime_settings.beginner_json_path) if runtime_settings.beginner_json_path is not None else None
        numbers_path = Path(runtime_settings.numbers_json_path) if runtime_settings.numbers_json_path is not None else None
        cache = app.state.card_content_cache
        phrase_mtime_ns = phrase_path.stat().st_mtime_ns if phrase_path.exists() else None
        beginner_mtime_ns = beginner_path.stat().st_mtime_ns if beginner_path is not None and beginner_path.exists() else None
        numbers_mtime_ns = numbers_path.stat().st_mtime_ns if numbers_path is not None and numbers_path.exists() else None
        cached_result = cache.get("result")

        if (
            not force_refresh
            and cached_result is not None
            and cache.get("phrase_mtime_ns") == phrase_mtime_ns
            and cache.get("beginner_mtime_ns") == beginner_mtime_ns
            and cache.get("numbers_mtime_ns") == numbers_mtime_ns
        ):
            return cached_result

        result = import_card_content(
            phrase_csv_path=runtime_settings.phrase_csv_path,
            beginner_json_path=runtime_settings.beginner_json_path,
            numbers_json_path=runtime_settings.numbers_json_path,
            word_limit=word_limit,
        )
        cache["result"] = result
        cache["phrase_mtime_ns"] = phrase_mtime_ns
        cache["beginner_mtime_ns"] = beginner_mtime_ns
        cache["numbers_mtime_ns"] = numbers_mtime_ns
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

    def fallback_lexicon_search(q: str, direction: str, top_k: int) -> list[dict[str, Any]]:
        """Return fast SQLite FTS/prefix matches when semantic embeddings are unavailable or warming."""
        import re
        import sqlite3
        from difflib import SequenceMatcher

        from mirad_translator.lexicon_db import DB_PATH, build_lexicon_db, lookup_word_candidates, lookup_mirad_word_candidates

        normalized = " ".join(str(q or "").strip().lower().split())
        if not normalized:
            return []
        fts_terms = re.findall(r"[A-Za-z0-9]+", normalized)
        fts_match = " ".join(f"{term}*" for term in fts_terms) if fts_terms else ""

        build_lexicon_db(db_path=DB_PATH)
        conn = sqlite3.connect(DB_PATH)
        try:
            if direction == "en_to_mir":
                exact = lookup_word_candidates(db_path=DB_PATH, english_word=normalized)
                rows = conn.execute(
                    """
                    SELECT english, mirad FROM lexicon
                    WHERE english LIKE ? OR english LIKE ?
                    ORDER BY CASE WHEN english = ? THEN 0 WHEN english LIKE ? THEN 1 ELSE 2 END, LENGTH(english), english
                    LIMIT ?
                    """,
                    (f"%{normalized}%", f"{normalized[: max(1, min(5, len(normalized)))]}%", normalized, f"{normalized}%", max(top_k * 4, 12)),
                ).fetchall()
                if not rows and fts_match:
                    try:
                        rows = conn.execute(
                            "SELECT lexicon.english, lexicon.mirad FROM lexicon_fts JOIN lexicon ON lexicon_fts.rowid = lexicon.id WHERE lexicon_fts MATCH ? LIMIT ?",
                            (fts_match, max(top_k * 4, 12)),
                        ).fetchall()
                    except sqlite3.OperationalError:
                        rows = []
                candidates = [(normalized, ", ".join(exact), True)] if exact else []
                candidates.extend((english, mirad, english == normalized) for english, mirad in rows)
                seen = set()
                payload = []
                for english, mirad, is_exact in candidates:
                    key = (english, mirad)
                    if key in seen:
                        continue
                    seen.add(key)
                    similarity = 1.0 if is_exact else max(0.5, SequenceMatcher(None, normalized, english).ratio())
                    payload.append({"english": english, "mirad": mirad, "cosine_similarity": round(similarity, 4), "is_exact": bool(is_exact)})
                    if len(payload) >= top_k:
                        break
                return payload

            exact = lookup_mirad_word_candidates(db_path=DB_PATH, mirad_word=normalized)
            rows = conn.execute(
                """
                SELECT mirad, english FROM reverse_lexicon
                WHERE mirad LIKE ? OR mirad LIKE ?
                ORDER BY CASE WHEN mirad = ? THEN 0 WHEN mirad LIKE ? THEN 1 ELSE 2 END, LENGTH(mirad), mirad
                LIMIT ?
                """,
                (f"%{normalized}%", f"{normalized[: max(1, min(5, len(normalized)))]}%", normalized, f"{normalized}%", max(top_k * 4, 12)),
            ).fetchall()
            if not rows and fts_match:
                try:
                    rows = conn.execute(
                        "SELECT reverse_lexicon.mirad, reverse_lexicon.english FROM reverse_lexicon_fts JOIN reverse_lexicon ON reverse_lexicon_fts.rowid = reverse_lexicon.id WHERE reverse_lexicon_fts MATCH ? LIMIT ?",
                        (fts_match, max(top_k * 4, 12)),
                    ).fetchall()
                except sqlite3.OperationalError:
                    rows = []
            candidates = [(normalized, ", ".join(exact), True)] if exact else []
            candidates.extend((mirad, english, mirad == normalized) for mirad, english in rows)
            seen = set()
            payload = []
            for mirad, english, is_exact in candidates:
                key = (mirad, english)
                if key in seen:
                    continue
                seen.add(key)
                similarity = 1.0 if is_exact else max(0.5, SequenceMatcher(None, normalized, mirad).ratio())
                payload.append({"mirad": mirad, "english": english, "cosine_similarity": round(similarity, 4), "is_exact": bool(is_exact)})
                if len(payload) >= top_k:
                    break
            return payload
        finally:
            conn.close()

    @app.get("/lookup/exact", tags=["lexicon"])
    def lookup_exact(
        q: str = Query(..., min_length=1),
        direction: Literal["en_to_mir", "mir_to_en"] = Query(...),
    ) -> JSONResponse:
        """Return an immediate exact-match from SQLite — no embedder needed.

        Sub-10ms response. Use this to show a result instantly while
        /lookup (semantic) is fetching in the background.
        """
        try:
            from mirad_translator.lexicon_db import lookup_word_candidates, lookup_mirad_word_candidates

            candidates: list[str]
            if direction == "en_to_mir":
                candidates = lookup_word_candidates(english_word=q)
                if candidates:
                    return JSONResponse(
                        status_code=200,
                        content=[{
                            "english": q.lower(),
                            "mirad": ", ".join(candidates),
                            "cosine_similarity": 1.0,
                            "is_exact": True,
                        }],
                    )
            else:
                candidates = lookup_mirad_word_candidates(mirad_word=q)
                if candidates:
                    return JSONResponse(
                        status_code=200,
                        content=[{
                            "mirad": q.lower(),
                            "english": ", ".join(candidates),
                            "cosine_similarity": 1.0,
                            "is_exact": True,
                        }],
                    )
            return JSONResponse(status_code=200, content=[])
        except Exception:
            return JSONResponse(status_code=200, content=[])

    @app.get("/lookup", tags=["lexicon"])
    def lookup(
        q: str = Query(..., min_length=1),
        direction: Literal["en_to_mir", "mir_to_en"] = Query(...),
        top_k: int = Query(default=3, ge=1),
    ) -> JSONResponse:
        """Return open semantic lexicon results for English or Mirad queries."""
        warmup = getattr(app.state, "semantic_warmup", {})
        if isinstance(warmup, dict) and warmup.get("status") in {"pending", "running", "error"}:
            return JSONResponse(status_code=status.HTTP_200_OK, content=fallback_lexicon_search(q, direction, top_k))

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
            payload = fallback_lexicon_search(q, direction, top_k)
            return JSONResponse(status_code=status.HTTP_200_OK, content=payload)
        except Exception:
            payload = fallback_lexicon_search(q, direction, top_k)
            return JSONResponse(status_code=status.HTTP_200_OK, content=payload)

        return JSONResponse(status_code=status.HTTP_200_OK, content=payload)

    @app.get("/auth/current-user", tags=["auth"])
    def current_user(request: Request) -> JSONResponse:
        """Return the current authenticated user or an explicit logged-out state."""
        try:
            user = resolve_current_user(request, "auth_current_user")
        except StorageError as exc:
            return storage_failure_response(exc)
        if user is None:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"authenticated": False, "user": None, "detail": "No active user session."})
        return JSONResponse(status_code=status.HTTP_200_OK, content=authenticated_payload(user))

    @app.get("/settings", tags=["settings"])
    def get_settings(request: Request) -> JSONResponse:
        """Return durable learner settings for the authenticated session."""
        user = resolve_current_user(request, "settings_get")
        if user is None:
            return unauthenticated_response("settings_get", "Login is required to view settings.")
        storage: MiraLingoStorage = request.app.state.storage
        try:
            storage.ensure_session_user(username=user.username, role=user.role, phase="settings_get")
            settings_record = storage.get_user_settings(username=user.username)
        except StorageError as exc:
            return storage_failure_response(exc)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"ok": True, "phase": "settings_get", "settings": settings_record.public_dict()})

    @app.put("/settings", tags=["settings"])
    def update_settings(request: Request, payload: UserSettingsUpdateRequest) -> JSONResponse:
        """Persist durable learner settings for the authenticated session."""
        user = resolve_current_user(request, "settings_update")
        if user is None:
            return unauthenticated_response("settings_update", "Login is required to update settings.")
        storage: MiraLingoStorage = request.app.state.storage
        try:
            storage.ensure_session_user(username=user.username, role=user.role, phase="settings_update")
            settings_record = storage.upsert_user_settings(
                username=user.username,
                theme=payload.theme,
                tts_speed=payload.tts_speed,
                tts_autoplay=payload.tts_autoplay,
                sfx_enabled=payload.sfx_enabled,
                sfx_mode=payload.sfx_mode,
            )
        except StorageError as exc:
            return storage_failure_response(exc)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"ok": True, "phase": "settings_update", "settings": settings_record.public_dict()})

    @app.post("/auth/register", tags=["auth"])
    def register(request: Request, registration: RegisterRequest) -> JSONResponse:
        """Register an email account in durable SQLite storage and log it in."""
        storage: MiraLingoStorage = request.app.state.storage
        try:
            if registration.email:
                user, error_payload, error_status = storage.register_account(
                    email=registration.email,
                    name=registration.name or registration.nickname,
                    password=registration.password,
                )
            else:
                user, error_payload, error_status = storage.register_account(
                    username=registration.username,
                    password=registration.password,
                )
        except StorageError as exc:
            return storage_failure_response(exc)
        if user is None:
            return JSONResponse(status_code=error_status or 400, content=error_payload or {})
        return create_login_response(user, status_code=status.HTTP_201_CREATED)

    @app.post("/auth/login", tags=["auth"])
    def login(request: Request, credentials: LoginRequest) -> JSONResponse:
        """Log in as either a registered learner or guarded development local admin."""
        storage: MiraLingoStorage = request.app.state.storage
        candidate_email = credentials.email or credentials.username or ""
        if candidate_email.strip().lower() in {LOCAL_ADMIN_EMAIL, LOCAL_ADMIN_USERNAME}:
            user, error_payload, error_status = authenticate_local_admin(email=credentials.email, username=credentials.username, password=credentials.password, settings=runtime_settings)
            if user is None:
                return JSONResponse(status_code=error_status or 401, content=error_payload or {})
            try:
                storage.ensure_session_user(username=user.username, role=user.role, phase="auth_login")
            except StorageError as exc:
                return storage_failure_response(exc)
            return create_login_response(user)

        try:
            registered_user = storage.authenticate_account(email=credentials.email, username=credentials.username, password=credentials.password)
        except StorageError as exc:
            return storage_failure_response(exc)
        if registered_user is None:
            error_payload, error_status = registered_login_error()
            return JSONResponse(status_code=error_status, content=error_payload)
        return create_login_response(registered_user)

    @app.post("/auth/logout", tags=["auth"])
    def logout(request: Request) -> JSONResponse:
        """Revoke the current opaque server-side session."""
        storage: MiraLingoStorage = request.app.state.storage
        try:
            storage.revoke_session(raw_token=session_token_from_request(request), secret=runtime_settings.session_secret)
        except StorageError as exc:
            return storage_failure_response(exc)
        response = JSONResponse(status_code=status.HTTP_200_OK, content={"authenticated": False})
        clear_session_cookie(response)
        return response

    @app.delete("/auth/account", tags=["auth"])
    def delete_account(request: Request, payload: DeleteAccountRequest) -> JSONResponse:
        """Delete the current learner account after explicit confirmation."""
        user = resolve_current_user(request, "account_delete")
        if user is None:
            return unauthenticated_response("account_delete", "Login is required to delete the current account.")
        if user.role == ADMIN_ROLE or user.id in {"local-admin", LOCAL_ADMIN_USERNAME}:
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"ok": False, "error": "protected_account", "phase": "account_delete", "detail": "The local admin account cannot be deleted."})
        expected_confirmation = f"{user.email} DELETE"
        payload_email = normalize_email(payload.email or payload.username or "")
        if payload.confirmation.strip() != expected_confirmation or payload_email != user.email:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"ok": False, "error": "invalid_confirmation", "phase": "account_delete", "detail": "Account deletion requires the current email plus the exact confirmation phrase '<email> DELETE'."},
            )
        storage: MiraLingoStorage = request.app.state.storage
        try:
            storage.delete_user_account(user_id=user.id)
        except StorageError as exc:
            status_code = status.HTTP_403_FORBIDDEN if exc.error == "protected_account" else status.HTTP_503_SERVICE_UNAVAILABLE
            return storage_failure_response(exc, status_code=status_code)
        response = JSONResponse(status_code=status.HTTP_200_OK, content={"ok": True, "phase": "account_delete", "deleted_email": user.email, "authenticated": False})
        clear_session_cookie(response)
        return response

    @app.post("/auth/password/forgot", tags=["auth"])
    def password_forgot(request: Request, payload: PasswordForgotRequest) -> JSONResponse:
        """Create a password reset token without revealing whether the email exists."""
        storage: MiraLingoStorage = request.app.state.storage
        dev_reset_url = None
        try:
            token = storage.create_password_reset_token(email=payload.email, secret=runtime_settings.session_secret, ttl_seconds=runtime_settings.password_reset_ttl_seconds)
        except StorageError as exc:
            return storage_failure_response(exc)
        if token and runtime_settings.environment == "development" and runtime_settings.enable_dev_password_reset_logging:
            dev_reset_url = f"{runtime_settings.frontend_base_url}/?reset_token={token}"
        content: dict[str, Any] = {"ok": True, "phase": "password_forgot", "detail": "If an account exists, reset instructions have been sent."}
        if dev_reset_url:
            content["dev_reset_url"] = dev_reset_url
        return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=content)

    @app.post("/auth/password/reset", tags=["auth"])
    def password_reset(request: Request, payload: PasswordResetRequest) -> JSONResponse:
        """Consume a single-use password reset token."""
        storage: MiraLingoStorage = request.app.state.storage
        try:
            user, error_payload, error_status = storage.register_account(email="reset-probe@example.invalid", password=payload.password)
            if user is not None:
                storage.delete_user_account(user_id=user.id)
        except StorageError:
            error_payload, error_status = None, None
        if error_payload and error_payload.get("error") == "invalid_password":
            return JSONResponse(status_code=error_status or 400, content={**error_payload, "phase": "password_reset"})
        try:
            reset_user = storage.reset_password_with_token(raw_token=payload.token, new_password=payload.password, secret=runtime_settings.session_secret)
        except StorageError as exc:
            return storage_failure_response(exc)
        if reset_user is None:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"ok": False, "error": "invalid_reset_token", "phase": "password_reset", "detail": "Password reset token is invalid, expired, or already used."})
        response = JSONResponse(status_code=status.HTTP_200_OK, content={"ok": True, "phase": "password_reset", "authenticated": False})
        clear_session_cookie(response)
        return response

    @app.get("/auth/google/login", tags=["auth"])
    def google_login(request: Request, next: str = Query(default="/")) -> Response:
        """Start Google OAuth/OIDC sign-in."""
        if not runtime_settings.google_oauth_configured:
            return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"ok": False, "error": "google_oauth_unconfigured", "phase": "auth_google_login", "detail": "Google sign-in is not configured."})
        state_token = new_public_token()
        try:
            request.app.state.storage.create_oauth_state(state=state_token, secret=runtime_settings.session_secret, ttl_seconds=600, next_path=next)
        except StorageError as exc:
            return storage_failure_response(exc)
        params = urlencode(
            {
                "client_id": runtime_settings.google_client_id,
                "redirect_uri": runtime_settings.google_redirect_uri,
                "response_type": "code",
                "scope": "openid email profile",
                "state": state_token,
                "access_type": "offline",
                "prompt": "select_account",
            }
        )
        return RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{params}")

    @app.get("/auth/google/callback", tags=["auth"])
    async def google_callback(request: Request, code: str = Query(default=""), state: str = Query(default="")) -> Response:
        """Finish Google OAuth/OIDC sign-in and create the normal opaque session."""
        if not runtime_settings.google_oauth_configured:
            return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"ok": False, "error": "google_oauth_unconfigured", "phase": "auth_google_callback", "detail": "Google sign-in is not configured."})
        if not code or not state:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"ok": False, "error": "invalid_google_callback", "phase": "auth_google_callback", "detail": "Google callback is missing code or state."})
        storage: MiraLingoStorage = request.app.state.storage
        try:
            next_path = storage.consume_oauth_state(state=state, secret=runtime_settings.session_secret)
        except StorageError as exc:
            return storage_failure_response(exc)
        if next_path is None:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"ok": False, "error": "invalid_oauth_state", "phase": "auth_google_callback", "detail": "OAuth state is invalid, expired, or already used."})
        try:
            from authlib.integrations.httpx_client import AsyncOAuth2Client
        except ImportError:
            return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"ok": False, "error": "authlib_missing", "phase": "auth_google_callback", "detail": "Google sign-in requires the authlib package."})
        try:
            oauth_client = AsyncOAuth2Client(
                client_id=runtime_settings.google_client_id,
                client_secret=runtime_settings.google_client_secret,
                redirect_uri=runtime_settings.google_redirect_uri,
                scope="openid email profile",
            )
            await oauth_client.fetch_token(
                "https://oauth2.googleapis.com/token",
                code=code,
                grant_type="authorization_code",
            )
            profile_response = await oauth_client.get("https://openidconnect.googleapis.com/v1/userinfo")
            if profile_response.status_code != status.HTTP_200_OK:
                return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"ok": False, "error": "invalid_google_profile", "phase": "auth_google_callback", "detail": "Google sign-in did not return a usable user profile."})
            profile = profile_response.json()
        except Exception:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"ok": False, "error": "invalid_google_token", "phase": "auth_google_callback", "detail": "Google sign-in failed token exchange."})
        if not profile.get("email_verified"):
            return forbidden_response("auth_google_callback", "Google email must be verified.")
        try:
            user = storage.upsert_google_user(email=str(profile.get("email") or ""), google_sub=str(profile.get("sub") or ""), name=profile.get("name"), email_verified=True)
        except StorageError as exc:
            return storage_failure_response(exc, status_code=status.HTTP_400_BAD_REQUEST)
        response = RedirectResponse(f"{runtime_settings.frontend_base_url}{next_path}")
        raw_token, expires_at = storage.create_session(user_id=user.id, secret=runtime_settings.session_secret, ttl_seconds=runtime_settings.session_ttl_seconds)
        set_session_cookie(response, raw_token, expires_at)
        return response

    @app.get("/practice/queue", tags=["practice"])
    def practice_queue(
        request: Request,
        limit: int = Query(default=10, ge=1, le=50),
        mode: Literal["mixed", "revision", "build_vocabulary"] = Query(default="mixed"),
    ) -> JSONResponse:
        """Return an adaptive practice queue for the authenticated session."""
        user = resolve_current_user(request, "auth_session")
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
            lifecycle_rows = [row.public_dict() for row in request.app.state.storage.list_practice_lifecycle(username=user.username)]
            exposure_by_item = request.app.state.storage.exposure_summary(username=user.username)
            payload = build_practice_queue(
                cards=result.cards,
                events=events,
                lifecycle_rows=lifecycle_rows,
                exposure_by_item=exposure_by_item,
                limit=limit,
                mode=mode,
            )
            if payload.get("ok") and mode == "build_vocabulary":
                seen_keys = request.app.state.storage.list_shown_card_keys(username=user.username)
                seen_base_ids = {base_card_id for base_card_id, _direction in seen_keys}
                for card in payload.get("cards", []):
                    base_card_id = str(card.get("base_card_id") or "")
                    card["intro_mode"] = base_card_id not in seen_base_ids
            request.app.state.storage.record_cards_shown(username=user.username, cards=payload["cards"])
        except StorageError as exc:
            return storage_failure_response(exc)
        return JSONResponse(status_code=status.HTTP_200_OK, content=payload)

    @app.get("/practice/analytics", tags=["practice"])
    def practice_analytics(
        request: Request,
        window_days: int = Query(default=30, ge=0, le=365),
        include_cards: bool = Query(default=False),
    ) -> JSONResponse:
        """Return compact+drilldown analytics for authenticated learner history."""
        user = resolve_current_user(request, "auth_session")
        if user is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "ok": False,
                    "error": "unauthenticated",
                    "phase": "practice_analytics",
                    "detail": "Login is required to request practice analytics.",
                },
            )
        try:
            result = imported_card_content()
        except CardContentSourceMissingError as exc:
            payload = error_to_payload(exc)
            payload["practice_phase"] = "practice_analytics"
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=payload)
        except CardContentImportError as exc:
            payload = error_to_payload(exc)
            payload["practice_phase"] = "practice_analytics"
            return JSONResponse(status_code=status.HTTP_502_BAD_GATEWAY, content=payload)

        try:
            ensure_practice_storage_user("practice_analytics", user.username, user.role)
            storage = request.app.state.storage
            events = [record.practice_event() for record in storage.list_answer_events(username=user.username, limit=None, phase="practice_analytics")]
            sessions = [s.public_dict() for s in storage.list_practice_sessions(username=user.username, phase="practice_analytics")]
            lifecycle_rows = [row.public_dict() for row in storage.list_practice_lifecycle(username=user.username)]
            shown_cards = [row.public_dict() for row in storage.list_shown_cards(username=user.username)] if include_cards else []
            payload = build_practice_analytics(
                cards=result.cards,
                events=events,
                sessions=sessions,
                lifecycle_rows=lifecycle_rows,
                shown_cards=shown_cards,
                filters={"window_days": window_days, "include_cards": include_cards},
            )
        except StorageError as exc:
            return storage_failure_response(exc)
        return JSONResponse(status_code=status.HTTP_200_OK, content=payload)

    @app.get("/practice/summary", tags=["practice"])
    def practice_summary(request: Request) -> JSONResponse:
        """Return fast dashboard practice metrics without full card expansion."""
        user = resolve_current_user(request, "auth_session")
        if user is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "ok": False,
                    "error": "unauthenticated",
                    "phase": "practice_summary",
                    "detail": "Login is required to request practice summary.",
                },
            )
        try:
            ensure_practice_storage_user("practice_summary", user.username, user.role)
            payload = request.app.state.storage.practice_summary(username=user.username)
        except StorageError as exc:
            return storage_failure_response(exc)
        return JSONResponse(status_code=status.HTTP_200_OK, content=payload)

    @app.get("/practice/progress", tags=["practice"])
    def practice_progress(request: Request) -> JSONResponse:
        """Return progress diagnostics for the authenticated session's bounded practice history."""
        user = resolve_current_user(request, "auth_session")
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

    def _require_practice_session_user(request: Request) -> tuple[Any, JSONResponse | None]:
        user = resolve_current_user(request, "auth_session")
        if user is None:
            return None, JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "ok": False,
                    "error": "unauthenticated",
                    "phase": "practice_session",
                    "detail": "Login is required to inspect practice sessions.",
                },
            )
        return user, None

    @app.get("/practice/sessions", tags=["practice"])
    def practice_sessions(request: Request) -> JSONResponse:
        """Return active durable session diagnostics for authenticated learners."""
        user, error_response = _require_practice_session_user(request)
        if error_response is not None:
            return error_response
        try:
            ensure_practice_storage_user("practice_session", user.username, user.role)
            active = request.app.state.storage.get_or_start_active_practice_session(username=user.username)
        except StorageError as exc:
            return storage_failure_response(exc)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"ok": True, "phase": "practice_session", "active_session": active})

    @app.post("/practice/sessions/start", tags=["practice"])
    def practice_sessions_start(request: Request) -> JSONResponse:
        """Idempotently continue or start an authenticated practice session."""
        user, error_response = _require_practice_session_user(request)
        if error_response is not None:
            return error_response
        try:
            ensure_practice_storage_user("practice_session", user.username, user.role)
            active = request.app.state.storage.get_or_start_active_practice_session(username=user.username)
        except StorageError as exc:
            return storage_failure_response(exc)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"ok": True, "phase": "practice_session", "active_session": active})

    @app.post("/practice/sessions/end", tags=["practice"])
    def practice_sessions_end(request: Request) -> JSONResponse:
        """End the current authenticated practice session if one is active."""
        user, error_response = _require_practice_session_user(request)
        if error_response is not None:
            return error_response
        try:
            ensure_practice_storage_user("practice_session", user.username, user.role)
            ended = request.app.state.storage.end_active_practice_session(username=user.username)
        except StorageError as exc:
            return storage_failure_response(exc)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"ok": True, "phase": "practice_session", "active_session": None, "ended_session": ended},
        )

    @app.get("/practice/audio/{card_id:path}", tags=["practice"])
    def practice_audio(request: Request, card_id: str):
        """Return MBROLA WAV audio for one authenticated configured practice card."""
        user = resolve_current_user(request, "auth_session")
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
        user = resolve_current_user(request, "auth_session")
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
        user = resolve_current_user(request, "auth_session")
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
            session = request.app.state.storage.get_or_start_active_practice_session(username=user.username)
            request.app.state.storage.record_practice_lifecycle_answer(
                username=user.username,
                session_id=str(session["session_id"]),
                base_card_id=str(latest_event["base_card_id"]),
                direction=str(latest_event["direction"]),
                correct=bool(latest_event["correct"]),
                card_id=str(latest_event["card_id"]),
                card_type=str(latest_event["card_type"]),
                submitted_answer=str(latest_event["submitted_answer"]),
                expected_answer=str(latest_event["expected_answer"]),
                answered_at=latest_event.get("answered_at"),
            )
            durable_events = answer_events_for_user(user.username, "practice_answer")
        except StorageError as exc:
            return storage_failure_response(exc)
        payload = answer_summary(result.cards, durable_events, submission.card_id)
        display_name = _achievement_display_name(user)
        lifecycle_rows_for_achievements = [row.public_dict() for row in request.app.state.storage.list_practice_lifecycle(username=user.username)]
        payload["achievements"] = build_practice_achievements(
            cards=result.cards,
            before_events=prior_events,
            after_events=durable_events,
            username=display_name,
            latest_card_id=submission.card_id,
            lifecycle_rows=lifecycle_rows_for_achievements,
        )
        return JSONResponse(status_code=status.HTTP_200_OK, content=payload)

    return app


app = create_app()
