"""
RAG Client Module

Provides functionality to retrieve relevant context from the RAG Ingestion Service
for use in chatbot responses.
"""
import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# RAG service configuration
# Use host.docker.internal when chatbot runs in Docker to access host services
# Use localhost when running chatbot directly with Python
INGESTION_SERVICE_URL = "http://host.docker.internal:8001"


def get_relevant_context(user_query: str, top_k: int = 3) -> str:
    """
    Retrieve relevant document chunks for a user query.
    
    Args:
        user_query: The user's question
        top_k: Number of relevant chunks to retrieve
        
    Returns:
        Formatted context string to pass to LLM, or empty string if no results or error
    """
    try:
        # Search for relevant chunks
        response = requests.post(
            f"{INGESTION_SERVICE_URL}/search",
            json={
                "query": user_query,
                "top_k": top_k
            },
            timeout=5  # 5 second timeout
        )
        
        if response.status_code != 200:
            logger.warning(f"RAG service returned status {response.status_code}")
            return ""
        else:
            logger.info(f"RAG service returned status {response.status_code}")

        
        data = response.json()
        
        # Format chunks as context
        if not data.get('results'):
            logger.info("No relevant context found for query")
            return ""
        
        context_parts = []
        for i, result in enumerate(data['results'], 1):
            # Extract relevant info
            text = result.get('text', '')
            metadata = result.get('metadata', {})
            doc_id = metadata.get('document_id', 'unknown')
            title = metadata.get('title', 'Untitled')
            
            context_parts.append(f"[Source {i}: {title}]\n{text}\n")
        
        context = "\n---\n".join(context_parts)
        logger.info(f"Retrieved {len(data['results'])} context chunks for query")
        return context
    
    except requests.exceptions.Timeout:
        logger.warning("RAG service request timed out")
        return ""
    
    except requests.exceptions.ConnectionError:
        logger.warning("Could not connect to RAG service")
        return ""
    
    except Exception as e:
        logger.error(f"Error retrieving context from RAG service: {str(e)}")
        return ""


def check_rag_health() -> bool:
    """
    Check if RAG service is available.
    
    Returns:
        True if RAG service is healthy, False otherwise
    """
    try:
        response = requests.get(f"{INGESTION_SERVICE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False
