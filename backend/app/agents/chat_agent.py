from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from app.models import Message, Role, Provider
from app.providers import PROVIDER_MAP
from app.config import settings
from .base import ConversationAgent
from .memory_agent import MemoryAgent
from .system_prompt_agent import SystemPromptAgent


class ChatAgent(ConversationAgent):
    """Main chat agent that orchestrates conversation flow"""
    
    def __init__(self, name: str = "ChatAgent", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.memory_agent = MemoryAgent()
        self.prompt_agent = SystemPromptAgent()
        self.providers = {}
        self.conversations = {}
    
    async def initialize(self) -> None:
        """Initialize the chat agent and its dependencies"""
        await self.memory_agent.initialize()
        await self.prompt_agent.initialize()
        
        # Initialize providers
        if settings.ollama_base_url:
            self.providers[Provider.OLLAMA] = PROVIDER_MAP[Provider.OLLAMA](
                base_url=settings.ollama_base_url
            )
        
        if settings.llamacpp_base_url:
            self.providers[Provider.LLAMACPP] = PROVIDER_MAP[Provider.LLAMACPP](
                base_url=settings.llamacpp_base_url
            )
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        await self.memory_agent.cleanup()
        await self.prompt_agent.cleanup()
        
        for provider in self.providers.values():
            if hasattr(provider, '__aexit__'):
                await provider.__aexit__(None, None, None)
    
    async def process(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """Process chat request"""
        if isinstance(input_data, dict) and "messages" in input_data:
            return await self.process_messages(input_data["messages"], context)
        raise ValueError("Invalid input data for ChatAgent")
    
    async def process_messages(
        self, 
        messages: List[Message], 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process conversation messages"""
        
        context = context or {}
        conversation_id = context.get("conversation_id") or str(uuid.uuid4())
        provider_str = context.get("provider", settings.default_provider)
        
        # Convert string provider to enum
        if isinstance(provider_str, str):
            provider = Provider(provider_str)
        else:
            provider = provider_str
            
        model = context.get("model") or settings.default_model
        system_prompt_id = context.get("system_prompt_id")
        
        # Get or create conversation
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = {
                "id": conversation_id,
                "messages": [],
                "created_at": datetime.utcnow(),
                "metadata": {}
            }
        
        conversation = self.conversations[conversation_id]
        
        # Apply system prompt if needed
        if system_prompt_id:
            system_message = await self.prompt_agent.get_system_message(
                system_prompt_id, 
                context.get("prompt_variables", {})
            )
            if system_message and not self._has_system_message(messages):
                messages = [system_message] + messages
        
        # Manage conversation memory
        messages = await self.memory_agent.manage_context(
            messages,
            max_tokens=context.get("max_context_length", settings.max_context_length)
        )
        
        # Get provider and send request
        if provider not in self.providers:
            raise ValueError(f"Provider {provider} not available")
        
        provider_instance = self.providers[provider]
        
        # Stream or regular chat
        if context.get("stream", False):
            return {
                "stream": provider_instance.chat_stream(
                    messages=messages,
                    model=model,
                    temperature=context.get("temperature", settings.default_temperature),
                    top_p=context.get("top_p", settings.default_top_p),
                    top_k=context.get("top_k", settings.default_top_k),
                    max_tokens=context.get("max_tokens")
                ),
                "conversation_id": conversation_id,
                "provider": provider,
                "model": model
            }
        else:
            response = await provider_instance.chat(
                messages=messages,
                model=model,
                temperature=context.get("temperature", settings.default_temperature),
                top_p=context.get("top_p", settings.default_top_p),
                top_k=context.get("top_k", settings.default_top_k),
                max_tokens=context.get("max_tokens")
            )
            
            # Create assistant message
            assistant_message = Message(
                role=Role.ASSISTANT,
                content=response["content"]
            )
            
            # Update conversation
            conversation["messages"].extend(messages[-1:])  # Add user message
            conversation["messages"].append(assistant_message)
            conversation["updated_at"] = datetime.utcnow()
            
            # Store in memory
            await self.memory_agent.store_conversation(
                conversation_id,
                conversation["messages"]
            )
            
            return {
                "message": assistant_message,
                "conversation_id": conversation_id,
                "provider": provider,
                "model": model,
                "usage": response.get("usage")
            }
    
    def _get_default_model(self, provider: Provider) -> str:
        """Get default model for provider"""
        if provider == Provider.OLLAMA:
            return settings.ollama_default_model
        elif provider == Provider.LLAMACPP:
            return settings.llamacpp_default_model
        return "default"
    
    def _has_system_message(self, messages: List[Message]) -> bool:
        """Check if messages contain a system message"""
        return any(msg.role == Role.SYSTEM for msg in messages)
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation by ID"""
        if conversation_id in self.conversations:
            return self.conversations[conversation_id]
        
        # Try to load from memory
        messages = await self.memory_agent.get_conversation(conversation_id)
        if messages:
            return {
                "id": conversation_id,
                "messages": messages,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        
        return None
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List all available models from all providers"""
        all_models = []
        
        for provider_type, provider_instance in self.providers.items():
            try:
                models = await provider_instance.list_models()
                all_models.extend([model.dict() for model in models])
            except Exception as e:
                # Log error but continue with other providers
                print(f"Error listing models from {provider_type}: {e}")
        
        return all_models
    
    async def check_providers_status(self) -> List[Dict[str, Any]]:
        """Check status of all configured providers"""
        status_list = []
        
        for provider_type in [Provider.OLLAMA, Provider.LLAMACPP]:
            if provider_type in self.providers:
                provider = self.providers[provider_type]
                is_healthy = await provider.health_check()
                
                status_list.append({
                    "provider": provider_type,
                    "available": is_healthy,
                    "base_url": provider.base_url,
                    "error": None if is_healthy else "Provider is not accessible"
                })
            else:
                status_list.append({
                    "provider": provider_type,
                    "available": False,
                    "base_url": None,
                    "error": "Provider not configured"
                })
        
        return status_list