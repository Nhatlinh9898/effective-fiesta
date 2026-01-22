"""
Base AI Provider - Abstract class for all AI providers
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class BaseAIProvider(ABC):
    """
    Base class for AI providers (OpenAI, Anthropic, Gemini, etc.)
    """
    
    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self.config = kwargs
        
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, 
                      **kwargs) -> str:
        """
        Generate text from prompt
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Chat completion with message history
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters
            
        Returns:
            AI response
        """
        pass
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get provider information"""
        return {
            "provider": self.__class__.__name__,
            "model": self.model,
            "config": self.config
        }
