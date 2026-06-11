from pathlib import Path

from fastapi.testclient import TestClient

from mirad_webapp.api import create_app
from mirad_webapp.config import Settings


def assert_no_secret_material(response_text: str, *secrets: str) -> None:
    for secret in secrets:
        assert secret not in response_text
    assert "password_hash" not in response_text
    assert "token_hash" not in response_text


def _settings(tmp_path: Path, **overrides) -> Settings:
    values = {"environment": "development", "enable_local_admin": True, "database_path": tmp_path / "miralingo.sqlite3"}
    values.update(overrides)
    return Settings(**values)


def assert_safe_user(user: dict, *, email: str, role: str = "user", name: str | None = None) -> None:
    assert user["id"]
    assert user["email"] == email
    assert user["role"] == role
    assert user["name"] == name
    assert "password_hash" not in user
    assert "google_sub" not in user


def test_local_admin_can_login_in_development(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))

    response = client.post("/auth/login", json={"email": "admin@local.miralingo", "password": "admin"})

    assert response.status_code == 200
    assert_safe_user(response.json()["user"], email="admin@local.miralingo", role="admin", name="Local Admin")
    assert "miralingo_session" in client.cookies

    current_user = client.get("/auth/current-user")
    assert current_user.status_code == 200
    assert current_user.json()["authenticated"] is True
    assert_safe_user(current_user.json()["user"], email="admin@local.miralingo", role="admin", name="Local Admin")


def test_register_logs_in_learner_then_logout_and_login_restore_session(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))
    password = "learner-password-1"

    registration = client.post("/auth/register", json={"email": " Mira@Example.COM ", "password": password, "name": "Mira"})

    assert registration.status_code == 201
    assert_safe_user(registration.json()["user"], email="mira@example.com", name="Mira")
    assert_no_secret_material(registration.text, password)

    current_user = client.get("/auth/current-user")
    assert current_user.status_code == 200
    assert_safe_user(current_user.json()["user"], email="mira@example.com", name="Mira")

    logout = client.post("/auth/logout")
    assert logout.status_code == 200
    assert logout.json() == {"authenticated": False}
    assert client.get("/auth/current-user").status_code == 401

    login = client.post("/auth/login", json={"email": "MIRA@example.com", "password": password})
    assert login.status_code == 200
    assert_safe_user(login.json()["user"], email="mira@example.com", name="Mira")
    assert_no_secret_material(login.text, password)


def test_session_cookie_is_opaque_and_server_side(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))
    response = client.post("/auth/register", json={"email": "mira@example.com", "password": "learner-password-1"})

    cookie = client.cookies.get("miralingo_session")
    assert response.status_code == 201
    assert cookie
    assert "mira@example.com" not in cookie
    assert "user" not in cookie.lower()

    import sqlite3

    with sqlite3.connect(tmp_path / "miralingo.sqlite3") as connection:
        rows = connection.execute("SELECT token_hash FROM auth_sessions").fetchall()
    assert len(rows) == 1
    assert rows[0][0] != cookie


def test_registration_validation_errors_do_not_create_sessions_or_accounts(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))

    missing_password = client.post("/auth/register", json={"email": "mira@example.com"})
    assert missing_password.status_code == 422
    assert client.get("/auth/current-user").status_code == 401

    invalid_email = client.post("/auth/register", json={"email": "not-an-email", "password": "valid-pass"})
    assert invalid_email.status_code == 400
    assert invalid_email.json() == {
        "authenticated": False,
        "error": "invalid_email",
        "phase": "auth_register",
        "detail": "A valid email address is required.",
    }

    short_password = client.post("/auth/register", json={"email": "mira@example.com", "password": "short"})
    assert short_password.status_code == 400
    assert short_password.json()["error"] == "invalid_password"
    assert_no_secret_material(short_password.text, "short")

    failed_login = client.post("/auth/login", json={"email": "mira@example.com", "password": "valid-pass"})
    assert failed_login.status_code == 401
    assert failed_login.json()["detail"] == "Invalid email or password."


def test_duplicate_registration_is_rejected_without_replacing_password(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))
    original_password = "original-password"
    duplicate_password = "duplicate-password"
    assert client.post("/auth/register", json={"email": "mira@example.com", "password": original_password}).status_code == 201
    client.post("/auth/logout")

    duplicate = client.post("/auth/register", json={"email": "MIRA@example.com", "password": duplicate_password})

    assert duplicate.status_code == 409
    assert duplicate.json()["error"] == "email_unavailable"
    assert_no_secret_material(duplicate.text, duplicate_password)

    replaced_login = client.post("/auth/login", json={"email": "mira@example.com", "password": duplicate_password})
    assert replaced_login.status_code == 401
    original_login = client.post("/auth/login", json={"email": "mira@example.com", "password": original_password})
    assert original_login.status_code == 200


def test_wrong_registered_user_password_returns_structured_error_without_secret_echo(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))
    assert client.post("/auth/register", json={"email": "mira@example.com", "password": "correct-password"}).status_code == 201
    client.post("/auth/logout")

    response = client.post("/auth/login", json={"email": "mira@example.com", "password": "wrong-password"})

    assert response.status_code == 401
    assert response.json()["error"] == "invalid_credentials"
    assert response.json()["detail"] == "Invalid email or password."
    assert_no_secret_material(response.text, "wrong-password", "correct-password")


