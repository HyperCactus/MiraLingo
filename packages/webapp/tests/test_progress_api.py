from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from mirad_webapp.api import create_app
from mirad_webapp.config import Settings
from mirad_webapp.practice import MAX_EVENTS
from mirad_webapp.practice_engine import build_practice_progress


NOW = datetime(2026, 5, 23, 12, 0, tzinfo=timezone.utc)


def _write_phrase_csv(path: Path) -> Path:
    path.write_text(
        "english,mirad\n"
        "hello world,ha world\n"
        "good morning,gud morgen\n",
        encoding="utf-8",
    )
    return path


def _app_with_cards(monkeypatch, tmp_path: Path):
    phrase_csv = _write_phrase_csv(tmp_path / "phrases.csv")

    def fake_lookup(english_word: str) -> str | None:
        return {"the": "te", "be": "bi"}.get(english_word)

    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", fake_lookup)
    return create_app(Settings(session_secret="test-secret", database_path=tmp_path / "miralingo.sqlite3", phrase_csv_path=phrase_csv))


def _login(client: TestClient) -> None:
    response = client.post("/auth/login", json={"username": "admin", "password": "admin"})
    assert response.status_code == 200


def test_practice_progress_requires_authenticated_session(monkeypatch, tmp_path: Path) -> None:
    app = _app_with_cards(monkeypatch, tmp_path)
    client = TestClient(app)

    response = client.get("/practice/progress")

    assert response.status_code == 401
    assert response.json() == {
        "ok": False,
        "error": "unauthenticated",
        "phase": "practice_progress",
        "detail": "Login is required to request practice progress.",
    }


def test_practice_progress_starts_empty_after_login(monkeypatch, tmp_path: Path) -> None:
    app = _app_with_cards(monkeypatch, tmp_path)
    client = TestClient(app)
    _login(client)

    response = client.get("/practice/progress")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["phase"] == "practice_progress"
    assert payload["card_count"] == 8
    assert payload["base_card_count"] == 4
    assert payload["event_count"] == 0
    assert payload["total"] == 0
    assert payload["correct"] == 0
    assert payload["incorrect"] == 0
    assert payload["accuracy"] is None
    assert payload["per_type"] == {
        "word": {"attempts": 0, "correct": 0, "incorrect": 0, "accuracy": None},
        "phrase": {"attempts": 0, "correct": 0, "incorrect": 0, "accuracy": None},
    }
    assert payload["latest_event"] is None
    assert payload["weak_count"] == 0
    assert payload["mastered_count"] == 0
    assert payload["stale_count"] == 0
    assert payload["new_count"] == 8
    assert set(payload["new_cards"]) == {
        "phrase:hello-world#english-to-mirad",
        "phrase:hello-world#mirad-to-english",
        "phrase:good-morning#english-to-mirad",
        "phrase:good-morning#mirad-to-english",
        "word:the#english-to-mirad",
        "word:the#mirad-to-english",
        "word:be#english-to-mirad",
        "word:be#mirad-to-english",
    }
    assert payload["per_card"][0]["scheduler_reason"] == "new_item"
    assert payload["per_card"][0]["mastery"] == {"attempts": 0, "correct": 0, "incorrect": 0, "accuracy": None}


