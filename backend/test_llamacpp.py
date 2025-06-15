import asyncio
import httpx
import json
from datetime import datetime


async def test_llamacpp_server():
    """Test all llama.cpp server endpoints"""
    
    base_url = "http://127.0.0.1:1234"
    results = {}
    
    print(f"\n🔧 Testing llama.cpp server at {base_url}")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test 1: Check /v1/models endpoint
        print("\n1️⃣ Testing GET /v1/models...")
        try:
            response = await client.get(f"{base_url}/v1/models")
            results['models'] = {
                'status': response.status_code,
                'success': response.status_code == 200,
                'data': response.json() if response.status_code == 200 else None
            }
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            results['models'] = {'success': False, 'error': str(e)}
            print(f"   ❌ Error: {e}")
        
        # Test 2: Chat Completions
        print("\n2️⃣ Testing POST /v1/chat/completions...")
        chat_payload = {
            "model": "qwen/qwen3-4b",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello! Can you tell me a very short joke?"}
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        try:
            response = await client.post(
                f"{base_url}/v1/chat/completions",
                json=chat_payload
            )
            results['chat'] = {
                'status': response.status_code,
                'success': response.status_code == 200,
                'data': response.json() if response.status_code == 200 else None
            }
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and data['choices']:
                    content = data['choices'][0]['message']['content']
                    print(f"   Response: {content}")
                    print(f"   Usage: {data.get('usage', 'N/A')}")
        except Exception as e:
            results['chat'] = {'success': False, 'error': str(e)}
            print(f"   ❌ Error: {e}")
        
        # Test 3: Streaming Chat Completions
        print("\n3️⃣ Testing POST /v1/chat/completions (streaming)...")
        stream_payload = {
            "model": "qwen/qwen3-4b",
            "messages": [
                {"role": "user", "content": "Count from 1 to 5"}
            ],
            "temperature": 0.7,
            "max_tokens": 50,
            "stream": True
        }
        
        try:
            chunks_received = 0
            full_response = ""
            
            async with client.stream(
                "POST",
                f"{base_url}/v1/chat/completions",
                json=stream_payload
            ) as response:
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    print("   Streaming response: ", end="", flush=True)
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            if line == "data: [DONE]":
                                break
                            try:
                                chunk = json.loads(line[6:])
                                if 'choices' in chunk and chunk['choices']:
                                    delta = chunk['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        content = delta['content']
                                        print(content, end="", flush=True)
                                        full_response += content
                                        chunks_received += 1
                            except json.JSONDecodeError:
                                pass
                    print()  # New line after streaming
                    
            results['stream'] = {
                'success': True,
                'chunks_received': chunks_received,
                'response_length': len(full_response)
            }
            print(f"   ✅ Received {chunks_received} chunks")
            
        except Exception as e:
            results['stream'] = {'success': False, 'error': str(e)}
            print(f"   ❌ Error: {e}")
        
        # Test 4: Completions endpoint
        print("\n4️⃣ Testing POST /v1/completions...")
        completion_payload = {
            "model": "qwen/qwen3-4b",
            "prompt": "The capital of France is",
            "temperature": 0.7,
            "max_tokens": 20
        }
        
        try:
            response = await client.post(
                f"{base_url}/v1/completions",
                json=completion_payload
            )
            results['completions'] = {
                'status': response.status_code,
                'success': response.status_code == 200,
                'data': response.json() if response.status_code == 200 else None
            }
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and data['choices']:
                    text = data['choices'][0]['text']
                    print(f"   Response: {completion_payload['prompt']}{text}")
        except Exception as e:
            results['completions'] = {'success': False, 'error': str(e)}
            print(f"   ❌ Error: {e}")
        
        # Test 5: Embeddings endpoint
        print("\n5️⃣ Testing POST /v1/embeddings...")
        embeddings_payload = {
            "model": "qwen/qwen3-4b",
            "input": "Hello world"
        }
        
        try:
            response = await client.post(
                f"{base_url}/v1/embeddings",
                json=embeddings_payload
            )
            results['embeddings'] = {
                'status': response.status_code,
                'success': response.status_code == 200
            }
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data']:
                    embedding_size = len(data['data'][0]['embedding'])
                    print(f"   ✅ Embedding size: {embedding_size}")
                    results['embeddings']['embedding_size'] = embedding_size
        except Exception as e:
            results['embeddings'] = {'success': False, 'error': str(e)}
            print(f"   ❌ Error: {e}")
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r.get('success', False))
    
    for test_name, result in results.items():
        status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
        print(f"{test_name.upper()}: {status}")
        if not result.get('success', False) and 'error' in result:
            print(f"  Error: {result['error']}")
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    return results


async def test_backend_integration():
    """Test the FastAPI backend with llama.cpp provider"""
    
    print("\n\n🚀 Testing FastAPI Backend Integration")
    print("=" * 60)
    
    # First, update the .env file to use the correct llama.cpp URL
    print("\n📝 Updating backend configuration...")
    
    env_content = """# Server Configuration
APP_NAME="Swift Neethi Backend"
APP_VERSION="1.0.0"
DEBUG=True
HOST=0.0.0.0
PORT=8000

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Provider Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama2

LLAMACPP_BASE_URL=http://127.0.0.1:1234
LLAMACPP_MODEL_PATH=./models/
LLAMACPP_DEFAULT_MODEL=qwen/qwen3-4b

# Agent Configuration
MAX_CONTEXT_LENGTH=4096
DEFAULT_TEMPERATURE=0.7
DEFAULT_TOP_P=0.9
DEFAULT_TOP_K=40

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database (optional)
DATABASE_URL=sqlite:///./swift_neethi.db

# Redis (optional for caching)
REDIS_URL=redis://localhost:6379

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
"""
    
    with open("/Users/methunraj/Desktop/Swift Neethi/backend/.env", "w") as f:
        f.write(env_content)
    
    print("✅ Configuration updated")
    
    # Now test the backend endpoints
    backend_url = "http://localhost:8000"
    
    print(f"\n🧪 Testing Backend at {backend_url}")
    print("(Make sure the FastAPI backend is running: python main.py)")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test 1: Provider Status
        print("\n1️⃣ Testing Provider Status...")
        try:
            response = await client.get(f"{backend_url}/api/models/providers")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                providers = response.json()
                for provider in providers:
                    status = "✅" if provider['available'] else "❌"
                    print(f"   {status} {provider['provider']}: {provider.get('base_url', 'N/A')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 2: List Models
        print("\n2️⃣ Testing List Models...")
        try:
            response = await client.get(f"{backend_url}/api/models")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                models = response.json()
                print(f"   Found {len(models)} models")
                for model in models:
                    print(f"   - {model['name']} ({model['provider']})")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 3: Chat with llama.cpp
        print("\n3️⃣ Testing Chat with llama.cpp...")
        chat_request = {
            "messages": [
                {"role": "user", "content": "What is 2+2?"}
            ],
            "provider": "llamacpp",
            "model": "qwen/qwen3-4b",
            "temperature": 0.7
        }
        
        try:
            response = await client.post(
                f"{backend_url}/api/chat",
                json=chat_request
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {data['message']['content']}")
                print(f"   Provider: {data['provider']}")
                print(f"   Model: {data['model']}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 4: Streaming Chat
        print("\n4️⃣ Testing Streaming Chat...")
        stream_request = {
            "messages": [
                {"role": "user", "content": "Count from 1 to 3"}
            ],
            "provider": "llamacpp",
            "model": "qwen/qwen3-4b",
            "stream": True
        }
        
        try:
            async with client.stream(
                "POST",
                f"{backend_url}/api/chat/stream",
                json=stream_request
            ) as response:
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    print("   Streaming: ", end="", flush=True)
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            if line == "data: [DONE]":
                                break
                            try:
                                chunk = json.loads(line[6:])
                                if 'content' in chunk:
                                    print(chunk['content'], end="", flush=True)
                            except json.JSONDecodeError:
                                pass
                    print()
        except Exception as e:
            print(f"   ❌ Error: {e}")


async def main():
    """Run all tests"""
    
    print("🧪 Swift Neethi llama.cpp Integration Test Suite")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test llama.cpp server directly
    await test_llamacpp_server()
    
    # Test backend integration
    await test_backend_integration()
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())