from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from mirad_webapp.api import create_app
from mirad_webapp.config import Settings


NOW = datetime(2026, 5, 24, 12, 0, tzinfo=timezone.utc)


def _write_phrase_csv(path: Path) -> Path:
    path.write_text(
        "english,mirad\n"
        "hello world,ha world\n"
        "good morning,gud morgen\n",
        encoding="utf-8",
    )
    return path


def _app(tmp_path: Path):
    settings = Settings(
        session_secret="test-secret",
        database_path=tmp_path / "miralingo.sqlite3",
        phrase_csv_path=_write_phrase_csv(tmp_path / "phrases.csv"),
    )
    return create_app(settings)


def _login(client: TestClient) -> None:
    response = client.post("/auth/login", json={"username": "admin", "password": "admin"})
    assert response.status_code == 200


def _answer(client: TestClient, *, card_id: str, answer: str) -> dict:
    response = client.post("/practice/answers", json={"card_id": card_id, "answer": answer})
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["phase"] == "practice_answer"
    return payload


def test_m008_integrated_authenticated_learner_flow_persists_sessions_and_analytics(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "mirad_webapp.card_content._default_lexicon_lookup",
        lambda english_word: {"the": "te", "be": "bi"}.get(english_word),
    )

    app = _app(tmp_path)
    client = TestClient(app)

    _login(client)

    sparse_before = client.get("/practice/analytics")
    assert sparse_before.status_code == 200
    sparse_payload = sparse_before.json()
    assert sparse_payload["sparse_history"]["is_sparse"] is True
    assert sparse_payload["sparse_history"]["reason"] == "new_learner"

    first_session = client.post("/practice/sessions/start")
    assert first_session.status_code == 200
    first_session_id = first_session.json()["active_session"]["session_id"]

    for _ in range(2):
        answer_payload = _answer(
            client,
            card_id="phrase:hello-world#english-to-mirad",
            answer="ha world",
        )
        assert answer_payload["base_card_id"] == "phrase:hello-world"
        assert answer_payload["direction"] == "english_to_mirad"

    miss = _answer(
        client,
        card_id="phrase:hello-world#mirad-to-english",
        answer="wrong answer",
    )
    assert miss["correct"] is False

    end_first = client.post("/practice/sessions/end")
    assert end_first.status_code == 200
    assert end_first.json()["ended_session"]["session_id"] == first_session_id

    second_session = client.post("/practice/sessions/start")
    assert second_session.status_code == 200
    second_session_id = second_session.json()["active_session"]["session_id"]
    assert second_session_id != first_session_id

    for _ in range(2):
        _answer(
            client,
            card_id="phrase:hello-world#english-to-mirad",
            answer="ha world",
        )

    queue = client.get("/practice/queue?limit=6&mode=mixed")
    assert queue.status_code == 200
    queue_payload = queue.json()
    assert queue_payload["ok"] is True
    assert queue_payload["phase"] == "practice_queue"
    assert isinstance(queue_payload["cards"], list)
    assert queue_payload["cards"]
    diagnostics = queue_payload["diagnostics"]
    assert set(diagnostics.keys()) >= {
        "requested_active_revision_ratio",
        "actual_active_revision_ratio",
        "requested_word_phrase_mix",
        "actual_word_phrase_mix",
        "repeat_gap",
        "repeat_gap_satisfied",
        "repeat_gap_relaxed",
        "fallback_reasons",
    }
    assert "small_pool" in diagnostics["fallback_reasons"]

    progress = client.get("/practice/progress")
    assert progress.status_code == 200
    progress_payload = progress.json()
    assert progress_payload["ok"] is True
    assert progress_payload["phase"] == "practice_progress"
    assert progress_payload["event_count"] >= 5
    assert "latest_event" in progress_payload
    assert "per_type" in progress_payload
    assert "per_direction" in progress_payload

    analytics = client.get("/practice/analytics?window_days=30&include_cards=true")
    assert analytics.status_code == 200
    payload = analytics.json()
    assert payload["ok"] is True
    assert payload["phase"] == "practice_analytics"
    assert payload["event_count"] >= 5
    assert payload["session_count"] >= 2
    assert payload["lifecycle_count"] >= 1
    assert payload["sparse_history"]["is_sparse"] is False
    assert payload["direction_breakdown"]["english_to_mirad"]["attempts"] >= 4
    assert payload["direction_breakdown"]["mirad_to_english"]["attempts"] >= 1
    assert payload["lifecycle"]["revision"] >= 1
    assert payload["lifecycle"]["active"] >= 0

    promoted = app.state.storage.get_practice_lifecycle(
        username="admin",
        base_card_id="phrase:hello-world",
        direction="english_to_mirad",
    )
    assert promoted["lifecycle"] == "revision"
    assert promoted["correct_streak"] >= 4
    assert promoted["session_streak"] >= 2

    sparse_direction = payload["direction_breakdown"]["mirad_to_english"]
    assert sparse_direction["attempts"] < payload["direction_breakdown"]["english_to_mirad"]["attempts"]

    assert all("submitted_answer" not in str(card) for card in payload.get("per_card", []))
    assert "traceback" not in str(payload).lower()

    queue_card = queue_payload["cards"][0]
    assert queue_card["audio_card_id"] == queue_card["base_card_id"]

    with app.state.storage._connect("practice_analytics") as connection:
        started_rows = connection.execute(
            "SELECT COUNT(*) FROM practice_sessions WHERE username = ? AND started_at IS NOT NULL",
            ("admin",),
        ).fetchone()[0]
        ended_rows = connection.execute(
            "SELECT COUNT(*) FROM practice_sessions WHERE username = ? AND ended_at IS NOT NULL",
            ("admin",),
        ).fetchone()[0]
    assert started_rows >= 2
    assert ended_rows >= 1
