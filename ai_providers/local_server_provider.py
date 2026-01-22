"""
Local AI Server Provider - calls a local FastAPI server
"""
from typing import Dict, Any, Optional, List
import os
import httpx

from .base_provider import BaseAIProvider


class LocalServerProvider(BaseAIProvider):
    """
    Local server provider
    """

    def __init__(self, model: str = "llama3.1:8b-instruct-q4_0", **kwargs):
        super().__init__(api_key="", model=model, **kwargs)
        self.base_url = kwargs.get("base_url") or os.getenv("LOCAL_AI_SERVER_URL", "http://localhost:8000")
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=120.0)

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate text using local server"""
        payload = {
            "prompt": prompt,
            "model": self.model,
        }
        if system_prompt:
            payload["system_prompt"] = system_prompt
        if "options" in kwargs:
            payload["options"] = kwargs["options"]

        try:
            response = await self.client.post("/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("text", "")
        except Exception as e:
            return f"Error calling Local AI Server: {str(e)}"

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat completion with local server"""
        payload = {
            "messages": messages,
            "model": self.model,
        }
        if "options" in kwargs:
            payload["options"] = kwargs["options"]

        try:
            response = await self.client.post("/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("text", "")
        except Exception as e:
            return f"Error calling Local AI Server: {str(e)}"

    def get_available_models(self) -> List[str]:
        """Fallback model list if server models not fetched."""
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
