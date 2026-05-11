"""
Ollama language model interface.
"""

class OllamaLM:
    def __init__(self, model: str = "qwen3.5:4b"):
        self.model = model

    def generate(self, prompt: str) -> str:
        return "Generated response from " + self.model
