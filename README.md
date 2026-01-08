# Chatbot API Service

A modular Python chatbot service that provides a unified REST API for interacting with multiple LLM providers including Ollama (local), OpenAI GPT, and Anthropic Claude. Built with FastAPI and fully containerized with Docker.

## Features

- 🔄 **Modular Provider Architecture** - Easily switch between Ollama, OpenAI, and Anthropic
- 🚀 **FastAPI** - High-performance async API with automatic documentation
- 🐳 **Docker Support** - Fully containerized with Docker Compose
- 🔒 **Production Ready** - Security best practices, health checks, and logging
- 📝 **Well Documented** - Comprehensive API docs and Gherkin specifications
- 🎯 **Type Safe** - Pydantic models for request/response validation

## Quick Start

### Prerequisites

- **Docker & Docker Compose** (recommended) OR
- **Python 3.11+** for local development
- **Ollama** (for local LLM) - [Install Ollama](https://ollama.ai)

### Option 1: Docker (Recommended)

1. **Clone and navigate to the project**:
   ```bash
   cd chatbot-project
   ```

2. **Start the services**:
   ```bash
   docker-compose up -d
   ```

3. **Download the llama3 model** (first time only):
   ```bash
   docker exec -it ollama ollama pull llama3
   ```

4. **Test the API**:
   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello, how are you?", "provider": "ollama"}'
   ```

### Option 2: Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install and start Ollama** (if not already running):
   - Download from [ollama.ai](https://ollama.ai)
   - Pull llama3 model: `ollama pull llama3`

3. **Start the API server**:
   ```bash
   python chatbot.py
   ```

4. **Test the API**:
   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello, how are you?"}'
   ```

## API Documentation

### Interactive Docs

Once the service is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints

#### `POST /chat`

Send a message to the chatbot.

**Request Body**:
```json
{
  "message": "What is the capital of France?",
  "provider": "ollama",
  "model": "llama3",
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 500
  }
}
```

**Response**:
```json
{
  "response": "The capital of France is Paris.",
  "provider": "ollama",
  "model": "llama3"
}
```

**Fields**:
- `message` (required): Your message to the chatbot
- `provider` (optional): Provider to use (`ollama`, `openai`, `anthropic`). Default: `ollama`
- `model` (optional): Model name. Default: provider-specific default
- `parameters` (optional): Additional provider-specific parameters

#### `GET /health`

Check service and provider health.

**Response**:
```json
{
  "status": "healthy",
  "providers": {
    "ollama": true,
    "openai": false,
    "anthropic": false
  }
}
```

#### `GET /`

Get API information.

**Response**:
```json
{
  "name": "Chatbot API",
  "version": "1.0.0",
  "endpoints": {
    "/chat": "POST - Send a message to the chatbot",
    "/health": "GET - Check service health",
    "/docs": "GET - Interactive API documentation"
  }
}
```

## Provider Configuration

### Ollama (Default)

Ollama is configured by default and runs locally.

**Environment Variables**:
```bash
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama3
```

**Available Models**:
```bash
# List available models
ollama list

# Pull a new model
ollama pull mistral
ollama pull codellama
ollama pull phi3
```

**Usage Example**:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain quantum computing",
    "provider": "ollama",
    "model": "llama3"
  }'
```

### OpenAI GPT (Optional)

To use OpenAI models, install the package and configure your API key.

**Setup**:
```bash
# Install OpenAI package
pip install openai==1.57.4

# Set API key (in .env file or environment)
export OPENAI_API_KEY=your_api_key_here
```

**Usage Example**:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Write a haiku about coding",
    "provider": "openai",
    "model": "gpt-4"
  }'
```

### Anthropic Claude (Optional)

To use Claude models, install the package and configure your API key.

**Setup**:
```bash
# Install Anthropic package
pip install anthropic==0.42.0

# Set API key (in .env file or environment)
export ANTHROPIC_API_KEY=your_api_key_here
```

**Usage Example**:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain the theory of relativity",
    "provider": "anthropic",
    "model": "claude-3-5-sonnet-20241022"
  }'
```

## Environment Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama3

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# OpenAI Configuration (optional)
OPENAI_API_KEY=sk-...

# Anthropic Configuration (optional)
ANTHROPIC_API_KEY=sk-ant-...
```

## Docker Commands

### Start Services
```bash
docker-compose up -d
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f chatbot
docker-compose logs -f ollama
```

### Stop Services
```bash
docker-compose down
```

### Rebuild After Code Changes
```bash
docker-compose up -d --build
```

### Execute Commands in Container
```bash
# Pull a model in Ollama
docker exec -it ollama ollama pull llama3

# Check Ollama models
docker exec -it ollama ollama list

# Access chatbot container shell
docker exec -it chatbot-api sh
```

