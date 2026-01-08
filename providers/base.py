from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def chat(self, message: str, model: Optional[str] = None, **kwargs) -> str:
        """
        Send a message to the LLM and get a response.
        
        Args:
            message: The user's message
            model: Optional model name to use (provider-specific)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            The LLM's response as a string
        """
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check if the provider is available and configured correctly.
        
        Returns:
            True if the provider is available, False otherwise
        """
        pass
    
    @abstractmethod
    def get_default_model(self) -> str:
        """
        Get the default model for this provider.
        
        Returns:
            The default model name
        """
        pass
