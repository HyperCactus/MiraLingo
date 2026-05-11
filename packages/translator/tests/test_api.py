from fastapi.testclient import TestClient
from mirad_translator.api import app


def test_health():
    """Test /health endpoint."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_translate():
    """Test /translate endpoint."""
    client = TestClient(app)
    response = client.post("/translate", json={"text": "Hello"})
    assert response.status_code == 200
    assert "translation" in response.json()
