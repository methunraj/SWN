import httpx
from typing import List, Dict, Any, Optional, AsyncGenerator
import json
from app.models import Message, ModelInfo, Provider
from .base import BaseProvider


class OllamaProvider(BaseProvider):
    """Ollama provider implementation"""
    
    def __init__(self, base_url: str = "http://localhost:11434", **kwargs):
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
        """Send chat completion request to Ollama"""
        
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": model,
            "messages": self.format_messages(messages),
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
            }
        }
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
            
        response = await self.client.post(url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return {
            "content": result["message"]["content"],
            "model": model,
            "usage": {
                "prompt_tokens": result.get("prompt_eval_count", 0),
                "completion_tokens": result.get("eval_count", 0),
                "total_tokens": result.get("prompt_eval_count", 0) + result.get("eval_count", 0)
            }
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
        """Stream chat completion response from Ollama"""
        
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": model,
            "messages": self.format_messages(messages),
            "stream": True,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
            }
        }
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
            
        async with self.client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    chunk = json.loads(line)
                    if "message" in chunk and "content" in chunk["message"]:
                        yield chunk["message"]["content"]
    
    async def list_models(self) -> List[ModelInfo]:
        """List available models in Ollama"""
        
        url = f"{self.base_url}/api/tags"
        response = await self.client.get(url)
        response.raise_for_status()
        
        models_data = response.json()
        models = []
        
        for model in models_data.get("models", []):
            models.append(ModelInfo(
                name=model["name"],
                provider=Provider.OLLAMA,
                size=model.get("size"),
                parameters={
                    "family": model.get("details", {}).get("family"),
                    "parameter_size": model.get("details", {}).get("parameter_size"),
                    "quantization_level": model.get("details", {}).get("quantization_level")
                }
            ))
        
        return models
    
    async def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Get information about a specific model"""
        
        url = f"{self.base_url}/api/show"
        response = await self.client.post(url, json={"name": model_name})
        
        if response.status_code == 404:
            return None
            
        response.raise_for_status()
        model_data = response.json()
        
        return ModelInfo(
            name=model_name,
            provider=Provider.OLLAMA,
            parameters=model_data.get("parameters", {}),
            context_length=model_data.get("parameters", {}).get("num_ctx")
        )
    
    async def health_check(self) -> bool:
        """Check if Ollama is running and accessible"""
        
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception:
            return False
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()