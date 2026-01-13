from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import uvicorn
import logging
import json
from providers import ProviderFactory
from rag_client import get_relevant_context

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Chatbot API",
    description="Modular chatbot API supporting multiple LLM providers (Gemini, Ollama, OpenAI, Claude)",
    version="1.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., description="The user's message", min_length=1)
    provider: str = Field(default="gemini", description="LLM provider to use")
    model: Optional[str] = Field(default=None, description="Model name (provider-specific)")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Additional provider parameters")
    use_rag: bool = Field(default=True, description="Whether to use RAG for context retrieval")


class ChatResponse(BaseModel):
    """Chat response model."""
    prompt: str = Field(..., description="The prompt that was sent to the LLM")
    response: str = Field(..., description="The LLM's response")
    provider: str = Field(..., description="Provider that was used")
    model: str = Field(..., description="Model that was used")


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Overall service status")
    providers: Dict[str, bool] = Field(..., description="Status of each provider")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the chatbot and get a response.
    
    Args:
        request: Chat request with message and provider information
        
    Returns:
        ChatResponse with the LLM's response
        
    Raises:
        HTTPException: If provider is unavailable or request fails
    """
    try:
        logger.info(f"Chat request - Provider: {request.provider}, Message: {request.message[:50]}..., RAG: {request.use_rag}")
        
        # Get provider instance
        provider = ProviderFactory.get_provider(request.provider)
        
        # Get model name
        model_name = request.model or provider.get_default_model()
        
        # Get additional parameters
        params = request.parameters or {}
        
        # Get relevant context from RAG if enabled
        context = ""
        if request.use_rag:
            context = get_relevant_context(request.message, top_k=3)
        
        # Build the message with context if available
        if context:
            enhanced_message = f"""Context information:
                {context}

                User question: {request.message}

                Answer the question based on the context above. If the context doesn't help answer the question, use your general knowledge."""
            logger.info(f"Enhanced message with {len(context)} chars of context")
        else:
            enhanced_message = request.message
        
        # Send message to provider
        response_text = await provider.chat(
            message=enhanced_message,
            model=model_name,
            **params
        )
        
        logger.info(f"Chat response - Provider: {request.provider}, Response length: {len(response_text)}")
        
        return ChatResponse(
            prompt=enhanced_message,
            response=response_text,
            provider=request.provider,
            model=model_name
        )
    
    except ValueError as e:
        logger.error(f"Invalid provider or configuration: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Send a message and get a streaming response (SSE).
    """
    try:
        logger.info(f"Stream request - Provider: {request.provider}, RAG: {request.use_rag}")
        
        provider = ProviderFactory.get_provider(request.provider)
        model_name = request.model or provider.get_default_model()
        params = request.parameters or {}
        
        # Get relevant context from RAG if enabled
        context = ""
        if request.use_rag:
            context = get_relevant_context(request.message, top_k=3)
        
        # Build the message with context if available
        if context:
            enhanced_message = f"""Context information:
                {context}

                User question: {request.message}

                Answer the question based on the context above. If the context doesn't help answer the question, use your general knowledge."""
            logger.info(f"Enhanced stream message with {len(context)} chars of context")
        else:
            enhanced_message = request.message

        async def generate():
            try:
                async for chunk in provider.chat_stream(
                    message=enhanced_message,
                    model=model_name,
                    **params
                ):
                    data = json.dumps({
                        "token": chunk,
                        "provider": request.provider,
                        "model": model_name
                    })
                    yield f"data: {data}\n\n"
            except Exception as e:
                logger.error(f"Stream error: {str(e)}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check the health of the service and all providers.
    
    Returns:
        HealthResponse with service status and provider availability
    """
    try:
        # Check all providers
        available_providers = ProviderFactory.get_available_providers()
        provider_status = {}
        
        for provider_name in available_providers:
            is_healthy = await ProviderFactory.check_provider_health(provider_name)
            provider_status[provider_name] = is_healthy
        
        # Overall status is healthy if at least one provider is available
        overall_status = "healthy" if any(provider_status.values()) else "unhealthy"
        
        logger.info(f"Health check - Status: {overall_status}, Providers: {provider_status}")
        
        return HealthResponse(
            status=overall_status,
            providers=provider_status
        )
    
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking service health: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "/chat": "POST - Send a message to the chatbot",
            "/health": "GET - Check service health",
            "/docs": "GET - Interactive API documentation"
        }
    }


if __name__ == "__main__":
    logger.info("Starting Chatbot API server...")
    uvicorn.run(
        "chatbot:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
