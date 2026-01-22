"""
Anthropic Provider - Claude models
"""
from typing import Dict, Any, Optional, List
from .base_provider import BaseAIProvider


class AnthropicProvider(BaseAIProvider):
    """
    Anthropic Claude provider
    Supports Claude 3 Opus, Sonnet, Haiku
    """
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.client = None
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize Anthropic client"""
        try:
            from anthropic import AsyncAnthropic
            self.client = AsyncAnthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("anthropic package not installed. Run: uv add anthropic")
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None,
                      **kwargs) -> str:
        """Generate text using Anthropic"""
        messages = [{"role": "user", "content": prompt}]
        
        # Anthropic uses system parameter separately
        params = {}
        if system_prompt:
            params["system"] = system_prompt
        
        return await self.chat(messages, **params, **kwargs)
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat completion with Anthropic"""
        # Default parameters
        params = {
            "model": self.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 4096),
            "temperature": kwargs.get("temperature", 0.7),
        }
        
        # Add system prompt if provided
        if "system" in kwargs:
            params["system"] = kwargs["system"]
        
        # Add optional parameters
        if "top_p" in kwargs:
            params["top_p"] = kwargs["top_p"]
        if "top_k" in kwargs:
            params["top_k"] = kwargs["top_k"]
        
        try:
            response = await self.client.messages.create(**params)
            return response.content[0].text
        except Exception as e:
            return f"Error calling Anthropic API: {str(e)}"
    
    def get_available_models(self) -> List[str]:
        """Get available Anthropic models"""
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
