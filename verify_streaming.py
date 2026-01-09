import asyncio
import aiohttp
import json
import time

async def verify_streaming():
    url = "http://localhost:8000/chat/stream"
    payload = {
        "message": "Write a short poem about coding.",
        "provider": "ollama",
        "model": "llama3"
    }

    print(f"Connecting to {url}...")
    start_time = time.time()
    first_chunk_time = None
    chunks = []
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload) as response:
                print(f"Status: {response.status}")
                if response.status != 200:
                    text = await response.text()
                    print(f"Error response: {text}")
                    return

                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if not line or not line.startswith("data: "):
                        continue
                    
                    current_time = time.time()
                    if first_chunk_time is None:
                        first_chunk_time = current_time
                        print(f"First chunk received after {first_chunk_time - start_time:.4f}s")
                    
                    data_str = line[6:]  # Remove "data: "
                    try:
                        data = json.loads(data_str)
                        if "token" in data:
                            token = data["token"]
                            print(f"{current_time - start_time:.4f}s: {token}")
                            chunks.append((current_time, token))
                    except json.JSONDecodeError:
                        print(f"Failed to decode: {data_str}")

        except Exception as e:
            print(f"Connection error: {e}")
            return

    if not chunks:
        print("No chunks received.")
        return

    # Analyze timing
    times = [c[0] for c in chunks]
    if len(times) > 1:
        total_duration = times[-1] - times[0]
        avg_gap = total_duration / (len(times) - 1)
        print(f"\nTotal tokens: {len(chunks)}")
        print(f"Stream duration (first to last): {total_duration:.4f}s")
        print(f"Average time between tokens: {avg_gap:.4f}s")
        
        if total_duration < 0.1 and len(chunks) > 5:
            print("\nWARNING: Tokens arrived very quickly. It might still be buffered!")
        else:
            print("\nSUCCESS: Tokens arrived sequentially over time.")
    else:
        print("Only received one chunk.")

if __name__ == "__main__":
    # Check if aiohttp is installed
    try:
        import aiohttp
        asyncio.run(verify_streaming())
    except ImportError:
        print("aiohttp not installed to run this script. Please install it or rely on manual verification methods.")
