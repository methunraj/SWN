import httpx
from typing import List, Dict, Any, Optional, AsyncGenerator
import json
from app.models import Message, ModelInfo, Provider
from .base import BaseProvider


class LlamaCppProvider(BaseProvider):
    """llama.cpp server provider implementation"""
    
    def __init__(self, base_url: str = "http://localhost:8080", **kwargs):
        super().__init__(base_url, **kwargs)
        self.client = httpx.AsyncClient(timeout=120.0)
    
    async def chat(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Send chat completion request to llama.cpp server"""
        
        url = f"{self.base_url}/v1/chat/completions"
        
        payload = {
            "model": model,  # Include model in payload
            "messages": self.format_messages(messages),
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "stream": False
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
            
        response = await self.client.post(url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return {
            "content": result["choices"][0]["message"]["content"],
            "model": model,
            "usage": result.get("usage", {})
        }
    
    async def chat_stream(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion response from llama.cpp server"""
        
        url = f"{self.base_url}/v1/chat/completions"
        
        payload = {
            "model": model,  # Include model in payload
            "messages": self.format_messages(messages),
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "stream": True
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
            
        async with self.client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    if line == "data: [DONE]":
                        break
                    try:
                        chunk = json.loads(line[6:])
                        if "choices" in chunk and chunk["choices"]:
                            delta = chunk["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                    except json.JSONDecodeError:
                        continue
    
    async def list_models(self) -> List[ModelInfo]:
        """List available models from llama.cpp server"""
        
        try:
            # Try the /v1/models endpoint first (your server supports this)
            response = await self.client.get(f"{self.base_url}/v1/models")
            if response.status_code == 200:
                models_data = response.json()
                models = []
                for model in models_data.get("data", []):
                    models.append(ModelInfo(
                        name=model["id"],
                        provider=Provider.LLAMACPP,
                        context_length=4096  # Default context length
                    ))
                return models
        except Exception:
            pass
        
        # Fallback to checking if server is running
        if await self.health_check():
            return [ModelInfo(
                name=self.config.get("default_model", "default"),
                provider=Provider.LLAMACPP,
                context_length=4096
            )]
        
        return []
    
    async def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Get information about the loaded model"""
        
        try:
            response = await self.client.get(f"{self.base_url}/props")
            if response.status_code == 200:
                props = response.json()
                return ModelInfo(
                    name=model_name,
                    provider=Provider.LLAMACPP,
                    context_length=props.get("n_ctx", 2048),
                    parameters=props
                )
        except Exception:
            pass
            
        # Return basic info if props endpoint doesn't exist
        if await self.health_check():
            return ModelInfo(
                name=model_name,
                provider=Provider.LLAMACPP,
                context_length=2048
            )
        
        return None
    
    async def health_check(self) -> bool:
        """Check if llama.cpp server is running and accessible"""
        
        try:
            # Try multiple endpoints to check health
            # First try /health
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                return True
        except Exception:
            pass
        
        try:
            # Try /v1/models as fallback
            response = await self.client.get(f"{self.base_url}/v1/models")
            return response.status_code == 200
        except Exception:
            return False
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()