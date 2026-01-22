"""
Base Agent Class - Foundation for all specialized agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class BaseAgent(ABC):
    """
    Base class for all AI agents in the system
    Each agent has specific responsibilities and capabilities
    """
    
    def __init__(self, name: str, description: str, ai_provider=None):
        self.name = name
        self.description = description
        self.ai_provider = ai_provider
        self.memory: List[Dict[str, Any]] = []
        self.created_at = datetime.now()
        
    @abstractmethod
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task - must be implemented by each agent
        
        Args:
            task: Dictionary containing task details
            
        Returns:
            Dictionary with results
        """
        pass
    
    def add_to_memory(self, interaction: Dict[str, Any]):
        """Add interaction to agent memory"""
        self.memory.append({
            "timestamp": datetime.now().isoformat(),
            "interaction": interaction
        })
        
    def get_memory(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve agent memory"""
        if limit:
            return self.memory[-limit:]
        return self.memory
    
    def clear_memory(self):
        """Clear agent memory"""
        self.memory = []
        
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": self.name,
            "description": self.description,
            "memory_size": len(self.memory),
            "created_at": self.created_at.isoformat(),
            "ai_provider": self.ai_provider.__class__.__name__ if self.ai_provider else None
        }
    
    async def call_ai(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """
        Call AI provider with prompt
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            **kwargs: Additional parameters for AI call
            
        Returns:
            AI response as string
        """
        if not self.ai_provider:
            raise ValueError(f"No AI provider configured for agent {self.name}")
        
        response = await self.ai_provider.generate(
            prompt=prompt,
            system_prompt=system_prompt or f"You are {self.name}. {self.description}",
            **kwargs
        )
        
        # Add to memory
        self.add_to_memory({
            "type": "ai_call",
            "prompt": prompt,
            "response": response
        })
        
        return response
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "status": self.get_status()
        }
