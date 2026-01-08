import os
from typing import Optional
import ollama
from providers.base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    """Ollama LLM provider implementation."""
    
    def __init__(self, base_url: Optional[str] = None, default_model: str = "llama3"):
        """
        Initialize the Ollama provider.
        
        Args:
            base_url: Ollama API base URL (default: http://localhost:11434)
            default_model: Default model to use (default: llama3)
        """
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.default_model = default_model
        self.client = None
    
    def _get_client(self):
        """Get or create the Ollama client."""
        if self.client is None:
            self.client = ollama.Client(host=self.base_url)
        return self.client
    
    async def chat(self, message: str, model: Optional[str] = None, **kwargs) -> str:
        """
        Send a message to Ollama and get a response.
        
        Args:
            message: The user's message
            model: Model name to use (defaults to llama3)
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            The LLM's response
        """
        try:
            client = self._get_client()
            model_name = model or self.default_model
            
            response = client.chat(
                model=model_name,
                messages=[
                    {
                        'role': 'user',
                        'content': message,
                    },
                ],
                **kwargs
            )
            
            return response['message']['content']
        except Exception as e:
            raise Exception(f"Ollama chat error: {str(e)}")
            
    async def chat_stream(self, message: str, model: Optional[str] = None, **kwargs):
        """
        Stream response from Ollama.
        """
        try:
            client = self._get_client()
            model_name = model or self.default_model
            
            # Using synchronous stream=True since the official client supports it
            stream = client.chat(
                model=model_name,
                messages=[{'role': 'user', 'content': message}],
                stream=True,
                **kwargs
            )
            
            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']
                    
        except Exception as e:
            raise Exception(f"Ollama stream error: {str(e)}")
    
    async def is_available(self) -> bool:
        """
        Check if Ollama is available.
        
        Returns:
            True if Ollama is reachable, False otherwise
        """
        try:
            client = self._get_client()
            # Try to list models to verify connectivity
            client.list()
            return True
        except Exception:
            return False
    
    def get_default_model(self) -> str:
        """Get the default model name."""
        return self.default_model