## Architecture

### Project Structure
```
chatbot-project/
├── chatbot.py              # Main FastAPI application
├── providers/              # LLM provider implementations
│   ├── __init__.py        # Provider factory
│   ├── base.py            # Abstract base class
│   ├── ollama_provider.py # Ollama implementation
│   ├── openai_provider.py # OpenAI implementation
│   └── anthropic_provider.py # Anthropic implementation
├── specs/                  # Gherkin specifications
│   └── chatbot.feature    # BDD feature specs
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container definition
├── docker-compose.yml     # Multi-container orchestration
├── .env.example          # Environment template
├── .dockerignore         # Docker build exclusions
└── README.md             # This file
```

### Provider Pattern

The service uses a factory pattern to support multiple LLM providers:

```python
from providers import ProviderFactory

# Get a provider instance
provider = ProviderFactory.get_provider("ollama")

# Send a chat message
response = await provider.chat(
    message="Hello",
    model="llama3"
)

# Check provider health
is_available = await provider.is_available()
```

### Adding a New Provider

1. Create a new provider class in `providers/`:
   ```python
   from providers.base import BaseLLMProvider
   
   class MyProvider(BaseLLMProvider):
       async def chat(self, message, model=None, **kwargs):
           # Implementation
           pass
       
       async def is_available(self):
           # Implementation
           pass
       
       def get_default_model(self):
           return "my-default-model"
   ```

2. Register in `providers/__init__.py`:
   ```python
   from providers.my_provider import MyProvider
   
   _providers = {
       'ollama': OllamaProvider,
       'my_provider': MyProvider,
       # ...
   }
   ```

## Testing

### Manual Testing

**Test Health Endpoint**:
```bash
curl http://localhost:8000/health
```

**Test Chat with Different Providers**:
```bash
# Ollama
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "provider": "ollama"}'

# OpenAI (requires API key)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "provider": "openai", "model": "gpt-3.5-turbo"}'
```

### Automated Testing

The service includes Gherkin specifications in `specs/chatbot.feature` that define expected behavior. You can implement automated tests using tools like:
- **pytest-bdd** - For Python BDD testing
- **behave** - Python BDD framework
- **Cucumber** - Cross-platform BDD

## Troubleshooting

### Ollama Connection Issues

**Problem**: `Ollama chat error: Connection refused`

**Solutions**:
- Ensure Ollama is running: `ollama serve`
- Check Ollama is accessible: `curl http://localhost:11434`
- Verify `OLLAMA_BASE_URL` in environment
- In Docker: Use service name `http://ollama:11434`

### Model Not Found

**Problem**: `model 'llama3' not found`

**Solution**:
```bash
# Local
ollama pull llama3

# Docker
docker exec -it ollama ollama pull llama3
```

### OpenAI API Errors

**Problem**: `OpenAI chat error: Incorrect API key`

**Solution**:
- Verify API key is set correctly
- Check key has sufficient credits
- Ensure key has proper permissions

### Container Won't Start

**Problem**: Container exits immediately

**Solutions**:
```bash
# Check logs
docker-compose logs chatbot

# Rebuild containers
docker-compose down
docker-compose up -d --build

# Check for port conflicts
netstat -an | findstr "8000"
```

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'providers'`

**Solution**:
- Ensure you're running from project root
- Check all `__init__.py` files exist
- Verify Python path includes project directory

## Performance Considerations

- **Ollama**: Fast local inference, no API costs, requires local resources
- **OpenAI**: Cloud-based, fast, usage-based pricing
- **Anthropic**: Cloud-based, context-aware, usage-based pricing

### Resource Usage

**Ollama** (local):
- CPU: Varies by model (2-8 cores recommended)
- RAM: 8-16GB minimum
- GPU: Optional but significantly faster (NVIDIA CUDA)

**API Providers**:
- Minimal local resources
- Network latency depends on location

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for sensitive data
3. **Enable CORS** selectively in production
4. **Use HTTPS** in production deployments
5. **Rate limit** API endpoints
6. **Monitor usage** and set billing alerts

## Production Deployment

### Recommendations

1. **Use HTTPS** with proper SSL certificates
2. **Add authentication** (API keys, OAuth, etc.)
3. **Implement rate limiting** (e.g., with slowapi)
4. **Set up monitoring** (logging, metrics, alerts)
5. **Use a reverse proxy** (nginx, Traefik)
6. **Enable auto-scaling** based on load
7. **Configure CORS** for specific origins only

### Example Production Changes

```python
# In chatbot.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues, questions, or contributions, please open an issue on the project repository.
