from typing import Dict, Type
from providers.base import BaseLLMProvider

# Optional providers
_OPTIONAL_PROVIDERS = {}

try:
    from providers.ollama_provider import OllamaProvider
    _OPTIONAL_PROVIDERS['ollama'] = OllamaProvider
except ImportError:
    pass

try:
    from providers.openai_provider import OpenAIProvider
    _OPTIONAL_PROVIDERS['openai'] = OpenAIProvider
except ImportError:
    pass

try:
    from providers.anthropic_provider import AnthropicProvider
    _OPTIONAL_PROVIDERS['anthropic'] = AnthropicProvider
except ImportError:
    pass

try:
    from providers.gemini_provider import GeminiProvider
    _OPTIONAL_PROVIDERS['gemini'] = GeminiProvider
except ImportError:
    pass


class ProviderFactory:
    """Factory for creating LLM provider instances."""
    
    _providers: Dict[str, Type[BaseLLMProvider]] = {
        **_OPTIONAL_PROVIDERS
    }
    
    _instances: Dict[str, BaseLLMProvider] = {}
    
    @classmethod
    def get_provider(cls, provider_name: str) -> BaseLLMProvider:
        """
        Get a provider instance by name.
        
        Args:
            provider_name: Name of the provider ('ollama', 'openai', 'anthropic')
            
        Returns:
            Provider instance
            
        Raises:
            ValueError: If provider is not supported or not available
        """
        provider_name = provider_name.lower()
        
        if provider_name not in cls._providers:
            available = ', '.join(cls._providers.keys())
            raise ValueError(
                f"Provider '{provider_name}' not supported. "
                f"Available providers: {available}"
            )
        
        # Return cached instance if exists
        if provider_name in cls._instances:
            return cls._instances[provider_name]
        
        # Create new instance
        try:
            provider_class = cls._providers[provider_name]
            instance = provider_class()
            cls._instances[provider_name] = instance
            return instance
        except Exception as e:
            raise ValueError(f"Failed to initialize provider '{provider_name}': {str(e)}")
    
    @classmethod
    def get_available_providers(cls) -> list[str]:
        """
        Get list of available provider names.
        
        Returns:
            List of provider names
        """
        return list(cls._providers.keys())
    
    @classmethod
    async def check_provider_health(cls, provider_name: str) -> bool:
        """
        Check if a provider is healthy and available.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            True if provider is healthy, False otherwise
        """
        try:
            provider = cls.get_provider(provider_name)
            return await provider.is_available()
        except Exception:
            return False


__all__ = ['ProviderFactory', 'BaseLLMProvider']
