"""
Ollama Provider - Local models via Ollama API
"""
from typing import Dict, Any, Optional, List
import os
import httpx

from .base_provider import BaseAIProvider


class OllamaProvider(BaseAIProvider):
    """
    Local Ollama provider
    Supports local models (llama3.1, mistral, phi3, etc.)
    """

    def __init__(self, model: str = "llama3.1", **kwargs):
        super().__init__(api_key="", model=model, **kwargs)
        self.base_url = kwargs.get("base_url") or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=120.0)

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate text using Ollama"""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
        }

        try:
            response = await self.client.post("/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except Exception as e:
            return f"Error calling Ollama API: {str(e)}"

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat completion with Ollama"""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }

        try:
            response = await self.client.post("/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            message = data.get("message", {})
            return message.get("content", "")
        except Exception as e:
            return f"Error calling Ollama API: {str(e)}"

    def get_available_models(self) -> List[str]:
        """Get available Ollama models"""
        return [
            "phi3:instruct-q4_0",
            "mistral:instruct-q4_0",
            "llama3.1:8b-instruct-q4_0",
            "llama3.1:8b-instruct-q5_0",
            "phi3",
            "mistral",
            "llama3.1",
            "llama3",
            "qwen2.5:7b",
        ]
