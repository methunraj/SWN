import httpx
import json
import asyncio

async def test_streaming():
    url = 'http://localhost:8000/api/chat/stream'
    data = {
        'messages': [{'role': 'user', 'content': 'Hello, say hi back'}],
        'stream': True,
        'provider': 'llamacpp',
        'model': 'qwen/qwen3-4b',
        'temperature': 0.7,
        'max_tokens': 100,
        'top_p': 0.9,
        'top_k': 40
    }
    
    async with httpx.AsyncClient() as client:
        async with client.stream('POST', url, json=data, timeout=30) as response:
            print(f'Status: {response.status_code}')
            print(f'Headers: {dict(response.headers)}')
            
            if response.status_code == 200:
                async for line in response.aiter_lines():
                    print(f'Received: {line}')
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str == '[DONE]':
                            print('Stream complete')
                            break
                        try:
                            data = json.loads(data_str)
                            if 'error' in data:
                                print(f'Error in stream: {data["error"]}')
                                break
                            elif 'content' in data:
                                print(f'Content chunk: {data["content"]}', end='', flush=True)
                        except json.JSONDecodeError as e:
                            print(f'JSON decode error: {e}')
            else:
                content = await response.aread()
                print(f'Error response: {content}')

if __name__ == '__main__':
    asyncio.run(test_streaming())