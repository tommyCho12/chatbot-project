# RAG Integration Guide

## Overview

This guide shows how to integrate the RAG Ingestion Service with your chatbot to provide context-aware responses.

## Integration Pattern

```
1. User asks question
2. Chatbot calls /search endpoint with the question
3. Retrieves relevant document chunks
4. Passes chunks as context to LLM
5. LLM generates response with context
```

## Python Integration Example

### Option 1: Simple Integration (Recommended)

```python
import requests

INGESTION_SERVICE_URL = "http://localhost:8001"

def get_relevant_context(user_query: str, top_k: int = 3) -> str:
    """
    Retrieve relevant document chunks for a user query.
    
    Args:
        user_query: The user's question
        top_k: Number of relevant chunks to retrieve
        
    Returns:
        Formatted context string to pass to LLM
    """
    # Search for relevant chunks
    response = requests.post(
        f"{INGESTION_SERVICE_URL}/search",
        json={
            "query": user_query,
            "top_k": top_k
        }
    )
    
    if response.status_code != 200:
        return ""
    
    data = response.json()
    
    # Format chunks as context
    if not data['results']:
        return ""
    
    context_parts = []
    for i, result in enumerate(data['results'], 1):
        # Extract relevant info
        text = result['text']
        doc_id = result['metadata'].get('document_id', 'unknown')
        title = result['metadata'].get('title', 'Untitled')
        
        context_parts.append(f"[Source {i}: {title}]\n{text}\n")
    
    return "\n---\n".join(context_parts)


def chatbot_with_rag(user_query: str) -> str:
    """
    Process user query with RAG.
    """
    # 1. Get relevant context
    context = get_relevant_context(user_query, top_k=3)
    
    # 2. Build prompt with context
    if context:
        system_prompt = f"""You are a helpful assistant. Answer the user's question based on the following context.
If the context doesn't contain relevant information, say so.

Context:
{context}
"""
    else:
        system_prompt = "You are a helpful assistant."
    
    # 3. Call your LLM (Ollama, OpenAI, etc.)
    # Example with Ollama:
    llm_response = requests.post(
        "http://localhost:8080/chat",  # Your chatbot service
        json={
            "message": user_query,
            "system": system_prompt
        }
    )
    
    return llm_response.json()['response']
```

### Option 2: Advanced Integration with Caching

```python
import requests
from functools import lru_cache
from typing import List, Dict, Any

class RAGClient:
    """Client for RAG Ingestion Service."""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for relevant chunks."""
        response = requests.post(
            f"{self.base_url}/search",
            json={"query": query, "top_k": top_k}
        )
        response.raise_for_status()
        return response.json()['results']
    
    def format_context(self, results: List[Dict[str, Any]], 
                      include_metadata: bool = True) -> str:
        """Format search results as context for LLM."""
        if not results:
            return ""
        
        context_parts = []
        for i, result in enumerate(results, 1):
            text = result['text']
            
            if include_metadata:
                metadata = result['metadata']
                header = f"[Document: {metadata.get('title', 'Unknown')}]"
                context_parts.append(f"{header}\n{text}")
            else:
                context_parts.append(text)
        
        return "\n\n".join(context_parts)
    
    def get_context_for_query(self, query: str, top_k: int = 3) -> str:
        """One-step: search and format context."""
        results = self.search(query, top_k)
        return self.format_context(results)


# Usage in your chatbot
rag_client = RAGClient()

def handle_user_message(user_query: str) -> str:
    # Get relevant context
    context = rag_client.get_context_for_query(user_query, top_k=3)
    
    # Build prompt
    prompt = f"""Context information:
{context}

User question: {user_query}

Answer the question based on the context above. If the context doesn't help, say so."""
    
    # Send to your LLM
    return call_your_llm(prompt)
```

## Response Format

The `/search` endpoint returns:

