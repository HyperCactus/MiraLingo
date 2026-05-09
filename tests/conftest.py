<<<<<<< HEAD
"""Shared pytest fixtures for mirad_tts tests."""
=======
"""Shared pytest fixtures for the Mirad TTS test suite."""
>>>>>>> milestone/M001

import pytest


@pytest.fixture
<<<<<<< HEAD
def sample_mirad_text():
    """A simple Mirad sentence used across multiple test modules."""
=======
def sample_mirad_text() -> str:
    """A representative multi-word Mirad sentence used across integration tests."""
>>>>>>> milestone/M001
    return "At tixe Mirad."