import dspy
import requests
import json
from typing import List, Dict, Any, Optional

class OllamaLM(dspy.LM):
    """DSPy LM adapter for Ollama using the native HTTP /api/chat endpoint.
    
    Bypasses litellm entirely to avoid compatibility issues with thinking-mode
    models (e.g. qwen3.5) that split output into reasoning + content fields.
    
    Supports:
    - Connection validation and model availability checks at init time
    - DSPy's calling convention via __call__ / forward
    - Structured JSON output when ``format`` is passed
    - ``/no_think`` system prefix to disable thinking mode on reasoning models
    """
    
    def __init__(self, model: str = "qwen3.5:4b", base_url: str = "http://localhost:11434"):
        self._raw_model = model
        self.base_url = base_url
        self.chat_url = f"{base_url}/api/chat"
        
        # Validate Ollama connection and model availability
        self._check_ollama(base_url, model)
        
        # Initialize dspy.LM base (required for DSPy compatibility)
        # We use a placeholder model string; actual calls go through _call
        super().__init__(model=f"ollama/{model}")
        self.history: List[Dict[str, Any]] = []
    
    @staticmethod
    def _check_ollama(base_url: str, model: str) -> None:
        """Verify Ollama is reachable and the requested model is available."""
        try:
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                raise Exception(f"Ollama returned status {response.status_code}: {response.text}")
            tags = response.json().get("models", [])
            available = [m["name"] for m in tags]
            base_model = model.split(":")[0]
            if not any(m.startswith(base_model) for m in available):
                raise Exception(
                    f"Model {model!r} not found in Ollama. Available: {available}"
                )
        except requests.exceptions.ConnectionError:
            raise Exception(f"Failed to connect to Ollama. Is Ollama running at {base_url}?")
    
    def __call__(self, prompt=None, messages=None, **kwargs):
        """Call the Ollama chat API.
        
        Accepts either a string prompt or a list of messages (OpenAI-style).
        Returns a list of completion strings (DSPy convention).
        """
        if messages is not None:
            ollama_messages = list(messages)
        elif prompt is not None:
            # Single string prompt → user message
            if isinstance(prompt, list):
                # DSPy sometimes passes a list of prompts
                return [self._single_call(p, **kwargs) for p in prompt]
            ollama_messages = [{"role": "user", "content": prompt}]
        else:
            raise ValueError("Either prompt or messages must be provided")
        
        return [self._chat(ollama_messages, **kwargs)]
    
    def _chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send messages to Ollama /api/chat and return the assistant response text."""
        payload = {
            "model": self._raw_model,
            "messages": messages,
            "stream": False,
            "think": False,  # Disable thinking mode for cleaner output
        }
        # Allow caller to request structured JSON output
        if "format" in kwargs:
            payload["format"] = kwargs["format"]
        if "options" in kwargs:
            payload["options"] = kwargs["options"]
        
        try:
            response = requests.post(self.chat_url, json=payload, timeout=120)
            if response.status_code != 200:
                raise Exception(f"Ollama API error {response.status_code}: {response.text}")
            result = response.json()
            content = result.get("message", {}).get("content", "")
            self.history.append({
                "messages": messages,
                "response": content,
            })
            return content
        except requests.exceptions.Timeout:
            raise Exception("Ollama API request timed out after 120s")
    
    def _single_call(self, prompt: str, **kwargs) -> str:
        """Call with a single string prompt."""
        messages = [{"role": "user", "content": prompt}]
        return self._chat(messages, **kwargs)