def test_registered_user_login_works_when_local_admin_bootstrap_is_disabled(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path, environment="production", enable_local_admin=True)))
    password = "learner-password-1"

    assert client.post("/auth/register", json={"email": "mira@example.com", "password": password}).status_code == 201
    client.post("/auth/logout")
    learner_login = client.post("/auth/login", json={"email": "mira@example.com", "password": password})
    admin_login = client.post("/auth/login", json={"email": "admin@local.miralingo", "password": "admin"})

    assert learner_login.status_code == 200
    assert_safe_user(learner_login.json()["user"], email="mira@example.com")
    assert admin_login.status_code == 403
    assert admin_login.json()["error"] == "local_admin_disabled"


def test_current_user_reports_logged_out_without_session(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))

    response = client.get("/auth/current-user")

    assert response.status_code == 401
    assert response.json() == {
        "authenticated": False,
        "user": None,
        "detail": "No active user session.",
    }


def test_logout_clears_authenticated_session(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))
    assert client.post("/auth/login", json={"email": "admin@local.miralingo", "password": "admin"}).status_code == 200

    logout = client.post("/auth/logout")

    assert logout.status_code == 200
    assert logout.json() == {"authenticated": False}
    current_user = client.get("/auth/current-user")
    assert current_user.status_code == 401


def test_logout_clears_access_to_practice_endpoints_for_registered_user(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))
    assert client.post("/auth/register", json={"email": "mira@example.com", "password": "learner-password-1"}).status_code == 201

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


def test_password_forgot_does_not_reveal_email_existence(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))
    existing = client.post("/auth/password/forgot", json={"email": "mira@example.com"})
    missing = client.post("/auth/password/forgot", json={"email": "missing@example.com"})
    assert existing.status_code == 202
    assert missing.status_code == 202
    assert existing.json()["detail"] == missing.json()["detail"]


def test_password_forgot_sends_reset_email_for_existing_account_without_public_status(monkeypatch, tmp_path: Path) -> None:
    sent: list[dict[str, str]] = []

    def fake_send_password_reset_email(*, settings, to_email: str, reset_url: str):
        sent.append({"to_email": to_email, "reset_url": reset_url, "provider": str(settings.email_provider)})
        from mirad_webapp.email_delivery import EmailDeliveryResult

        return EmailDeliveryResult(ok=True, provider="resend")

    monkeypatch.setattr("mirad_webapp.api.send_password_reset_email", fake_send_password_reset_email)
    client = TestClient(
        create_app(
            _settings(
                tmp_path,
                app_url="https://yourapp.com",
                email_provider="resend",
                email_from="Your App <noreply@yourdomain.com>",
                resend_api_key="re_test_secret",
            )
        )
    )
    assert client.post("/auth/register", json={"email": "mira@example.com", "password": "learner-password-1"}).status_code == 201

    response = client.post("/auth/password/forgot", json={"email": "MIRA@example.com"})

    assert response.status_code == 202
    assert response.json() == {"ok": True, "phase": "password_forgot", "detail": "If an account exists, reset instructions have been sent."}
    assert sent[0]["to_email"] == "mira@example.com"
    assert sent[0]["provider"] == "resend"
    assert sent[0]["reset_url"].startswith("https://yourapp.com/?reset_token=")
    assert "reset_token" not in response.text
    assert "re_test_secret" not in response.text


def test_password_forgot_skips_provider_for_missing_account(monkeypatch, tmp_path: Path) -> None:
    def fail_if_called(**_kwargs):
        raise AssertionError("email provider should not be called for missing account")

    monkeypatch.setattr("mirad_webapp.api.send_password_reset_email", fail_if_called)
    app = create_app(_settings(tmp_path, email_provider="resend", email_from="Your App <noreply@yourdomain.com>", resend_api_key="re_test_secret"))
    client = TestClient(app)

    response = client.post("/auth/password/forgot", json={"email": "missing@example.com"})

    assert response.status_code == 202
    assert response.json()["detail"] == "If an account exists, reset instructions have been sent."
    assert app.state.last_password_reset_email.ok is False
    assert app.state.last_password_reset_email.provider == "resend"
    assert app.state.last_password_reset_email.skipped is True
    assert app.state.last_password_reset_email.reason == "no_resettable_account"
    assert "missing@example.com" not in response.text


def test_password_forgot_records_sanitized_provider_failure(monkeypatch, tmp_path: Path) -> None:
    from mirad_webapp.email_delivery import EmailDeliveryError

    def fail_send(**_kwargs):
        raise EmailDeliveryError(provider="resend", reason="resend_http_401")

    monkeypatch.setattr("mirad_webapp.api.send_password_reset_email", fail_send)
    app = create_app(_settings(tmp_path, email_provider="resend", email_from="Your App <noreply@yourdomain.com>", resend_api_key="re_test_secret"))
    client = TestClient(app)
    assert client.post("/auth/register", json={"email": "mira@example.com", "password": "learner-password-1"}).status_code == 201

    response = client.post("/auth/password/forgot", json={"email": "mira@example.com"})

    assert response.status_code == 202
    assert response.json()["detail"] == "If an account exists, reset instructions have been sent."
    assert app.state.last_password_reset_email.ok is False
    assert app.state.last_password_reset_email.provider == "resend"
    assert app.state.last_password_reset_email.reason == "resend_http_401"
    assert "re_test_secret" not in response.text


def test_google_login_reports_structured_unconfigured_error(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))
    response = client.get("/auth/google/login")
    assert response.status_code == 503
    assert response.json()["error"] == "google_oauth_unconfigured"
