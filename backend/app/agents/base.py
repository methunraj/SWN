from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from app.models import Message


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
    
    @abstractmethod
    async def process(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """Process input data and return result"""
        pass
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the agent"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup resources"""
        pass


class ConversationAgent(BaseAgent):
    """Base class for conversation-based agents"""
    
    @abstractmethod
    async def process_messages(
        self, 
        messages: List[Message], 
        context: Optional[Dict[str, Any]] = None
    ) -> List[Message]:
        """Process conversation messages"""
        pass