def test_practice_progress_reflects_correct_and_incorrect_word_and_phrase_answers(monkeypatch, tmp_path: Path) -> None:
    app = _app_with_cards(monkeypatch, tmp_path)
    client = TestClient(app)
    _login(client)

    correct = client.post("/practice/answers", json={"card_id": "phrase:hello-world", "correct": True})
    incorrect = client.post("/practice/answers", json={"card_id": "word:the", "answer": "wrong"})
    response = client.get("/practice/progress")

    assert correct.status_code == 200
    assert incorrect.status_code == 200
    assert response.status_code == 200
    payload = response.json()
    assert payload["event_count"] == 2
    assert payload["total"] == 2
    assert payload["correct"] == 1
    assert payload["incorrect"] == 1
    assert payload["accuracy"] == 0.5
    assert payload["per_type"]["phrase"] == {"attempts": 1, "correct": 1, "incorrect": 0, "accuracy": 1.0}
    assert payload["per_type"]["word"] == {"attempts": 1, "correct": 0, "incorrect": 1, "accuracy": 0.0}
    assert payload["latest_event"]["card_id"] == "word:the#english-to-mirad"
    assert payload["latest_event"]["base_card_id"] == "word:the"
    assert payload["latest_event"]["direction"] == "english_to_mirad"
    assert payload["latest_event"]["card_type"] == "word"
    assert payload["latest_event"]["correct"] is False
    assert payload["weak_count"] == 1
    assert payload["mastered_count"] == 1
    assert payload["new_count"] == 6
    assert payload["weak_cards"] == ["word:the#english-to-mirad"]
    assert payload["mastered_cards"] == ["phrase:hello-world#english-to-mirad"]

    cards = {card["id"]: card for card in payload["per_card"]}
    assert cards["word:the#english-to-mirad"]["scheduler_reason"] == "weak_recent_performance"
    assert cards["word:the#english-to-mirad"]["mastery"] == {"attempts": 1, "correct": 0, "incorrect": 1, "accuracy": 0.0}
    assert cards["word:the#mirad-to-english"]["mastery"]["attempts"] == 0
    assert cards["phrase:hello-world#english-to-mirad"]["scheduler_reason"] == "mastered_recent"
    assert cards["phrase:hello-world#english-to-mirad"]["mastery"] == {"attempts": 1, "correct": 1, "incorrect": 0, "accuracy": 1.0}


def test_practice_progress_missing_content_source_returns_structured_payload(tmp_path: Path) -> None:
    missing_csv = tmp_path / "missing.csv"
    app = create_app(Settings(session_secret="test-secret", database_path=tmp_path / "miralingo.sqlite3", phrase_csv_path=missing_csv))
    client = TestClient(app)
    _login(client)

    response = client.get("/practice/progress")

    assert response.status_code == 404
    payload = response.json()
    assert payload["ok"] is False
    assert payload["error"] == "source_missing"
    assert payload["phase"] == "phrase_import"
    assert payload["source_type"] == "phrase_csv"
    assert payload["source_path"] == str(missing_csv)
    assert payload["practice_phase"] == "practice_progress"


def test_progress_aggregation_ignores_malformed_events_and_bounds_history() -> None:
    cards = [
        {"id": "phrase:hello-world", "type": "phrase", "english": "hello world", "mirad": "ha world"},
        {"id": "word:the", "type": "word", "english": "the", "mirad": "te"},
    ]
    events = [
        {"card_id": "word:the", "correct": True},
        {"card_id": "word:the", "correct": True, "answered_at": "not-a-date"},
    ]
    for index in range(MAX_EVENTS + 5):
        events.append(
            {
                "card_id": "word:the",
                "card_type": "word",
                "submitted_answer": "te",
                "expected_answer": "te",
                "correct": True,
                "answered_at": (NOW + timedelta(seconds=index)).isoformat(),
            }
        )

    payload = build_practice_progress(cards=cards, events=events, now=NOW + timedelta(minutes=10))

    assert payload["event_count"] == MAX_EVENTS
    assert payload["total"] == MAX_EVENTS
    assert payload["correct"] == MAX_EVENTS
    assert payload["incorrect"] == 0
    assert payload["per_type"]["word"] == {"attempts": MAX_EVENTS, "correct": MAX_EVENTS, "incorrect": 0, "accuracy": 1.0}
    assert payload["latest_event"] == {
        "card_id": "word:the#english-to-mirad",
        "base_card_id": "word:the",
        "direction": "english_to_mirad",
        "card_type": "word",
        "correct": True,
        "answered_at": "2026-05-23T12:03:24+00:00",
    }
    assert payload["mastered_cards"] == ["word:the#english-to-mirad"]
    assert set(payload["new_cards"]) == {
        "phrase:hello-world#english-to-mirad",
        "phrase:hello-world#mirad-to-english",
        "word:the#mirad-to-english",
    }
