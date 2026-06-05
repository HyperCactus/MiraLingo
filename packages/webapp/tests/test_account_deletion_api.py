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
        "hello world,ha world\n"
        "the,te\n",
        encoding="utf-8",
    )
    return path


def _settings(tmp_path: Path, database_path: Path | None = None) -> Settings:
    return Settings(
        session_secret="test-secret",
        phrase_csv_path=_write_phrase_csv(tmp_path / "phrases.csv"),
        database_path=database_path or (tmp_path / "miralingo.sqlite3"),
    )


def _register(client: TestClient, username: str, password: str = "learner-password-1") -> None:
    response = client.post("/auth/register", json={"username": username, "password": password})
    assert response.status_code == 201


def _seed_practice_rows(client: TestClient) -> None:
    queue = client.get("/practice/queue?limit=1")
    assert queue.status_code == 200
    card_id = queue.json()["cards"][0]["id"]
    answer = client.post("/practice/answers", json={"card_id": card_id, "answer": "ha world"})
    assert answer.status_code == 200


def test_account_delete_requires_authenticated_session(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))

    response = client.request("DELETE", "/auth/account", json={"email": "mira@legacy.local", "confirmation": "mira@legacy.local DELETE"})

    assert response.status_code == 401
    assert response.json() == {
        "ok": False,
        "error": "unauthenticated",
        "phase": "account_delete",
        "detail": "Login is required to delete the current account.",
    }


def test_account_delete_rejects_wrong_confirmation_and_preserves_session(tmp_path: Path) -> None:
    database_path = tmp_path / "miralingo.sqlite3"
    client = TestClient(create_app(_settings(tmp_path, database_path)))
    _register(client, "mira")

    wrong_phrase = client.request("DELETE", "/auth/account", json={"username": "mira", "confirmation": "KEEP"})
    wrong_username = client.request("DELETE", "/auth/account", json={"email": "sara@legacy.local", "confirmation": "mira@legacy.local DELETE"})
    current_user = client.get("/auth/current-user")

    assert wrong_phrase.status_code == 400
    assert wrong_phrase.json() == {
        "ok": False,
        "error": "invalid_confirmation",
        "phase": "account_delete",
        "detail": "Account deletion requires the current email plus the exact confirmation phrase '<email> DELETE'.",
    }
    assert wrong_username.status_code == 400
    assert wrong_username.json() == {
        "ok": False,
        "error": "invalid_confirmation",
        "phase": "account_delete",
        "detail": "Account deletion requires the current email plus the exact confirmation phrase '<email> DELETE'.",
    }
    assert current_user.status_code == 200
    with sqlite3.connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM users WHERE username = 'mira'").fetchone()[0] == 1


def test_account_delete_rejects_local_admin_and_preserves_bootstrap_login(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))
    login = client.post("/auth/login", json={"username": "admin", "password": "admin"})
    assert login.status_code == 200

    response = client.request("DELETE", "/auth/account", json={"username": "admin", "confirmation": "admin DELETE"})

    assert response.status_code == 403
    assert response.json() == {
        "ok": False,
        "error": "protected_account",
        "phase": "account_delete",
        "detail": "The local admin account cannot be deleted.",
    }
    assert client.get("/auth/current-user").status_code == 200
    client.post("/auth/logout")
    relogin = client.post("/auth/login", json={"username": "admin", "password": "admin"})
    assert relogin.status_code == 200


def test_account_delete_cascades_owned_rows_clears_session_and_keeps_other_learner_rows(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: {"the": "te"}.get(english_word))
    database_path = tmp_path / "miralingo.sqlite3"
    app = create_app(_settings(tmp_path, database_path))
    client = TestClient(app)
    _register(client, "mira")
    client.put("/settings", json={"theme": "dark", "tts_speed": 0.9})
    _seed_practice_rows(client)
    assert client.post("/auth/logout").status_code == 200

    other = TestClient(create_app(_settings(tmp_path, database_path)))
    _register(other, "sara")
    other.put("/settings", json={"theme": "light", "tts_speed": 1.0})
    _seed_practice_rows(other)
    assert other.post("/auth/logout").status_code == 200

    deleting_client = TestClient(create_app(_settings(tmp_path, database_path)))
    login = deleting_client.post("/auth/login", json={"username": "mira", "password": "learner-password-1"})
    assert login.status_code == 200

    response = deleting_client.request(
        "DELETE",
        "/auth/account",
        json={"email": "mira@legacy.local", "confirmation": "mira@legacy.local DELETE"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "ok": True,
        "phase": "account_delete",
        "deleted_email": "mira@legacy.local",
        "authenticated": False,
    }
    current_user = deleting_client.get("/auth/current-user")
    assert current_user.status_code == 401
    failed_login = deleting_client.post(
        "/auth/login", json={"username": "mira", "password": "learner-password-1"}
    )
    assert failed_login.status_code == 401

    with sqlite3.connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM users WHERE username = 'mira'").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM user_settings WHERE username = 'mira'").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM shown_cards WHERE username = 'mira'").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM answer_events WHERE username = 'mira'").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM users WHERE username = 'sara'").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM user_settings WHERE username = 'sara'").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM shown_cards WHERE username = 'sara'").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM answer_events WHERE username = 'sara'").fetchone()[0] == 1


def test_account_delete_storage_failure_returns_phase_specific_json(tmp_path: Path) -> None:
    app = create_app(_settings(tmp_path))
    client = TestClient(app)
    _register(client, "mira")

    def fail_delete(*, user_id: str = None, username: str = None):
        raise StorageError(phase="account_delete", detail="Could not delete account.")

    app.state.storage.delete_user_account = fail_delete
    response = client.request("DELETE", "/auth/account", json={"email": "mira@legacy.local", "confirmation": "mira@legacy.local DELETE"})

    assert response.status_code == 503
    assert response.json() == {
        "ok": False,
        "error": "storage_error",
        "phase": "account_delete",
        "detail": "Could not delete account.",
    }
    assert client.get("/auth/current-user").status_code == 200
