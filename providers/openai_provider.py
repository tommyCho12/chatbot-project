import os
from typing import Optional
from providers.base import BaseLLMProvider

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider implementation."""
    
    def __init__(self, api_key: Optional[str] = None, default_model: str = "gpt-3.5-turbo"):
        """
        Initialize the OpenAI provider.
        
        Args:
            api_key: OpenAI API key (can also be set via OPENAI_API_KEY env var)
            default_model: Default model to use (default: gpt-3.5-turbo)
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not installed. Install with: pip install openai")
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.default_model = default_model
        self.client = None
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
    
    def _get_client(self):
        """Get or create the OpenAI client."""
        if self.client is None:
            self.client = AsyncOpenAI(api_key=self.api_key)
        return self.client
    
    async def chat(self, message: str, model: Optional[str] = None, **kwargs) -> str:
        """
        Send a message to OpenAI and get a response.
        
        Args:
            message: The user's message
            model: Model name to use (e.g., gpt-4, gpt-3.5-turbo)
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            The LLM's response
        """
        try:
            client = self._get_client()
            model_name = model or self.default_model
            
            response = await client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": message}
                ],
                **kwargs
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI chat error: {str(e)}")
    
    async def is_available(self) -> bool:
        """
        Check if OpenAI API is available.
        
        Returns:
            True if API key is set and valid, False otherwise
        """
        if not self.api_key:
            return False
        
        try:
            client = self._get_client()
            # Try to list models to verify API key
            await client.models.list()
            return True
        except Exception:
            return False
    
    def get_default_model(self) -> str:
        """Get the default model name."""
        return self.default_model
