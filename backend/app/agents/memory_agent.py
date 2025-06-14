from typing import List, Dict, Any, Optional
import json
from collections import deque
from app.models import Message, Role
from .base import ConversationAgent


class MemoryAgent(ConversationAgent):
    """Agent responsible for managing conversation memory and context"""
    
    def __init__(self, name: str = "MemoryAgent", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.conversations = {}
        self.max_memory_size = config.get("max_memory_size", 100) if config else 100
        self.summarization_threshold = config.get("summarization_threshold", 0.8) if config else 0.8
    
    async def initialize(self) -> None:
        """Initialize memory agent"""
        # Could load persistent conversations from database here
        pass
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        # Could save conversations to database here
        pass
    
    async def process(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """Process memory-related operations"""
        if isinstance(input_data, list) and all(isinstance(m, Message) for m in input_data):
            return await self.manage_context(input_data, context.get("max_tokens", 4096))
        return input_data
    
    async def process_messages(
        self, 
        messages: List[Message], 
        context: Optional[Dict[str, Any]] = None
    ) -> List[Message]:
        """Process messages for memory management"""
        return await self.manage_context(messages, context.get("max_tokens", 4096))
    
    async def manage_context(
        self, 
        messages: List[Message], 
        max_tokens: int = 4096
    ) -> List[Message]:
        """Manage conversation context to fit within token limits"""
        
        # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
        total_tokens = sum(len(msg.content) // 4 for msg in messages)
        
        if total_tokens <= max_tokens:
            return messages
        
        # Keep system message and recent messages
        system_messages = [msg for msg in messages if msg.role == Role.SYSTEM]
        other_messages = [msg for msg in messages if msg.role != Role.SYSTEM]
        
        # Calculate how many recent messages we can keep
        system_tokens = sum(len(msg.content) // 4 for msg in system_messages)
        available_tokens = max_tokens - system_tokens
        
        # Keep messages from the end until we hit the limit
        kept_messages = []
        current_tokens = 0
        
        for msg in reversed(other_messages):
            msg_tokens = len(msg.content) // 4
            if current_tokens + msg_tokens <= available_tokens * self.summarization_threshold:
                kept_messages.insert(0, msg)
                current_tokens += msg_tokens
            else:
                break
        
        # If we had to truncate, add a summary message
        if len(kept_messages) < len(other_messages):
            summary = await self._create_summary(
                other_messages[:len(other_messages) - len(kept_messages)]
            )
            if summary:
                kept_messages.insert(0, summary)
        
        return system_messages + kept_messages
    
    async def _create_summary(self, messages: List[Message]) -> Optional[Message]:
        """Create a summary of truncated messages"""
        
        # Simple summary implementation
        num_messages = len(messages)
        user_messages = len([m for m in messages if m.role == Role.USER])
        assistant_messages = len([m for m in messages if m.role == Role.ASSISTANT])
        
        summary_content = (
            f"[Previous conversation summary: {num_messages} messages "
            f"({user_messages} user, {assistant_messages} assistant) were exchanged. "
            f"The conversation covered various topics that have been truncated to fit context limits.]"
        )
        
        return Message(
            role=Role.SYSTEM,
            content=summary_content
        )
    
    async def store_conversation(
        self, 
        conversation_id: str, 
        messages: List[Message]
    ) -> None:
        """Store conversation in memory"""
        
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = deque(maxlen=self.max_memory_size)
        
        # Store messages
        for message in messages:
            if message not in self.conversations[conversation_id]:
                self.conversations[conversation_id].append(message)
    
    async def get_conversation(
        self, 
        conversation_id: str
    ) -> Optional[List[Message]]:
        """Retrieve conversation from memory"""
        
        if conversation_id in self.conversations:
            return list(self.conversations[conversation_id])
        return None
    
    async def clear_conversation(self, conversation_id: str) -> None:
        """Clear a specific conversation from memory"""
        
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
    
    async def get_conversation_summary(
        self, 
        conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get summary statistics for a conversation"""
        
        if conversation_id not in self.conversations:
            return None
        
        messages = self.conversations[conversation_id]
        
        return {
            "conversation_id": conversation_id,
            "total_messages": len(messages),
            "user_messages": len([m for m in messages if m.role == Role.USER]),
            "assistant_messages": len([m for m in messages if m.role == Role.ASSISTANT]),
            "system_messages": len([m for m in messages if m.role == Role.SYSTEM]),
            "estimated_tokens": sum(len(m.content) // 4 for m in messages)
        }
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage statistics"""
        
        total_conversations = len(self.conversations)
        total_messages = sum(len(msgs) for msgs in self.conversations.values())
        
        return {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "max_memory_size": self.max_memory_size,
            "conversations": {
                conv_id: len(msgs) 
                for conv_id, msgs in self.conversations.items()
            }
        }