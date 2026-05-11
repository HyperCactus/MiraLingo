"""Integration tests against a live Ollama instance.

These tests require Ollama to be running with the configured model available.
They are skipped automatically if Ollama is unreachable.

Run with:  pytest tests/test_ollama_integration.py -v
"""
import os
import subprocess

import pytest
import requests
import dspy

# Configurable model and URL
OLLAMA_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3.5:4b")


def _ollama_available():
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _ollama_available(),
    reason=f"Ollama not reachable at {OLLAMA_URL}",
)

from mirad_translator.ollama_lm import OllamaLM
from mirad_translator.translate import TranslatorModule


# ── OllamaLM connectivity integration ──────────────────────────────

class TestOllamaLMReal:
    """Test the real OllamaLM adapter against a running Ollama service."""

    def test_ollama_lm_connects(self):
        """OllamaLM() should connect and validate the model without raising."""
        lm = OllamaLM(model=OLLAMA_MODEL, base_url=OLLAMA_URL)
        assert lm.model == f"ollama/{OLLAMA_MODEL}"

    def test_ollama_lm_model_not_found_raises(self):
        """OllamaLM should raise if the model doesn't exist."""
        with pytest.raises(Exception, match="not found"):
            OllamaLM(model="nonexistent-model-xyz", base_url=OLLAMA_URL)

    def test_ollama_lm_generates_text(self):
        """Calling the LM through DSPy should produce non-empty output."""
        lm = OllamaLM(model=OLLAMA_MODEL, base_url=OLLAMA_URL)
        result = lm("Say hello in one word.")
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], str)
        assert len(result[0].strip()) > 0


# ── DSPy TranslatorModule with real LM ──────────────────────────────

class TestTranslatorModuleReal:
    """Test the full DSPy pipeline with a real Ollama LM.

    The 4B model has no Mirad training data, so translations won't be
    accurate. We verify the pipeline wiring produces structurally correct
    output (both mirad_text and confidence fields populated).
    """

    @pytest.fixture(autouse=True)
    def setup_lm(self):
        """Configure DSPy with the real Ollama LM for every test."""
        self.lm = OllamaLM(model=OLLAMA_MODEL, base_url=OLLAMA_URL)
        dspy.configure(lm=self.lm)

    def test_translate_simple_greeting(self):
        """Translation should return mirad_text and confidence."""
        translator = TranslatorModule()
        result = translator.forward(english_text="Hello")
        assert hasattr(result, "mirad_text")
        assert hasattr(result, "confidence")
        assert isinstance(result.mirad_text, str)
        assert len(result.mirad_text.strip()) > 0

    def test_translate_returns_mirad_content(self):
        """Translation output should contain non-empty text."""
        translator = TranslatorModule()
        result = translator.forward(english_text="good morning")
        text = result.mirad_text.strip()
        assert len(text) > 0, "mirad_text should not be empty"

    def test_translate_confidence_is_string(self):
        """Confidence should be a non-empty string."""
        translator = TranslatorModule()
        result = translator.forward(english_text="How are you?")
        conf = result.confidence
        assert conf is not None
        assert isinstance(conf, str)
        assert len(conf.strip()) > 0


# ── CLI integration with real Ollama ────────────────────────────────

class TestCLIReal:
    """Test the CLI with a real Ollama connection."""

    def test_cli_help(self):
        """mirad-translate --help should work without Ollama."""
        result = subprocess.run(
            ["python", "-m", "mirad_translator.cli", "--help"],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "Text to translate" in result.stdout

    def test_cli_connects_to_ollama(self):
        """CLI should connect to Ollama and produce output (not a connection error)."""
        result = subprocess.run(
            ["python", "-m", "mirad_translator.cli", "Hello"],
            capture_output=True, text=True, timeout=120,
        )
        # We accept exit 0 (success) or exit 1 (translation parse error on small models).
        # We reject connection-refused or model-not-found errors.
        stderr = result.stderr.lower()
        assert "connectionrefused" not in stderr, "Cannot reach Ollama"
        # Model-not-found should only fail if the model actually isn't available
        assert "model" not in stderr or "translation" in stderr.lower(), \
            f"Model not found error: {result.stderr}"