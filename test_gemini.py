"""
Quick test script to verify Gemini provider integration
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from providers import ProviderFactory

async def test_gemini():
    print("Testing Gemini Provider Integration")
    print("=" * 50)
    
    # Check if API key is set
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        return
    else:
        print(f"✓ GEMINI_API_KEY found: {api_key[:10]}...")
    
    # Check if Gemini is available in providers
    available_providers = ProviderFactory.get_available_providers()
    print(f"\n✓ Available providers: {', '.join(available_providers)}")
    
    if 'gemini' not in available_providers:
        print("❌ Gemini provider not registered")
        return
    else:
        print("✓ Gemini provider is registered")
    
    # Try to get the provider instance
    try:
        provider = ProviderFactory.get_provider('gemini')
        print(f"✓ Gemini provider instance created")
        print(f"✓ Default model: {provider.get_default_model()}")
    except Exception as e:
        print(f"❌ Failed to create Gemini provider: {e}")
        return
    
    # Check provider health
    try:
        is_healthy = await ProviderFactory.check_provider_health('gemini')
        if is_healthy:
            print("✓ Gemini provider is healthy")
        else:
            print("❌ Gemini provider health check failed")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test chat functionality
    print("\n" + "=" * 50)
    print("Testing chat functionality...")
    print("=" * 50)
    
    try:
        response = await provider.chat("Say 'Hello from Gemini!' in one sentence.")
        print(f"✓ Chat response: {response}")
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test streaming functionality
    print("\n" + "=" * 50)
    print("Testing streaming functionality...")
    print("=" * 50)
    
    try:
        print("✓ Stream response:", flush=True)
        chunk_count = 0
        full_response = ""
        async for chunk in provider.chat_stream("Write a short story about a robot learning to paint. Make it 5-6 sentences long."):
            chunk_count += 1
            full_response += chunk
            print(f"\n  [Chunk {chunk_count}]: {chunk}", flush=True)
        
        print(f"\n✓ Streaming completed - received {chunk_count} chunk(s)")
        print(f"✓ Full response: {full_response}")
    except Exception as e:
        print(f"\n❌ Streaming test failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 50)
    print("All tests passed! ✓")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_gemini())
