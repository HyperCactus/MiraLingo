from fastapi.testclient import TestClient
from mirad_translator.api import app
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

    with patch('mirad_translator.api.translator_en_mir') as mock_en_mir:
        mock_en_mir.return_value = mock_prediction
        with patch('mirad_translator.api.translator_mir_en') as mock_mir_en:
            mock_mir_en.return_value = mock_prediction

            response = client.get("/health")
            assert response.status_code == 200
            assert response.json() == {"status": "healthy"}


def test_health_not_ready():
    """Test /health endpoint when translator is not initialized."""
    import mirad_translator.api as api_module
    original_en_mir = api_module.translator_en_mir
    original_mir_en = api_module.translator_mir_en
    try:
        api_module.translator_en_mir = None
        api_module.translator_mir_en = None

        response = client.get("/health")
        assert response.status_code == 503
        assert response.json()["status"] == "unhealthy"
    finally:
        api_module.translator_en_mir = original_en_mir
        api_module.translator_mir_en = original_mir_en


def test_health_check_failed():
    """Test /health endpoint when translator health check fails."""
    with patch('mirad_translator.api.translator_en_mir') as mock_en_mir:
        mock_en_mir.side_effect = Exception("Health check failed")

        response = client.get("/health")
        assert response.status_code == 503
        assert response.json()["status"] == "unhealthy"
        assert "reason" in response.json()


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "directions" in response.json()


def test_translate_success():
    """Test /translate endpoint with successful En→Mir translation."""
    mock_prediction = dspy.Prediction(
        mirad_text="Helo",
        confidence="0.95",
        word_equivalents={"hello": "helo"},
        context=["[grammar] greeting rules"],
    )

    with patch('mirad_translator.api.translator_en_mir') as mock_en_mir:
        mock_en_mir.return_value = mock_prediction

        response = client.post("/translate", json={"text": "Hello"})

        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "Hello"
        assert data["translation"] == "Helo"
        assert data["direction"] == "en_to_mir"
        assert data["confidence"] == "0.95"
        # Without retrieve=True, word_equivalents and context should be null
        assert data.get("word_equivalents") is None
        assert data.get("context") is None


def test_translate_mir_to_en():
    """Test /translate endpoint with Mir→En direction."""
    mock_prediction = dspy.Prediction(
        english_text="I know the answer.",
        word_equivalents={"at": "i", "te": "know"},
        context=["[grammar] verb rules"],
    )

    with patch('mirad_translator.api.translator_mir_en') as mock_mir_en:
        mock_mir_en.return_value = mock_prediction

        response = client.post("/translate", json={"text": "At te ha dud.", "direction": "mir_to_en"})

        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "At te ha dud."
        assert data["translation"] == "I know the answer."
        assert data["direction"] == "mir_to_en"


def test_translate_with_retrieve():
    """Test /translate endpoint with retrieve=True returns word_equivalents and context."""
    mock_prediction = dspy.Prediction(
        mirad_text="At tose oma.",
        confidence="0.90",
        word_equivalents={"i": "at", "cold": "oma"},
        context=["[grammar] verb rules"],
    )

    with patch('mirad_translator.api.translator_en_mir') as mock_en_mir:
        mock_en_mir.return_value = mock_prediction

        response = client.post("/translate", json={"text": "I am cold.", "retrieve": True})

        assert response.status_code == 200
        data = response.json()
        assert data["word_equivalents"] == {"i": "at", "cold": "oma"}
        assert data["context"] == ["[grammar] verb rules"]


def test_translate_no_translator():
    """Test /translate endpoint when translator is not initialized."""
    import mirad_translator.api as api_module
    original_en_mir = api_module.translator_en_mir
    try:
        api_module.translator_en_mir = None

        response = client.post("/translate", json={"text": "Hello"})
        assert response.status_code == 503

    finally:
        api_module.translator_en_mir = original_en_mir


def test_translate_exception():
    """Test /translate endpoint when translation fails."""
    with patch('mirad_translator.api.translator_en_mir') as mock_en_mir:
        mock_en_mir.side_effect = Exception("Translation failed")

        response = client.post("/translate", json={"text": "Hello"})
        assert response.status_code == 500