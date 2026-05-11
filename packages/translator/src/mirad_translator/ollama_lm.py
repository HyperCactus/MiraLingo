import dspy
import requests
from typing import Optional, Dict, Any

class OllamaLM(dspy.LM):
    def __init__(self, model: str = "qwen3.5:4b", base_url: str = "http://localhost:11434"):
        super().__init__(model=model)
        self.model = model
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
        self.history = []
        
        # Test connection
        try:
            response = requests.post(
                f"{base_url}/api/tags",
                json={}
            )
            if response.status_code != 200:
                raise Exception(f"Ollama connection failed: {response.text}")
            # Check if model is available
            tags = response.json().get('models', [])
            if not any(m['name'] == model for m in tags):
                raise Exception(f"Model {model} not found in Ollama. Available models: {[m['name'] for m in tags]}")
        except requests.exceptions.ConnectionError:
            raise Exception("Failed to connect to Ollama. Is Ollama running at {base_url}?")
        
    def _call(self, prompt: str, **kwargs) -> str:
        """
        Makes a call to the Ollama API to generate a response.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(self.api_url, json=payload)
        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.text}")
        
        result = response.json()
        generated_text = result.get("response", "")
        
        # Log the interaction
        self.history.append({
            "prompt": prompt,
            "response": generated_text
        })
        
        return generated_text
    
    def _generate(self, prompts, **kwargs):
        return [self._call(prompt, **kwargs) for prompt in prompts]