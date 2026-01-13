"""
Test script to verify RAG integration with the chatbot.

This script tests:
1. Chat endpoint with RAG enabled
2. Chat endpoint with RAG disabled
3. Streaming endpoint with RAG enabled
"""
import requests
import json
import sys

CHATBOT_URL = "http://localhost:8000"


def test_chat_with_rag():
    """Test the /chat endpoint with RAG enabled."""
    print("\n" + "="*60)
    print("TEST 1: Chat with RAG enabled")
    print("="*60)
    
    try:
        response = requests.post(
            f"{CHATBOT_URL}/chat",
            json={
                "message": "What is machine learning?",
                "use_rag": True
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Provider: {data['provider']}")
            print(f"✓ Model: {data['model']}")
            print(f"✓ Response length: {len(data['response'])} chars")
            print(f"\nResponse preview:\n{data['response'][:200]}...")
            return True
        else:
            print(f"✗ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_chat_without_rag():
    """Test the /chat endpoint with RAG disabled."""
    print("\n" + "="*60)
    print("TEST 2: Chat with RAG disabled")
    print("="*60)
    
    try:
        response = requests.post(
            f"{CHATBOT_URL}/chat",
            json={
                "message": "What is machine learning?",
                "use_rag": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Provider: {data['provider']}")
            print(f"✓ Model: {data['model']}")
            print(f"✓ Response length: {len(data['response'])} chars")
            print(f"\nResponse preview:\n{data['response'][:200]}...")
            return True
        else:
            print(f"✗ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_stream_with_rag():
    """Test the /chat/stream endpoint with RAG enabled."""
    print("\n" + "="*60)
    print("TEST 3: Streaming chat with RAG enabled")
    print("="*60)
    
    try:
        response = requests.post(
            f"{CHATBOT_URL}/chat/stream",
            json={
                "message": "Tell me about artificial intelligence",
                "use_rag": True
            },
            stream=True,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Streaming response (first 10 chunks):\n")
            
            chunk_count = 0
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = json.loads(line[6:])
                        if 'token' in data:
                            print(data['token'], end='', flush=True)
                            chunk_count += 1
                            if chunk_count >= 50:  # Limit output
                                print("\n... (truncated)")
                                break
            
            print(f"\n\n✓ Received {chunk_count} chunks")
            return True
        else:
            print(f"✗ Failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def check_services():
    """Check if required services are running."""
    print("\n" + "="*60)
    print("Checking service availability...")
    print("="*60)
    
    # Check chatbot service
    try:
        response = requests.get(f"{CHATBOT_URL}/health", timeout=5)
        print(f"✓ Chatbot service is running (status: {response.status_code})")
    except:
        print(f"✗ Chatbot service is NOT running at {CHATBOT_URL}")
        print("  Please start the chatbot with: python chatbot.py")
        return False
    
    # Check RAG service
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        print(f"✓ RAG service is running (status: {response.status_code})")
    except:
        print(f"⚠ RAG service is NOT running at http://localhost:8001")
        print("  RAG features will gracefully fall back to non-RAG mode")
        print("  To enable RAG, start the ingestion service")
    
    return True


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("RAG INTEGRATION VERIFICATION")
    print("="*60)
    
    # Check services
    if not check_services():
        sys.exit(1)
    
    # Run tests
    results = []
    results.append(("Chat with RAG", test_chat_with_rag()))
    results.append(("Chat without RAG", test_chat_without_rag()))
    results.append(("Streaming with RAG", test_stream_with_rag()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")
    
    if total_passed == len(results):
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