```json
{
  "query": "machine learning",
  "count": 3,
  "results": [
    {
      "chunk_id": "doc123_0_abc123",
      "text": "Machine learning is a subset of AI...",
      "metadata": {
        "document_id": "doc123",
        "title": "ML Guide",
        "category": "education",
        "chunk_index": 0,
        "total_chunks": 5,
        "embedding_version": "v1"
      },
      "distance": 0.234  // Lower = more relevant
    }
  ]
}
```

## Best Practices

### 1. Set Appropriate `top_k`

```python
# For general questions: 3-5 chunks
context = rag_client.get_context_for_query(query, top_k=3)

# For complex questions: 5-10 chunks
context = rag_client.get_context_for_query(query, top_k=7)
```

### 2. Filter by Metadata (if needed)

If you want to search only specific document types, you'll need to filter results:

```python
def get_context_filtered(query: str, category: str = None) -> str:
    results = rag_client.search(query, top_k=10)
    
    # Filter by category
    if category:
        results = [r for r in results 
                  if r['metadata'].get('category') == category]
    
    return rag_client.format_context(results[:3])
```

### 3. Handle No Results

```python
def chatbot_with_fallback(user_query: str) -> str:
    context = rag_client.get_context_for_query(user_query, top_k=3)
    
    if not context:
        # No relevant docs found - use general LLM knowledge
        return call_llm_without_context(user_query)
    
    # Use RAG response
    return call_llm_with_context(user_query, context)
```

## Docker Networking

If both services are in Docker:

### Option 1: Same docker-compose.yml

Add your chatbot to the ingestion service's `docker-compose.yml`:

```yaml
services:
  ingestion-api:
    # ... existing config
  
  chatbot:
    image: your-chatbot-image
    environment:
      - RAG_SERVICE_URL=http://ingestion-api:8000  # Internal Docker network
```

### Option 2: Separate Compose Files

Create a shared network:

```bash
# Create network
docker network create rag-network

# In ingestion_service/docker-compose.yml
networks:
  rag-network:
    external: true

services:
  ingestion-api:
    networks:
      - rag-network

# In your chatbot's docker-compose.yml
networks:
  rag-network:
    external: true

services:
  chatbot:
    networks:
      - rag-network
    environment:
      - RAG_SERVICE_URL=http://ingestion-api:8000
```

## Example: Full Chatbot Integration

```python
# chatbot_service.py
from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()
RAG_SERVICE = "http://localhost:8001"  # or http://ingestion-api:8000 in Docker

class ChatRequest(BaseModel):
    message: str
    use_rag: bool = True

@app.post("/chat")
async def chat(request: ChatRequest):
    user_message = request.message
    
    # Step 1: Get relevant context from RAG service
    if request.use_rag:
        try:
            rag_response = requests.post(
                f"{RAG_SERVICE}/search",
                json={"query": user_message, "top_k": 3},
                timeout=5
            )
            
            if rag_response.status_code == 200:
                results = rag_response.json()['results']
                context = "\n\n".join([r['text'] for r in results])
            else:
                context = ""
        except Exception as e:
            print(f"RAG service error: {e}")
            context = ""
    else:
        context = ""
    
    # Step 2: Build prompt
    if context:
        full_prompt = f"""Context:
{context}

Question: {user_message}

Answer based on the context above."""
    else:
        full_prompt = user_message
    
    # Step 3: Call your LLM (Ollama example)
    llm_response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama2",
            "prompt": full_prompt
        }
    )
    
    return {"response": llm_response.json()['response']}
```

## Monitoring

Check if RAG service is available:

```python
def check_rag_health():
    try:
        response = requests.get(f"{RAG_SERVICE}/health", timeout=2)
        return response.status_code == 200
    except:
        return False
```

## Next Steps

1. **Ingest your documents** via `/documents/ingest`
2. **Test search** with sample queries
3. **Integrate** the search into your chatbot's prompt building
4. **Tune** the `top_k` parameter for your use case
5. **Monitor** relevance and adjust chunking if needed
