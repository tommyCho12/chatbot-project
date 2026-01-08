# Chatbot Service Implementation Plan

This plan outlines the implementation of a Python-based chatbot service using Ollama as the local LLM backend, exposed via a REST API, and containerized using Docker.

## User Review Required

> [!IMPORTANT]
> **Model Configuration**: Using `llama3` as the default Ollama model. The architecture will be modular to support switching between different LLM providers (Ollama, OpenAI GPT, Anthropic Claude) without changing the API interface.

> [!IMPORTANT]
> **Port Configuration**: The API will be exposed on port 8000 by default. The service expects Ollama to be running on `http://localhost:11434` (Ollama's default port). Let me know if you need different ports.

## Proposed Changes

### API Service Component

#### [NEW] [chatbot.py](file:///c:/AI_projects/chatbot-project/chatbot.py)
Main FastAPI application with the following features:
- `/chat` POST endpoint for sending messages and receiving responses
- `/health` GET endpoint for health checks
- Request/response models using Pydantic
- CORS middleware for cross-origin requests
- Comprehensive error handling
- Provider factory pattern for LLM backend selection

**API Endpoint Details:**
```
POST /chat
Request: {"message": "Hello, how are you?", "provider": "ollama", "model": "llama3"}
Response: {"response": "I'm doing well, thank you!", "provider": "ollama", "model": "llama3"}

POST /chat/stream
Request: {"message": "Tell me a story", "provider": "ollama", "model": "llama3"}
Response: Streaming Server-Sent Events (SSE)
data: {"token": "Once"}
data: {"token": " upon"}
data: {"token": " a"}
...

GET /health
Response: {"status": "healthy", "providers": {"ollama": true, "openai": false, "anthropic": false}}
```

#### [NEW] [providers/base.py](file:///c:/AI_projects/chatbot-project/providers/base.py)
Abstract base class for LLM providers:
- Defines common interface for all providers
- `chat()` method signature
- `is_available()` health check method

#### [NEW] [providers/ollama_provider.py](file:///c:/AI_projects/chatbot-project/providers/ollama_provider.py)
Ollama-specific implementation:
- Uses `ollama` Python package
- Integrates with local Ollama service
- Default model: `llama3`

#### [NEW] [providers/openai_provider.py](file:///c:/AI_projects/chatbot-project/providers/openai_provider.py)
OpenAI GPT implementation (optional, requires API key):
- Uses `openai` Python package
- Supports GPT-4, GPT-3.5-turbo, etc.

#### [NEW] [providers/anthropic_provider.py](file:///c:/AI_projects/chatbot-project/providers/anthropic_provider.py)
Anthropic Claude implementation (optional, requires API key):
- Uses `anthropic` Python package
- Supports Claude 3 models

#### [NEW] [providers/__init__.py](file:///c:/AI_projects/chatbot-project/providers/__init__.py)
Provider factory and registration:
- Factory method to instantiate providers
- Registry of available providers

---

### Dependencies

#### [NEW] [requirements.txt](file:///c:/AI_projects/chatbot-project/requirements.txt)
Python dependencies:
- `fastapi` - Modern web framework for building APIs
- `uvicorn[standard]` - ASGI server for running FastAPI
- `ollama` - Official Ollama Python client
- `pydantic` - Data validation using Python type hints
- `python-dotenv` - Environment variable management
- `openai` (optional) - OpenAI API client for GPT models
- `anthropic` (optional) - Anthropic API client for Claude models

---

### Docker Configuration

#### [NEW] [Dockerfile](file:///c:/AI_projects/chatbot-project/Dockerfile)
Multi-stage Docker build:
- Base image: `python:3.11-slim`
- Installs dependencies from requirements.txt
- Copies application code
- Exposes port 8000
- Uses uvicorn as the server
- Non-root user for security

#### [NEW] [docker-compose.yml](file:///c:/AI_projects/chatbot-project/docker-compose.yml)
Docker Compose configuration with two services:
1. **ollama** - Ollama service container
   - Uses official `ollama/ollama` image
   - GPU support (optional, can be removed if no GPU available)
   - Volume for model persistence
   - Port 11434
2. **chatbot** - Your chatbot API service
   - Builds from local Dockerfile
   - Depends on ollama service
   - Port 8000
   - Network connectivity to ollama
   - Restart policy

#### [NEW] [.dockerignore](file:///c:/AI_projects/chatbot-project/.dockerignore)
Excludes unnecessary files from Docker build context:
- Python cache files
- Virtual environments
- Git files
- Documentation

---

### Configuration

#### [NEW] [.env.example](file:///c:/AI_projects/chatbot-project/.env.example)
Environment variable template:
- `OLLAMA_BASE_URL` - URL for Ollama service
- `DEFAULT_MODEL` - Default Ollama model to use
- `API_HOST` - API server host
- `API_PORT` - API server port

---

### Documentation

#### [NEW] [README.md](file:///c:/AI_projects/chatbot-project/README.md)
Comprehensive documentation including:
- Project overview
- Prerequisites (Docker, Docker Compose)
- Setup instructions
- Running locally vs Docker
- API usage examples with curl
- Provider configuration (Ollama, OpenAI, Anthropic)
- Model management
- Troubleshooting guide

#### [NEW] [specs/chatbot.feature](file:///c:/AI_projects/chatbot-project/specs/chatbot.feature)
Gherkin specification file defining:
- Chat endpoint behavior
- Health check scenarios
- Provider switching functionality
- Error handling scenarios
- Authentication and validation rules

## Verification Plan

### Automated Tests
1. **Health Check Test**: Verify the `/health` endpoint returns 200 and correct status
2. **Chat Endpoint Test**: Send a test message and verify response format
3. **Error Handling Test**: Test with invalid inputs

### Manual Verification
1. **Local Development**:
   - Install dependencies: `pip install -r requirements.txt`
   - Ensure Ollama is running locally
   - Start API: `python chatbot.py`
   - Test with curl or Postman

2. **Docker Build**:
   - Build image: `docker-compose build`
   - Start services: `docker-compose up`
   - Verify both containers are running
   - Test API endpoint through container

3. **Ollama Integration**:
   - Verify model is downloaded in Ollama
   - Test chat functionality end-to-end
   - Check response quality and latency

4. **Container Health**:
   - Check logs: `docker-compose logs`
   - Verify network connectivity between services
   - Test container restart behavior
