#!/usr/bin/env python3

import asyncio
import sys
sys.path.append('.')

from app.config import settings
from app.agents import ChatAgent
from app.models import Message, Role, Provider


async def quick_test():
    """Quick test of the backend components"""
    
    print("🚀 Quick Backend Test")
    print("=" * 50)
    
    # Create and initialize chat agent
    print("\n1️⃣ Initializing Chat Agent...")
    chat_agent = ChatAgent()
    await chat_agent.initialize()
    print("✅ Chat Agent initialized")
    
    # Check provider status
    print("\n2️⃣ Checking Providers...")
    providers_status = await chat_agent.check_providers_status()
    for status in providers_status:
        icon = "✅" if status["available"] else "❌"
        print(f"{icon} {status['provider']}: {status.get('base_url', 'N/A')}")
    
    # List models
    print("\n3️⃣ Listing Models...")
    try:
        models = await chat_agent.list_models()
        print(f"Found {len(models)} models:")
        for model in models:
            print(f"  - {model['name']} ({model['provider']})")
    except Exception as e:
        print(f"❌ Error listing models: {e}")
    
    # Test chat with llama.cpp
    print("\n4️⃣ Testing Chat with llama.cpp...")
    try:
        messages = [
            Message(role=Role.USER, content="What is 2+2? Reply with just the number.")
        ]
        
        context = {
            "provider": Provider.LLAMACPP,
            "model": "qwen/qwen3-4b",
            "temperature": 0.1,
            "max_tokens": 10
        }
        
        result = await chat_agent.process_messages(messages, context)
        print(f"Response: {result['message'].content}")
        print(f"Provider: {result['provider']}")
        print(f"Model: {result['model']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test streaming
    print("\n5️⃣ Testing Streaming...")
    try:
        messages = [
            Message(role=Role.USER, content="Count from 1 to 3")
        ]
        
        context = {
            "provider": Provider.LLAMACPP,
            "model": "qwen/qwen3-4b",
            "stream": True,
            "max_tokens": 50
        }
        
        result = await chat_agent.process_messages(messages, context)
        print("Streaming: ", end="", flush=True)
        
        chunk_count = 0
        async for chunk in result["stream"]:
            print(chunk, end="", flush=True)
            chunk_count += 1
        
        print(f"\n✅ Received {chunk_count} chunks")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Cleanup
    print("\n6️⃣ Cleaning up...")
    await chat_agent.cleanup()
    print("✅ Cleanup complete")


if __name__ == "__main__":
    asyncio.run(quick_test())