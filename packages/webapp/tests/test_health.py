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
    assert "MiraLingo" in contents
    assert "Practice Mirad pronunciation and translation." in contents
    assert "Create account" in contents
    assert "Log in" in contents


def test_frontend_auth_states_and_error_copy_are_wired() -> None:
    app_source = Path(__file__).parents[1] / "frontend" / "src" / "App.svelte"

    contents = app_source.read_text(encoding="utf-8")
    assert 'fetch("/auth/current-user"' in contents
    assert 'fetch("/auth/login"' in contents
    assert 'fetch("/auth/register"' in contents
    assert 'fetch("/auth/logout"' in contents
    assert 'authState="anonymous"' in contents
    assert 'authState="login-failed"' in contents
    assert 'authState="registration-failed"' in contents
    assert 'authState="authenticated"' in contents
    assert "Could not reach MiraLingo auth" in contents
    assert 'role="alert"' in contents


def test_frontend_stylesheet_defines_responsive_app_home() -> None:
    frontend_src = Path(__file__).parents[1] / "frontend" / "src"
    app_source = (frontend_src / "App.svelte").read_text(encoding="utf-8")
    css_source = frontend_src / "app.css"

    assert 'import "./app.css";' in app_source
    assert css_source.exists()
    contents = css_source.read_text(encoding="utf-8")
    assert ".hero-title" in contents
    assert ".auth-card" in contents
    assert ".pcard-main" in contents


def test_frontend_registration_source_affordance_is_wired() -> None:
    app_source = Path(__file__).parents[1] / "frontend" / "src" / "App.svelte"

    contents = app_source.read_text(encoding="utf-8")
    assert 'async function submitRegistration()' in contents
    assert 'fetch("/auth/register", {' in contents
    assert '"Content-Type":"application/json"' in contents
    assert "username:regU" in contents
    registration_body = contents.split("async function submitRegistration()", maxsplit=1)[1].split("async function", maxsplit=1)[0]
    assert 'activeSection="menu"' in registration_body
    assert 'await loadSettings({force:true});' in registration_body
    logout_body = contents.split("async function logout()", maxsplit=1)[1].split("// ── settings", maxsplit=1)[0]
    assert 'clearAuthAppState()' in logout_body
    assert 'resetPracticeSurface()' in logout_body
    assert 'resetSettingsSurface()' in logout_body


def test_frontend_practice_direction_labels_are_helper_based() -> None:
    app_source = Path(__file__).parents[1] / "frontend" / "src" / "App.svelte"

    contents = app_source.read_text(encoding="utf-8")
    assert 'activeSection === "practice"' in contents
    assert 'const langLabel = (l) =>' in contents
    assert 'const promptTag = (c) =>' in contents
    assert 'const answerTag = (c) =>' in contents
    assert 'const inputLabel = (c) =>' in contents
    assert 'const isEnMir = (c) =>' in contents
    assert 'class="pcard-lang"' in contents
    assert 'class="pcard-main"' in contents
