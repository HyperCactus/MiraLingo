from pathlib import Path
import warnings

from fastapi.testclient import TestClient

from mirad_webapp.api import create_app
from mirad_webapp.config import Settings


FRONTEND_SRC = Path(__file__).parents[1] / "frontend" / "src"


def _source(*parts: str) -> str:
    return (FRONTEND_SRC.joinpath(*parts)).read_text(encoding="utf-8")


def test_health_reports_ok() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "mirad-webapp"
    assert "semantic_warmup" in payload
    assert payload["email_delivery"]["configured"] is False
    assert "last_result" not in payload["email_delivery"]


def test_health_reports_email_delivery_configuration(tmp_path: Path) -> None:
    client = TestClient(
        create_app(
            Settings(
                database_path=tmp_path / "miralingo.sqlite3",
                email_provider="resend",
                email_from="MiraLingo <noreply@example.com>",
                resend_api_key="re_test_secret",
            )
        )
    )

    response = client.get("/health")

    payload = response.json()["email_delivery"]
    assert payload["provider"] == "resend"
    assert payload["configured"] is True
    assert "re_test_secret" not in response.text


def test_lookup_fallback_handles_punctuation_without_500() -> None:
    app = create_app()
    app.state.semantic_warmup = {"status": "running"}
    client = TestClient(app)

    for query, direction in (("can't", "mir_to_en"), ("x:y", "en_to_mir"), ("100", "en_to_mir")):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            response = client.get("/lookup", params={"q": query, "direction": direction, "top_k": 3})

        assert response.status_code == 200
        assert isinstance(response.json(), list)


def test_current_user_reports_logged_out_without_session() -> None:
    client = TestClient(create_app())

    response = client.get("/auth/current-user")

    assert response.status_code == 401
    assert response.json() == {
        "authenticated": False,
        "user": None,
        "detail": "No active user session.",
    }


def test_frontend_welcome_text_is_present() -> None:
    app = _source("App.svelte")
    welcome = _source("lib", "pages", "Welcome.svelte")

    assert "MiraLingo" in app
    assert "Build confidence in Mirad with focused daily practice." in welcome
    assert "MiraLingo helps you practice Mirad" in welcome
    assert "Create Account" in welcome
    assert "Log In" in welcome


def test_frontend_auth_states_and_error_copy_are_wired() -> None:
    app = _source("App.svelte")
    auth_api = _source("lib", "api", "auth.ts")

    assert "fetch('/auth/current-user'" in auth_api
    assert "fetch('/auth/login'" in auth_api
    assert "fetch('/auth/register'" in auth_api
    assert "fetch('/auth/logout'" in auth_api
    assert 'setAuthFailure("login-failed"' in app
    assert 'setAuthFailure("registration-failed"' in app
    assert "setAuthenticated(payload.user)" in app
    assert "Could not reach MiraLingo auth" in app
    assert "authMessage.set(payload?.detail" in app
    forgot_body = app.split("async function submitPasswordResetRequest()", maxsplit=1)[1].split("async function", maxsplit=1)[0]
    assert "const email = loginEmail.trim();" in forgot_body
    assert "registrationEmail" not in forgot_body
    assert 'role="alert"' in _source("lib", "pages", "Welcome.svelte")
    assert 'role="status"' in _source("lib", "pages", "Welcome.svelte")


def test_frontend_stylesheet_defines_responsive_app_home() -> None:
    app_source = _source("App.svelte")
    css = _source("app.css")

    assert 'import "./app.css";' in app_source
    assert ".hero-title" in css
    assert ".auth-card" in css
    assert ".pcard-main" in css


def test_frontend_registration_source_affordance_is_wired() -> None:
    app = _source("App.svelte")
    auth_api = _source("lib", "api", "auth.ts")

    assert "async function submitRegistration()" in app
    assert "fetch('/auth/register'" in auth_api
    assert "'Content-Type': 'application/json'" in auth_api
    assert "register(registrationEmail, regP, registrationName)" in app
    registration_body = app.split("async function submitRegistration()", maxsplit=1)[1].split("async function", maxsplit=1)[0]
    assert 'syncRouteFromHash("dashboard")' in app or 'replaceHash("dashboard")' in registration_body
    assert "await loadSettings({ force: true });" in registration_body
    logout_body = app.split("async function logout()", maxsplit=1)[1].split("async function", maxsplit=1)[0]
    assert "clearAuthAppState()" in logout_body
    assert "resetAnalyticsSurface" not in logout_body
    assert "resetPracticeSurface();" in app
    assert "resetSettingsSurface();" in app


def test_frontend_practice_direction_labels_are_helper_based() -> None:
    app = _source("App.svelte")
    exercise = _source("lib", "components", "learning", "ExerciseCard.svelte")
    prompt = _source("lib", "components", "learning", "ExercisePrompt.svelte")

    assert 'section === "practice"' in app
    assert "languageLabel" in exercise
    assert "inputLabel" in exercise
    assert "promptEyebrow" in exercise
    assert "eyebrow" in prompt
    assert "ClickableTranslationText" in prompt
