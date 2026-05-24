from pathlib import Path

from fastapi.testclient import TestClient

from mirad_webapp.api import create_app


def test_health_reports_ok() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "mirad-webapp"}


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
    app_source = Path(__file__).parents[1] / "frontend" / "src" / "App.svelte"

    assert app_source.exists()
    contents = app_source.read_text(encoding="utf-8")
    assert "Welcome to MiraLingo" in contents
    assert "Mirad pronunciation, translation, and vocabulary" in contents
    assert "Create account" in contents
    assert "../../README.md" in contents


def test_frontend_auth_states_and_error_copy_are_wired() -> None:
    app_source = Path(__file__).parents[1] / "frontend" / "src" / "App.svelte"

    contents = app_source.read_text(encoding="utf-8")
    assert 'fetch("/auth/current-user"' in contents
    assert 'fetch("/auth/login"' in contents
    assert 'fetch("/auth/register"' in contents
    assert 'fetch("/auth/logout"' in contents
    assert 'authState = "anonymous"' in contents
    assert 'authState = "login-failed"' in contents
    assert 'authState = "registration-failed"' in contents
    assert 'authState = "authenticated"' in contents
    assert "Invalid username or password." in contents
    assert "Could not reach MiraLingo auth" in contents
    assert 'role="alert"' in contents


def test_frontend_stylesheet_defines_responsive_app_home() -> None:
    frontend_src = Path(__file__).parents[1] / "frontend" / "src"
    app_source = (frontend_src / "App.svelte").read_text(encoding="utf-8")
    css_source = frontend_src / "app.css"

    assert 'import "./app.css";' in app_source
    assert css_source.exists()
    contents = css_source.read_text(encoding="utf-8")
    assert ".welcome-shell" in contents
    assert ".home-panel" in contents
    assert "@media (max-width: 820px)" in contents


def test_frontend_registration_source_affordance_is_wired() -> None:
    app_source = Path(__file__).parents[1] / "frontend" / "src" / "App.svelte"

    contents = app_source.read_text(encoding="utf-8")
    logged_out_branch = contents.split("{:else}", maxsplit=1)[1]
    logout_body = contents.split("async function logout()", maxsplit=1)[1].split("async function loadPracticeProgress", maxsplit=1)[0]

    assert 'async function submitRegistration()' in contents
    assert 'fetch("/auth/register", {' in contents
    assert '"Content-Type": "application/json"' in contents
    assert 'body: JSON.stringify({ username: registerUsername, password: registerPassword })' in contents
    assert 'await loadPracticeQueue();' in contents.split("async function submitRegistration()", maxsplit=1)[1].split("async function logout", maxsplit=1)[0]
    assert 'aria-label="Learner registration"' in logged_out_branch
    assert 'autocomplete="new-password"' in logged_out_branch
    assert 'Passwords are never echoed in errors.' in logged_out_branch
    assert 'registerUsername = "";' in logout_body
    assert 'registerPassword = "";' in logout_body
    assert 'username = "admin";' in logout_body


def test_frontend_practice_direction_labels_are_helper_based() -> None:
    app_source = Path(__file__).parents[1] / "frontend" / "src" / "App.svelte"

    contents = app_source.read_text(encoding="utf-8")
    authenticated_branch = contents.split('{#if authState === "authenticated"}', maxsplit=1)[1].split("{:else}", maxsplit=1)[0]

    assert 'const languageLabel = (language) =>' in contents
    assert 'const directionLabel = (card) =>' in contents
    assert 'const promptLabel = (card) =>' in contents
    assert 'const answerLabel = (card) =>' in contents
    assert 'return "practice";' in contents
    assert 'Direction: {directionLabel(currentCard)}' in authenticated_branch
    assert '{promptLabel(currentCard)}' in authenticated_branch
    assert 'Show {answerLabel(currentCard)}' in authenticated_branch
    assert 'English prompt' not in authenticated_branch
    assert 'Show Mirad answer' not in authenticated_branch
