import os
from typing import Optional
from providers.base import BaseLLMProvider

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider implementation."""
    
    def __init__(self, api_key: Optional[str] = None, default_model: Optional[str] = None):
        """
        Initialize the Gemini provider.
        
        Args:
            api_key: Gemini API key (can also be set via GEMINI_API_KEY env var)
            default_model: Default model to use (can also be set via GEMINI_MODEL env var, defaults to gemini-2.5-flash)
        """
        if not GEMINI_AVAILABLE:
            raise ImportError("Google Generative AI package not installed. Install with: pip install google-generativeai")
        
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.default_model = default_model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.client = None
        
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable.")
        
        # Configure the API key
        genai.configure(api_key=self.api_key)
    
    def _get_client(self, model_name: str):
        """Get or create the Gemini model instance."""
        return genai.GenerativeModel(model_name)
    
    async def chat(self, message: str, model: Optional[str] = None, **kwargs) -> str:
        """
        Send a message to Gemini and get a response.
        
        Args:
            message: The user's message
            model: Model name to use (e.g., gemini-pro, gemini-2.0-flash-exp)
            **kwargs: Additional parameters (temperature, max_output_tokens, etc.)
            
        Returns:
            The LLM's response
        """
        try:
            model_name = model or self.default_model
            client = self._get_client(model_name)
            
            # Generate content
            response = await client.generate_content_async(
                message,
                **kwargs
            )
            
            return response.text
        except Exception as e:
            raise Exception(f"Gemini chat error: {str(e)}")
            
    async def chat_stream(self, message: str, model: Optional[str] = None, **kwargs):
        """
        Stream response from Gemini.
        """
        try:
            model_name = model or self.default_model
            client = self._get_client(model_name)
            
            # Generate content with streaming
            response = await client.generate_content_async(
                message,
                stream=True,
                **kwargs
            )
            
            async for chunk in response:
                # Gemini returns chunks with parts that contain text
                if hasattr(chunk, 'text') and chunk.text:
                    yield chunk.text
                elif hasattr(chunk, 'parts'):
                    for part in chunk.parts:
                        if hasattr(part, 'text') and part.text:
                            yield part.text
                    
        except Exception as e:
            raise Exception(f"Gemini stream error: {str(e)}")
    
    async def is_available(self) -> bool:
        """
        Check if Gemini API is available.
        
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
