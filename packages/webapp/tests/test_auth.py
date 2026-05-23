from fastapi.testclient import TestClient

from mirad_webapp.api import create_app
from mirad_webapp.config import Settings


def test_local_admin_can_login_in_development() -> None:
    client = TestClient(create_app(Settings(environment="development", enable_local_admin=True)))

    response = client.post("/auth/login", json={"username": "admin", "password": "admin"})

    assert response.status_code == 200
    assert response.json() == {
        "authenticated": True,
        "user": {"username": "admin", "role": "admin"},
    }

    current_user = client.get("/auth/current-user")
    assert current_user.status_code == 200
    assert current_user.json() == {
        "authenticated": True,
        "user": {"username": "admin", "role": "admin"},
    }


def test_invalid_credentials_return_structured_error_without_echoing_password() -> None:
    client = TestClient(create_app(Settings(environment="development", enable_local_admin=True)))

    response = client.post("/auth/login", json={"username": "admin", "password": "wrong"})

    assert response.status_code == 401
    body = response.json()
    assert body == {
        "authenticated": False,
        "error": "invalid_credentials",
        "detail": "Invalid username or password.",
    }
    assert "wrong" not in response.text


def test_current_user_reports_logged_out_without_session() -> None:
    client = TestClient(create_app(Settings(environment="development", enable_local_admin=True)))

    response = client.get("/auth/current-user")

    assert response.status_code == 401
    assert response.json() == {
        "authenticated": False,
        "user": None,
        "detail": "No active user session.",
    }


def test_local_admin_login_refused_when_development_bootstrap_disabled() -> None:
    client = TestClient(create_app(Settings(environment="production", enable_local_admin=True)))

    response = client.post("/auth/login", json={"username": "admin", "password": "admin"})

    assert response.status_code == 403
    assert response.json() == {
        "authenticated": False,
        "error": "local_admin_disabled",
        "detail": "Local admin bootstrap is disabled for this environment.",
    }
    assert "password" not in response.text


def test_logout_clears_authenticated_session() -> None:
    client = TestClient(create_app(Settings(environment="development", enable_local_admin=True)))
    assert client.post("/auth/login", json={"username": "admin", "password": "admin"}).status_code == 200

    logout = client.post("/auth/logout")

    assert logout.status_code == 200
    assert logout.json() == {"authenticated": False}
    current_user = client.get("/auth/current-user")
    assert current_user.status_code == 401
