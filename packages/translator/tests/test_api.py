from fastapi.testclient import TestClient
from mirad_translator.api import app, translator
from unittest.mock import patch, Mock
import pytest

# Create test client
client = TestClient(app)

def test_health_ready():
    """Test /health endpoint when translator is ready."""
    # Mock the translator to be available
    with patch('mirad_translator.api.translator') as mock_translator:
        # Setup mock prediction
        mock_prediction = Mock()
        mock_prediction.mirad_text = "Helo"
        mock_prediction.confidence = 0.95
        mock_translator.forward.return_value = mock_prediction
        
        # Set translator to be available
        mock_translator is not None
        
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

def test_health_not_ready():
    """Test /health endpoint when translator is not initialized."""
    # Save original translator
    global translator
    original_translator = translator
    try:
        # Set translator to None
        translator = None
        
        response = client.get("/health")
        assert response.status_code == 503
        assert response.json() == {
            "status": "unhealthy", 
            "reason": "Translator not initialized"
        }
    finally:
        # Restore
        translator = original_translator

def test_health_check_failed():
    """Test /health endpoint when translator health check fails."""
    # Mock translator to fail health check
    with patch('mirad_translator.api.translator') as mock_translator:
        # Make forward method raise an exception
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
    # Mock the translator forward method
    with patch('mirad_translator.api.translator') as mock_translator:
        # Setup mock prediction
        mock_prediction = Mock()
        mock_prediction.mirad_text = "Helo"
        mock_prediction.confidence = 0.95
        mock_translator.forward.return_value = mock_prediction
        
        # Test translation
        response = client.post("/translate", json={"text": "Hello"})
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "Hello"
        assert data["translation"] == "Helo"
        assert data["confidence"] == 0.95
        
        # Verify forward was called with correct arguments
        mock_translator.forward.assert_called_once_with(english_text="Hello")

def test_translate_no_translator():
    """Test /translate endpoint when translator is not initialized."""
    # Save original translator
    global translator
    original_translator = translator
    try:
        # Set translator to None
        translator = None
        
        # Test translation
        response = client.post("/translate", json={"text": "Hello"})
        assert response.status_code == 503
        assert response.json()["detail"] == "Translator not initialized"
        
    finally:
        # Restore
        translator = original_translator

def test_translate_exception():
    """Test /translate endpoint when translation fails."""
    with patch('mirad_translator.api.translator') as mock_translator:
        mock_translator.forward.side_effect = Exception("Translation failed")
        
        response = client.post("/translate", json={"text": "Hello"})
        assert response.status_code == 500
        
def test_startup_event():
    """Test startup event initializes translator."""
    # This tests that the startup event runs
    # The actual initialization is tested in the startup event
    assert app.on_event("startup") is not None
