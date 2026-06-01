from __future__ import annotations

import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from mirad_webapp.api import create_app
from mirad_webapp.config import Settings
from mirad_webapp.storage import StorageError


def _write_phrase_csv(path: Path) -> Path:
    path.write_text(
        "english,mirad\n"
        "hello world,ha world\n",
        encoding="utf-8",
    )
    return path


def _settings(tmp_path: Path, database_path: Path | None = None) -> Settings:
    return Settings(
        session_secret="test-secret",
        phrase_csv_path=_write_phrase_csv(tmp_path / "phrases.csv"),
        database_path=database_path or (tmp_path / "miralingo.sqlite3"),
    )


def _register(client: TestClient, username: str = "mira", password: str = "learner-password-1") -> None:
    response = client.post("/auth/register", json={"username": username, "password": password})
    assert response.status_code == 201


def test_settings_requires_authenticated_session(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))

    get_response = client.get("/settings")
    put_response = client.put("/settings", json={"theme": "dark", "tts_speed": 0.8, "tts_autoplay": False, "sfx_enabled": True})

    assert get_response.status_code == 401
    assert get_response.json() == {
        "ok": False,
        "error": "unauthenticated",
        "phase": "settings_get",
        "detail": "Login is required to view settings.",
    }
    assert put_response.status_code == 401
    assert put_response.json() == {
        "ok": False,
        "error": "unauthenticated",
        "phase": "settings_update",
        "detail": "Login is required to update settings.",
    }


def test_settings_get_returns_defaults_and_single_voice_metadata(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))
    _register(client)

    response = client.get("/settings")

    assert response.status_code == 200
    assert response.json() == {
        "ok": True,
        "phase": "settings_get",
        "settings": {
            "theme": "system",
            "tts_speed": 0.8,
            "tts_autoplay": True,
            "sfx_enabled": True,
            "voice": {
                "id": "de6",
                "label": "Mirad de6",
                "provider": "mbrola",
                "mutable": False,
            },
        },
    }


def test_settings_update_persists_across_app_recreation_and_is_per_user(tmp_path: Path) -> None:
    database_path = tmp_path / "miralingo.sqlite3"
    first = TestClient(create_app(_settings(tmp_path, database_path)))
    _register(first, username="mira")

    update = first.put("/settings", json={"theme": "dark", "tts_speed": 1.1, "tts_autoplay": False, "sfx_enabled": False})
    assert update.status_code == 200
    assert update.json()["settings"]["theme"] == "dark"
    assert update.json()["settings"]["tts_speed"] == 1.1
    assert update.json()["settings"]["tts_autoplay"] is False
    assert update.json()["settings"]["sfx_enabled"] is False
    assert first.post("/auth/logout").status_code == 200

    second = TestClient(create_app(_settings(tmp_path, database_path)))
    _register(second, username="sara")
    sara_defaults = second.get("/settings")
    assert sara_defaults.status_code == 200
    assert sara_defaults.json()["settings"]["theme"] == "system"
    assert sara_defaults.json()["settings"]["tts_speed"] == 0.8
    assert sara_defaults.json()["settings"]["tts_autoplay"] is True
    assert sara_defaults.json()["settings"]["sfx_enabled"] is True
    assert second.post("/auth/logout").status_code == 200

    recreated = TestClient(create_app(_settings(tmp_path, database_path)))
    login = recreated.post("/auth/login", json={"username": "mira", "password": "learner-password-1"})
    assert login.status_code == 200

    fetched = recreated.get("/settings")

    assert fetched.status_code == 200
    assert fetched.json()["settings"] == {
        "theme": "dark",
        "tts_speed": 1.1,
        "tts_autoplay": False,
        "sfx_enabled": False,
        "voice": {
            "id": "de6",
            "label": "Mirad de6",
            "provider": "mbrola",
            "mutable": False,
        },
    }
    with sqlite3.connect(database_path) as connection:
        rows = connection.execute(
            "SELECT username, theme, tts_speed, tts_autoplay, sfx_enabled, voice_id FROM user_settings ORDER BY username"
        ).fetchall()
    assert rows == [
        ("mira", "dark", 1.1, 0, 0, "de6"),
        ("sara", "system", 0.8, 1, 1, "de6"),
    ]


def test_settings_update_rejects_invalid_theme_and_speed_without_mutating_storage(tmp_path: Path) -> None:
    database_path = tmp_path / "miralingo.sqlite3"
    client = TestClient(create_app(_settings(tmp_path, database_path)))
    _register(client)

    bad_theme = client.put("/settings", json={"theme": "neon", "tts_speed": 0.8, "tts_autoplay": True, "sfx_enabled": True})
    bad_speed = client.put("/settings", json={"theme": "light", "tts_speed": 0, "tts_autoplay": True, "sfx_enabled": True})
    bad_type = client.put("/settings", json={"theme": "light", "tts_speed": "fast", "tts_autoplay": True, "sfx_enabled": True})
    fetched = client.get("/settings")

    assert bad_theme.status_code == 422
    assert bad_speed.status_code == 422
    assert bad_type.status_code == 422
    assert fetched.status_code == 200
    assert fetched.json()["settings"]["theme"] == "system"
    assert fetched.json()["settings"]["tts_speed"] == 0.8
    assert fetched.json()["settings"]["tts_autoplay"] is True
    assert fetched.json()["settings"]["sfx_enabled"] is True
    with sqlite3.connect(database_path) as connection:
        rows = connection.execute("SELECT username, theme, tts_speed, tts_autoplay, sfx_enabled FROM user_settings").fetchall()
    assert rows == [("mira", "system", 0.8, 1, 1)]


def test_settings_storage_failures_return_phase_specific_json(tmp_path: Path) -> None:
    app = create_app(_settings(tmp_path))
    client = TestClient(app)
    _register(client)

    def fail_get(*, username: str):
        raise StorageError(phase="settings_get", detail="Could not read settings.")

    def fail_put(*, username: str, theme: str, tts_speed: float, tts_autoplay: bool, sfx_enabled: bool):
        raise StorageError(phase="settings_update", detail="Could not update settings.")

    app.state.storage.get_user_settings = fail_get
    get_response = client.get("/settings")
    assert get_response.status_code == 503
    assert get_response.json() == {
        "ok": False,
        "error": "storage_error",
        "phase": "settings_get",
        "detail": "Could not read settings.",
    }

    app.state.storage.get_user_settings = lambda *, username: None
    app.state.storage.upsert_user_settings = fail_put
    put_response = client.put("/settings", json={"theme": "light", "tts_speed": 0.9, "tts_autoplay": False, "sfx_enabled": True})
    assert put_response.status_code == 503
    assert put_response.json() == {
        "ok": False,
        "error": "storage_error",
        "phase": "settings_update",
        "detail": "Could not update settings.",
    }
