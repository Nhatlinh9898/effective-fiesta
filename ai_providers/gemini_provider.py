"""
Google Gemini Provider
"""
from typing import Dict, Any, Optional, List
from .base_provider import BaseAIProvider


class GeminiProvider(BaseAIProvider):
    """
    Google Gemini provider
    Supports Gemini Pro, Gemini Pro Vision
    """
    
    def __init__(self, api_key: str, model: str = "gemini-pro", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.client = None
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize Gemini client"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai
            self.model_instance = genai.GenerativeModel(self.model)
        except ImportError:
            raise ImportError("google-generativeai package not installed. Run: uv add google-generativeai")
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None,
                      **kwargs) -> str:
        """Generate text using Gemini"""
        # Combine system prompt with user prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        # Generation config
        generation_config = {
            "temperature": kwargs.get("temperature", 0.7),
            "max_output_tokens": kwargs.get("max_tokens", 4096),
        }
        
        if "top_p" in kwargs:
            generation_config["top_p"] = kwargs["top_p"]
        if "top_k" in kwargs:
            generation_config["top_k"] = kwargs["top_k"]
        
        try:
            response = await self.model_instance.generate_content_async(
                full_prompt,
                generation_config=generation_config
            )
            return response.text
        except Exception as e:
            return f"Error calling Gemini API: {str(e)}"
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat completion with Gemini"""
        # Convert messages to Gemini format
        # Gemini uses a different chat format
        chat = self.model_instance.start_chat(history=[])
        
        # Build conversation
        conversation = []
        for msg in messages:
            if msg["role"] == "system":
                # Prepend system message to first user message
                conversation.append(("system", msg["content"]))
            elif msg["role"] == "user":
                conversation.append(("user", msg["content"]))
            elif msg["role"] == "assistant":
                conversation.append(("model", msg["content"]))
        
        # Get last user message
        last_message = messages[-1]["content"] if messages else ""
        
        # Add system context if present
        system_context = ""
        for role, content in conversation:
            if role == "system":
                system_context += content + "\n\n"
        
        full_message = system_context + last_message
        
        try:
            response = await chat.send_message_async(full_message)
            return response.text
        except Exception as e:
            return f"Error calling Gemini API: {str(e)}"
    
    def get_available_models(self) -> List[str]:
        """Get available Gemini models"""
        return [
            "gemini-pro",
            "gemini-pro-vision",
            "gemini-1.5-pro",
            "gemini-1.5-flash"
        ]
