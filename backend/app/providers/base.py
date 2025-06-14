from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator
from app.models import Message, ModelInfo


class BaseProvider(ABC):
    """Base class for LLM providers"""
    
    def __init__(self, base_url: str, **kwargs):
        self.base_url = base_url
        self.config = kwargs
    
    @abstractmethod
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
        """Send chat completion request"""
        pass
    
    @abstractmethod
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
        """Stream chat completion response"""
        pass
    
    @abstractmethod
    async def list_models(self) -> List[ModelInfo]:
        """List available models"""
        pass
    
    @abstractmethod
    async def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Get information about a specific model"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is healthy and accessible"""
        pass
    
    def format_messages(self, messages: List[Message]) -> List[Dict[str, str]]:
        """Format messages for the provider's API"""
        return [{"role": msg.role.value, "content": msg.content} for msg in messages]