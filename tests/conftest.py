"""Shared pytest fixtures for mirad_tts tests."""

import pytest


@pytest.fixture
def sample_mirad_text():
    """A simple Mirad sentence used across multiple test modules."""
    return "At tixe Mirad."