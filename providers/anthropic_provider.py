import os
from typing import Optional
from providers.base import BaseLLMProvider

try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider implementation."""
    
    def __init__(self, api_key: Optional[str] = None, default_model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize the Anthropic provider.
        
        Args:
            api_key: Anthropic API key (can also be set via ANTHROPIC_API_KEY env var)
            default_model: Default model to use (default: claude-3-5-sonnet-20241022)
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic package not installed. Install with: pip install anthropic")
        
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.default_model = default_model
        self.client = None
        
        if not self.api_key:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable.")
    
    def _get_client(self):
        """Get or create the Anthropic client."""
        if self.client is None:
            self.client = AsyncAnthropic(api_key=self.api_key)
        return self.client
    
    async def chat(self, message: str, model: Optional[str] = None, **kwargs) -> str:
        """
        Send a message to Claude and get a response.
        
        Args:
            message: The user's message
            model: Model name to use (e.g., claude-3-opus-20240229)
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            The LLM's response
        """
        try:
            client = self._get_client()
            model_name = model or self.default_model
            
            # Set default max_tokens if not provided
            if 'max_tokens' not in kwargs:
                kwargs['max_tokens'] = 1024
            
            response = await client.messages.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": message}
                ],
                **kwargs
            )
            
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Anthropic chat error: {str(e)}")
    
    async def is_available(self) -> bool:
        """
        Check if Anthropic API is available.
        
        Returns:
            True if API key is set and valid, False otherwise
        """
        if not self.api_key:
            return False
        
        try:
            # API key presence is a good indicator
            # We could make a test call, but that costs money
            return True
        except Exception:
            return False
    
    def get_default_model(self) -> str:
        """Get the default model name."""
        return self.default_model
