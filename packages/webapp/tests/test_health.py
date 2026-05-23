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
    assert "Welcome to MiraLingo" in app_source.read_text(encoding="utf-8")
