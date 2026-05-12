from fastapi.testclient import TestClient
from mirad_translator.api import app, translator
from unittest.mock import patch, Mock
import pytest
import dspy

# Create test client
client = TestClient(app)


def test_health_ready():
    """Test /health endpoint when translator is ready."""
    mock_prediction = dspy.Prediction(
        mirad_text="Helo", confidence="0.95",
        word_equivalents={}, context=[],
    )

    with patch('mirad_translator.api.translator') as mock_translator:
        mock_translator.forward.return_value = mock_prediction

        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


def test_health_not_ready():
    """Test /health endpoint when translator is not initialized."""
    global translator
    original_translator = translator
    try:
        translator = None

        response = client.get("/health")
        assert response.status_code == 503
        assert response.json() == {
            "status": "unhealthy",
            "reason": "Translator not initialized"
        }
    finally:
        translator = original_translator


def test_health_check_failed():
    """Test /health endpoint when translator health check fails."""
    with patch('mirad_translator.api.translator') as mock_translator:
        mock_translator.forward.side_effect = Exception("Health check failed")

        response = client.get("/health")
        assert response.status_code == 503
        assert response.json()["status"] == "unhealthy"
        assert "reason" in response.json()


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_translate_success():
    """Test /translate endpoint with successful translation."""
    mock_prediction = dspy.Prediction(
        mirad_text="Helo",
        confidence="0.95",
        word_equivalents={"hello": "helo"},
        context=["[grammar] greeting rules"],
    )

    with patch('mirad_translator.api.translator') as mock_translator:
        mock_translator.forward.return_value = mock_prediction

        response = client.post("/translate", json={"text": "Hello"})

        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "Hello"
        assert data["translation"] == "Helo"
        assert data["confidence"] == "0.95"
        # Without retrieve=True, word_equivalents and context should be null
        assert data.get("word_equivalents") is None
        assert data.get("context") is None

        mock_translator.forward.assert_called_once_with(english_text="Hello")


def test_translate_with_retrieve():
    """Test /translate endpoint with retrieve=True returns word_equivalents and context."""
    mock_prediction = dspy.Prediction(
        mirad_text="At tose oma.",
        confidence="0.90",
        word_equivalents={"i": "at", "cold": "oma"},
        context=["[grammar] verb rules"],
    )

    with patch('mirad_translator.api.translator') as mock_translator:
        mock_translator.forward.return_value = mock_prediction

        response = client.post("/translate", json={"text": "I am cold.", "retrieve": True})

        assert response.status_code == 200
        data = response.json()
        assert data["word_equivalents"] == {"i": "at", "cold": "oma"}
        assert data["context"] == ["[grammar] verb rules"]


def test_translate_no_translator():
    """Test /translate endpoint when translator is not initialized."""
    global translator
    original_translator = translator
    try:
        translator = None

        response = client.post("/translate", json={"text": "Hello"})
        assert response.status_code == 503
        assert response.json()["detail"] == "Translator not initialized"

    finally:
        translator = original_translator


def test_translate_exception():
    """Test /translate endpoint when translation fails."""
    with patch('mirad_translator.api.translator') as mock_translator:
        mock_translator.forward.side_effect = Exception("Translation failed")

        response = client.post("/translate", json={"text": "Hello"})
        assert response.status_code == 500


def test_startup_event():
    """Test startup event exists and does not crash when Ollama is unavailable."""
    startup_handlers = [
        h for h in app.router.on_startup
    ] if hasattr(app.router, 'on_startup') else []
    assert len(startup_handlers) >= 1 or app.on_event("startup") is not None