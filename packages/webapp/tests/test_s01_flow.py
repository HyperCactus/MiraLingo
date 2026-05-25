from pathlib import Path

from fastapi.testclient import TestClient

from mirad_webapp.api import create_app
from mirad_webapp.config import Settings


FRONTEND_APP = Path(__file__).parents[1] / "frontend" / "src" / "App.svelte"


def test_s01_logged_out_welcome_surface_is_backed_by_explicit_auth_state() -> None:
    client = TestClient(create_app(Settings(environment="development", enable_local_admin=True)))

    health = client.get("/health")
    current_user = client.get("/auth/current-user")
    frontend_source = FRONTEND_APP.read_text(encoding="utf-8")

    assert health.status_code == 200
    assert health.json() == {"status": "ok", "service": "mirad-webapp"}
    assert current_user.status_code == 401
    assert current_user.json() == {
        "authenticated": False,
        "user": None,
        "detail": "No active user session.",
    }
    assert "MiraLingo" in frontend_source
    assert "Practice Mirad pronunciation and translation." in frontend_source
    assert 'authState="anonymous"' in frontend_source


def test_s01_local_admin_login_reaches_app_home_and_logout_returns_to_logged_out_state() -> None:
    client = TestClient(create_app(Settings(environment="development", enable_local_admin=True)))

    login = client.post("/auth/login", json={"username": "admin", "password": "admin"})
    current_user = client.get("/auth/current-user")
    logout = client.post("/auth/logout")
    logged_out_again = client.get("/auth/current-user")
    frontend_source = FRONTEND_APP.read_text(encoding="utf-8")

    assert login.status_code == 200
    assert login.json() == {
        "authenticated": True,
        "user": {"username": "admin", "role": "admin"},
    }
    assert current_user.status_code == 200
    assert current_user.json() == {
        "authenticated": True,
        "user": {"username": "admin", "role": "admin"},
    }
    assert logout.status_code == 200
    assert logout.json() == {"authenticated": False}
    assert logged_out_again.status_code == 401
    assert "Welcome back" in frontend_source
    assert "Continue Practice" in frontend_source


def test_s01_admin_bootstrap_is_refused_outside_development_without_password_echo() -> None:
    client = TestClient(create_app(Settings(environment="production", enable_local_admin=True)))

    response = client.post("/auth/login", json={"username": "admin", "password": "admin"})

    assert response.status_code == 403
    assert response.json() == {
        "authenticated": False,
        "error": "local_admin_disabled",
        "detail": "Local admin bootstrap is disabled for this environment.",
    }
    assert "password" not in response.text
    assert "admin/admin" not in response.text


def test_s01_malformed_login_body_returns_validation_error_without_session() -> None:
    client = TestClient(create_app(Settings(environment="development", enable_local_admin=True)))

    response = client.post("/auth/login", json={"username": "admin"})
    current_user = client.get("/auth/current-user")

    assert response.status_code == 422
    assert current_user.status_code == 401
    assert current_user.json()["authenticated"] is False
