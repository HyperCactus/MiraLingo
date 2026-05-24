from pathlib import Path

from fastapi.testclient import TestClient

from mirad_webapp.api import create_app
from mirad_webapp.config import Settings


def assert_no_secret_material(response_text: str, *secrets: str) -> None:
    for secret in secrets:
        assert secret not in response_text
    assert "password_hash" not in response_text


def _settings(tmp_path: Path, **overrides) -> Settings:
    values = {"environment": "development", "enable_local_admin": True, "database_path": tmp_path / "miralingo.sqlite3"}
    values.update(overrides)
    return Settings(**values)


def test_local_admin_can_login_in_development(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))

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


def test_register_logs_in_learner_then_logout_and_login_restore_session(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))
    password = "learner-password-1"

    registration = client.post("/auth/register", json={"username": " Mira ", "password": password})

    assert registration.status_code == 201
    assert registration.json() == {
        "authenticated": True,
        "user": {"username": "mira", "role": "learner"},
    }
    assert_no_secret_material(registration.text, password)

    current_user = client.get("/auth/current-user")
    assert current_user.status_code == 200
    assert current_user.json() == {
        "authenticated": True,
        "user": {"username": "mira", "role": "learner"},
    }

    logout = client.post("/auth/logout")
    assert logout.status_code == 200
    assert logout.json() == {"authenticated": False}
    assert client.get("/auth/current-user").status_code == 401

    login = client.post("/auth/login", json={"username": "MIRA", "password": password})
    assert login.status_code == 200
    assert login.json() == {
        "authenticated": True,
        "user": {"username": "mira", "role": "learner"},
    }
    assert_no_secret_material(login.text, password)


def test_registration_validation_errors_do_not_create_sessions_or_accounts(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))

    missing_password = client.post("/auth/register", json={"username": "mira"})
    assert missing_password.status_code == 422
    assert client.get("/auth/current-user").status_code == 401

    empty_username = client.post("/auth/register", json={"username": "  ", "password": "valid-pass"})
    assert empty_username.status_code == 400
    assert empty_username.json() == {
        "authenticated": False,
        "error": "invalid_username",
        "phase": "auth_register",
        "detail": "Username must be at least 3 characters.",
    }

    short_password = client.post("/auth/register", json={"username": "mira", "password": "short"})
    assert short_password.status_code == 400
    assert short_password.json() == {
        "authenticated": False,
        "error": "invalid_password",
        "phase": "auth_register",
        "detail": "Password must be at least 8 characters.",
    }
    assert_no_secret_material(short_password.text, "short")

    failed_login = client.post("/auth/login", json={"username": "mira", "password": "valid-pass"})
    assert failed_login.status_code == 401
    assert failed_login.json() == {
        "authenticated": False,
        "error": "invalid_credentials",
        "phase": "auth_login",
        "detail": "Invalid username or password.",
    }


def test_duplicate_registration_is_rejected_without_replacing_password(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))
    original_password = "original-password"
    duplicate_password = "duplicate-password"
    assert (
        client.post("/auth/register", json={"username": "mira", "password": original_password}).status_code
        == 201
    )
    client.post("/auth/logout")

    duplicate = client.post("/auth/register", json={"username": "MIRA", "password": duplicate_password})

    assert duplicate.status_code == 409
    assert duplicate.json() == {
        "authenticated": False,
        "error": "username_unavailable",
        "phase": "auth_register",
        "detail": "Username is already registered.",
    }
    assert_no_secret_material(duplicate.text, duplicate_password)

    replaced_login = client.post("/auth/login", json={"username": "mira", "password": duplicate_password})
    assert replaced_login.status_code == 401
    original_login = client.post("/auth/login", json={"username": "mira", "password": original_password})
    assert original_login.status_code == 200


def test_reserved_admin_registration_is_rejected(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))
    password = "learner-password-1"

    response = client.post("/auth/register", json={"username": " admin ", "password": password})

    assert response.status_code == 400
    assert response.json() == {
        "authenticated": False,
        "error": "reserved_username",
        "phase": "auth_register",
        "detail": "The admin username is reserved.",
    }
    assert_no_secret_material(response.text, password)


def test_wrong_registered_user_password_returns_structured_error_without_secret_echo(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))
    assert (
        client.post("/auth/register", json={"username": "mira", "password": "correct-password"}).status_code
        == 201
    )
    client.post("/auth/logout")

    response = client.post("/auth/login", json={"username": "mira", "password": "wrong-password"})

    assert response.status_code == 401
    assert response.json() == {
        "authenticated": False,
        "error": "invalid_credentials",
        "phase": "auth_login",
        "detail": "Invalid username or password.",
    }
    assert_no_secret_material(response.text, "wrong-password", "correct-password")


def test_registered_user_login_works_when_local_admin_bootstrap_is_disabled(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path, environment="production", enable_local_admin=True)))
    password = "learner-password-1"

    assert client.post("/auth/register", json={"username": "mira", "password": password}).status_code == 201
    client.post("/auth/logout")
    learner_login = client.post("/auth/login", json={"username": "mira", "password": password})
    admin_login = client.post("/auth/login", json={"username": "admin", "password": "admin"})

    assert learner_login.status_code == 200
    assert learner_login.json() == {
        "authenticated": True,
        "user": {"username": "mira", "role": "learner"},
    }
    assert admin_login.status_code == 403
    assert admin_login.json() == {
        "authenticated": False,
        "error": "local_admin_disabled",
        "detail": "Local admin bootstrap is disabled for this environment.",
    }


def test_invalid_credentials_return_structured_error_without_echoing_password(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))

    response = client.post("/auth/login", json={"username": "admin", "password": "wrong"})

    assert response.status_code == 401
    body = response.json()
    assert body == {
        "authenticated": False,
        "error": "invalid_credentials",
        "detail": "Invalid username or password.",
    }
    assert "wrong" not in response.text


def test_current_user_reports_logged_out_without_session(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))

    response = client.get("/auth/current-user")

    assert response.status_code == 401
    assert response.json() == {
        "authenticated": False,
        "user": None,
        "detail": "No active user session.",
    }


def test_local_admin_login_refused_when_development_bootstrap_disabled(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path, environment="production", enable_local_admin=True)))

    response = client.post("/auth/login", json={"username": "admin", "password": "admin"})

    assert response.status_code == 403
    assert response.json() == {
        "authenticated": False,
        "error": "local_admin_disabled",
        "detail": "Local admin bootstrap is disabled for this environment.",
    }
    assert "password" not in response.text


def test_logout_clears_authenticated_session(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))
    assert client.post("/auth/login", json={"username": "admin", "password": "admin"}).status_code == 200

    logout = client.post("/auth/logout")

    assert logout.status_code == 200
    assert logout.json() == {"authenticated": False}
    current_user = client.get("/auth/current-user")
    assert current_user.status_code == 401


def test_logout_clears_access_to_practice_endpoints_for_registered_user(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))
    assert (
        client.post("/auth/register", json={"username": "mira", "password": "learner-password-1"}).status_code
        == 201
    )

    logout = client.post("/auth/logout")
    practice_queue = client.get("/practice/queue")

    assert logout.status_code == 200
    assert practice_queue.status_code == 401
    assert practice_queue.json() == {
        "ok": False,
        "error": "unauthenticated",
        "phase": "practice_queue",
        "detail": "Login is required to request a practice queue.",
    }
