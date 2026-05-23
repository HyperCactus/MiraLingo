from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from mirad_webapp.api import create_app
from mirad_webapp.config import Settings
from mirad_webapp.content_cli import main as content_cli_main


def _write_phrase_csv(path: Path) -> Path:
    path.write_text(
        "english,mirad\n"
        "hello world,ha world\n"
        "single,sol\n"
        "known word,kon wurd\n",
        encoding="utf-8",
    )
    return path


def test_content_import_preview_returns_structured_counts(monkeypatch, tmp_path: Path) -> None:
    phrase_csv = _write_phrase_csv(tmp_path / "phrases.csv")

    def fake_lookup(english_word: str) -> str | None:
        return {"the": "te", "be": "bi"}.get(english_word)

    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", fake_lookup)
    app = create_app(Settings(session_secret="test-secret", phrase_csv_path=phrase_csv))
    client = TestClient(app)

    response = client.get("/content/import/preview?word_limit=3")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["mutating"] is False
    assert payload["auth_required"] is False
    assert payload["source"] == "configured"
    assert payload["counts"]["phrase"]["imported"] == 2
    assert payload["counts"]["phrase"]["skipped"]["one_word_english"] == 1
    assert payload["counts"]["word"]["imported"] == 2
    assert payload["counts"]["word"]["missed"]["lexicon_miss"] == 1
    assert payload["sources"]["phrase_csv"] == str(phrase_csv)


def test_content_import_preview_rejects_path_tampering_and_invalid_limit(tmp_path: Path) -> None:
    phrase_csv = _write_phrase_csv(tmp_path / "phrases.csv")
    app = create_app(Settings(session_secret="test-secret", phrase_csv_path=phrase_csv))
    client = TestClient(app)

    invalid_source = client.get("/content/import/preview?source=../../secret.csv")
    invalid_limit = client.get("/content/import/preview?word_limit=5001")

    assert invalid_source.status_code == 422
    assert invalid_limit.status_code == 422


def test_content_import_preview_missing_source_returns_structured_error(tmp_path: Path) -> None:
    missing_csv = tmp_path / "missing.csv"
    app = create_app(Settings(session_secret="test-secret", phrase_csv_path=missing_csv))
    client = TestClient(app)

    response = client.get("/content/import/preview")

    assert response.status_code == 404
    payload = response.json()
    assert payload["ok"] is False
    assert payload["error"] == "source_missing"
    assert payload["phase"] == "phrase_import"
    assert payload["source_type"] == "phrase_csv"
    assert payload["source_path"] == str(missing_csv)


def test_content_cli_prints_deterministic_counts(monkeypatch, capsys, tmp_path: Path) -> None:
    phrase_csv = _write_phrase_csv(tmp_path / "phrases.csv")

    def fake_lookup(english_word: str) -> str | None:
        return {"the": "te"}.get(english_word)

    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", fake_lookup)

    exit_code = content_cli_main(["--phrase-csv", str(phrase_csv), "--word-limit", "2"])

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert "cards" not in output
    assert output["ok"] is True
    assert output["mutating"] is False
    assert output["counts"]["phrase"]["imported"] == 2
    assert output["counts"]["phrase"]["skipped"]["one_word_english"] == 1
    assert output["counts"]["word"]["imported"] == 1
    assert output["counts"]["word"]["missed"]["lexicon_miss"] == 1


def test_content_cli_missing_csv_exits_nonzero_with_structured_diagnostic(capsys, tmp_path: Path) -> None:
    missing_csv = tmp_path / "missing.csv"

    exit_code = content_cli_main(["--phrase-csv", str(missing_csv)])

    assert exit_code == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    payload = json.loads(captured.err)
    assert payload["ok"] is False
    assert payload["error"] == "source_missing"
    assert payload["phase"] == "phrase_import"
    assert payload["source_path"] == str(missing_csv)


def test_content_cli_invalid_limit_exits_with_argument_diagnostic(capsys, tmp_path: Path) -> None:
    phrase_csv = _write_phrase_csv(tmp_path / "phrases.csv")

    exit_code = content_cli_main(["--phrase-csv", str(phrase_csv), "--word-limit", "5001"])

    assert exit_code == 2
    payload = json.loads(capsys.readouterr().err)
    assert payload["ok"] is False
    assert payload["error"] == "invalid_word_limit"
    assert payload["phase"] == "argument_validation"
