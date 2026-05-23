from __future__ import annotations

import sys
import types
from pathlib import Path

from fastapi.testclient import TestClient

from mirad_webapp.api import create_app
from mirad_webapp.config import Settings


def _write_phrase_csv(path: Path) -> Path:
    path.write_text(
        "english,mirad\n"
        "hello world,ha mirad\n"
        "good morning,gud morgen\n",
        encoding="utf-8",
    )
    return path


def _login(client: TestClient) -> None:
    response = client.post("/auth/login", json={"username": "admin", "password": "admin"})
    assert response.status_code == 200


def _app(tmp_path: Path) -> FastAPIApp:
    return create_app(Settings(session_secret="test-secret", phrase_csv_path=_write_phrase_csv(tmp_path / "phrases.csv")))


FastAPIApp = object


def _install_fake_mbrola(monkeypatch, behavior: str = "success") -> None:
    module = types.ModuleType("mirad_tts.mbrola_backend")

    class MbrolaError(ValueError):
        pass

    class MbrolaNotFoundError(RuntimeError):
        pass

    class MbrolaVoiceNotFoundError(RuntimeError):
        pass

    class MbrolaSynthesisError(RuntimeError):
        pass

    def synthesize_to_wav(text: str, output_path: str | Path) -> Path:
        output = Path(output_path)
        if behavior == "success":
            assert text == "ha mirad"
            output.write_bytes(b"RIFF\x24\x00\x00\x00WAVEfmt ")
            return output
        if behavior == "missing_binary":
            raise MbrolaNotFoundError("mbrola binary not found on PATH")
        if behavior == "missing_voice":
            raise MbrolaVoiceNotFoundError("MBROLA de6 voice database not found")
        if behavior == "synthesis_failure":
            raise MbrolaSynthesisError("MBROLA synthesis failed with exit code 1")
        raise AssertionError(f"unknown fake behavior: {behavior}")

    module.MbrolaError = MbrolaError
    module.MbrolaNotFoundError = MbrolaNotFoundError
    module.MbrolaVoiceNotFoundError = MbrolaVoiceNotFoundError
    module.MbrolaSynthesisError = MbrolaSynthesisError
    module.synthesize_to_wav = synthesize_to_wav
    monkeypatch.setitem(sys.modules, "mirad_tts.mbrola_backend", module)


def test_authenticated_audio_success_returns_wav_with_no_store(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: None)
    _install_fake_mbrola(monkeypatch)
    client = TestClient(_app(tmp_path))
    _login(client)

    response = client.get("/practice/audio/phrase:hello-world")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("audio/wav")
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-miralingo-audio-phase"] == "audio_synthesis"
    assert response.headers["x-miralingo-audio-backend"] == "mbrola"
    assert response.headers["x-miralingo-card-id"] == "phrase:hello-world"
    assert response.content.startswith(b"RIFF")


def test_audio_requires_authenticated_session(tmp_path: Path) -> None:
    client = TestClient(_app(tmp_path))

    response = client.get("/practice/audio/phrase:hello-world")

    assert response.status_code == 401
    assert response.json() == {
        "ok": False,
        "error": "unauthenticated",
        "phase": "audio_synthesis",
        "backend": "mbrola",
        "card_id": "phrase:hello-world",
        "detail": "Login is required to request practice audio.",
    }


def test_audio_unknown_card_returns_structured_404_without_synthesis(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: None)
    _install_fake_mbrola(monkeypatch)
    client = TestClient(_app(tmp_path))
    _login(client)

    response = client.get("/practice/audio/word:missing")

    assert response.status_code == 404
    assert response.json() == {
        "ok": False,
        "error": "unknown_card",
        "phase": "audio_synthesis",
        "backend": "mbrola",
        "card_id": "word:missing",
        "detail": "Practice card was not found in the configured content source.",
    }


def test_audio_missing_content_source_propagates_import_diagnostic(tmp_path: Path) -> None:
    missing_csv = tmp_path / "missing.csv"
    app = create_app(Settings(session_secret="test-secret", phrase_csv_path=missing_csv))
    client = TestClient(app)
    _login(client)

    response = client.get("/practice/audio/phrase:hello-world")

    assert response.status_code == 404
    payload = response.json()
    assert payload["ok"] is False
    assert payload["error"] == "source_missing"
    assert payload["phase"] == "audio_synthesis"
    assert payload["backend"] == "mbrola"
    assert payload["card_id"] == "phrase:hello-world"
    assert payload["source_type"] == "phrase_csv"
    assert payload["source_path"] == str(missing_csv)


def test_audio_import_missing_returns_backend_unavailable(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: None)
    monkeypatch.setitem(sys.modules, "mirad_tts.mbrola_backend", None)
    client = TestClient(_app(tmp_path))
    _login(client)

    response = client.get("/practice/audio/phrase:hello-world")

    assert response.status_code == 503
    payload = response.json()
    assert payload["ok"] is False
    assert payload["error"] == "audio_backend_unavailable"
    assert payload["phase"] == "audio_synthesis"
    assert payload["backend"] == "mbrola"
    assert payload["card_id"] == "phrase:hello-world"
    assert "Traceback" not in payload["detail"]


def test_audio_missing_mbrola_binary_returns_unavailable(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: None)
    _install_fake_mbrola(monkeypatch, "missing_binary")
    client = TestClient(_app(tmp_path))
    _login(client)

    response = client.get("/practice/audio/phrase:hello-world")

    assert response.status_code == 503
    payload = response.json()
    assert payload["error"] == "mbrola_unavailable"
    assert payload["phase"] == "audio_synthesis"
    assert payload["backend"] == "mbrola"
    assert "Traceback" not in payload["detail"]


def test_audio_missing_de6_voice_returns_voice_unavailable(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: None)
    _install_fake_mbrola(monkeypatch, "missing_voice")
    client = TestClient(_app(tmp_path))
    _login(client)

    response = client.get("/practice/audio/phrase:hello-world")

    assert response.status_code == 503
    payload = response.json()
    assert payload["error"] == "mbrola_voice_unavailable"
    assert payload["phase"] == "audio_synthesis"
    assert payload["backend"] == "mbrola"
    assert "Traceback" not in payload["detail"]


def test_audio_synthesis_failure_returns_structured_error(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: None)
    _install_fake_mbrola(monkeypatch, "synthesis_failure")
    client = TestClient(_app(tmp_path))
    _login(client)

    response = client.get("/practice/audio/phrase:hello-world")

    assert response.status_code == 502
    payload = response.json()
    assert payload["ok"] is False
    assert payload["error"] == "audio_synthesis_failed"
    assert payload["phase"] == "audio_synthesis"
    assert payload["backend"] == "mbrola"
    assert payload["card_id"] == "phrase:hello-world"
    assert "Traceback" not in payload["detail"]


def test_audio_rejects_blank_and_path_like_card_ids(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("mirad_webapp.card_content._default_lexicon_lookup", lambda english_word: None)
    _install_fake_mbrola(monkeypatch)
    client = TestClient(_app(tmp_path))
    _login(client)

    blank = client.get("/practice/audio/%20")
    path_like = client.get("/practice/audio/phrase:..secret")

    assert blank.status_code == 422
    assert blank.json()["error"] == "invalid_card_id"
    assert path_like.status_code in {404, 422}
    if path_like.headers.get("content-type", "").startswith("application/json"):
        assert path_like.json().get("error") in {"invalid_card_id", "unknown_card"}
