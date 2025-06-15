from typing import Dict, Any, Optional, List
import re
from datetime import datetime
import json
from app.models import Message, Role, SystemPrompt
from .base import BaseAgent


class SystemPromptAgent(BaseAgent):
    """Agent responsible for managing system prompts and templates"""
    
    def __init__(self, name: str = "SystemPromptAgent", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.prompts = {}
        self.default_prompts = {
            "default": SystemPrompt(
                id="default",
                name="Default Assistant",
                content="You are a helpful AI assistant. Provide clear, accurate, and helpful responses.",
                description="Default system prompt for general assistance"
            ),
            "coding": SystemPrompt(
                id="coding",
                name="Coding Assistant",
                content="You are an expert programmer. Help with coding questions, debugging, and best practices. Provide clear explanations and working code examples.",
                description="System prompt for programming assistance",
                tags=["programming", "technical"]
            ),
            "creative": SystemPrompt(
                id="creative",
                name="Creative Writing Assistant",
                content="You are a creative writing assistant. Help with storytelling, creative ideas, and writing improvement. Be imaginative and encouraging.",
                description="System prompt for creative writing tasks",
                tags=["writing", "creative"]
            ),
            "analytical": SystemPrompt(
                id="analytical",
                name="Analytical Assistant",
                content="You are an analytical assistant. Provide data-driven insights, logical reasoning, and thorough analysis. Break down complex problems systematically.",
                description="System prompt for analytical tasks",
                tags=["analysis", "data"]
            )
        }
    
    async def initialize(self) -> None:
        """Initialize system prompt agent"""
        # Load default prompts
        self.prompts.update(self.default_prompts)
        
        # Could load custom prompts from database here
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        # Could save custom prompts to database here
        pass
    
    async def process(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """Process system prompt operations"""
        
        if isinstance(input_data, str):
            # Assume it's a prompt ID
            return await self.get_system_message(input_data, context.get("variables", {}))
        elif isinstance(input_data, dict):
            # Could be creating/updating a prompt
            if "action" in input_data:
                action = input_data["action"]
                if action == "create":
                    return await self.create_prompt(input_data.get("prompt"))
                elif action == "update":
                    return await self.update_prompt(input_data.get("id"), input_data.get("prompt"))
                elif action == "delete":
                    return await self.delete_prompt(input_data.get("id"))
        
        return None
    
    async def get_system_message(
        self, 
        prompt_id: str, 
        variables: Optional[Dict[str, Any]] = None
    ) -> Optional[Message]:
        """Get system message from prompt ID with variable substitution"""
        
        prompt = self.prompts.get(prompt_id)
        if not prompt:
            return None
        
        content = prompt.content
        
        # Apply variable substitution
        if variables:
            content = await self._substitute_variables(content, variables)
        
        # Apply dynamic context
        content = await self._apply_dynamic_context(content)
        
        return Message(
            role=Role.SYSTEM,
            content=content
        )
    
    async def _substitute_variables(
        self, 
        content: str, 
        variables: Dict[str, Any]
    ) -> str:
        """Substitute variables in prompt content"""
        
        # Find all variables in the format {variable_name}
        pattern = r'\{(\w+)\}'
        
        def replace_var(match):
            var_name = match.group(1)
            return str(variables.get(var_name, match.group(0)))
        
        return re.sub(pattern, replace_var, content)
    
    async def _apply_dynamic_context(self, content: str) -> str:
        """Apply dynamic context like datetime"""
        
        # Add current datetime if requested
        if "{datetime}" in content:
            current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            content = content.replace("{datetime}", current_time)
        
        # Add other dynamic contexts as needed
        
        return content
    
    async def create_prompt(self, prompt_data: Dict[str, Any]) -> SystemPrompt:
        """Create a new system prompt"""
        
        prompt = SystemPrompt(**prompt_data)
        if not prompt.id:
            prompt.id = f"custom_{len(self.prompts)}"
        
        self.prompts[prompt.id] = prompt
        return prompt
    
    async def update_prompt(
        self, 
        prompt_id: str, 
        prompt_data: Dict[str, Any]
    ) -> Optional[SystemPrompt]:
        """Update an existing system prompt"""
        
        if prompt_id not in self.prompts:
            return None
        
        # Don't update default prompts
        if prompt_id in self.default_prompts:
            return None
        
        prompt = self.prompts[prompt_id]
        for key, value in prompt_data.items():
            if hasattr(prompt, key):
                setattr(prompt, key, value)
        
        prompt.updated_at = datetime.utcnow()
        return prompt
    
    async def delete_prompt(self, prompt_id: str) -> bool:
        """Delete a system prompt"""
        
        # Don't delete default prompts
        if prompt_id in self.default_prompts:
            return False
        
        if prompt_id in self.prompts:
            del self.prompts[prompt_id]
            return True
        
        return False
    
    async def list_prompts(
        self, 
        tags: Optional[List[str]] = None
    ) -> List[SystemPrompt]:
        """List all available prompts, optionally filtered by tags"""
        
        prompts = list(self.prompts.values())
        
        if tags:
            prompts = [
                p for p in prompts 
                if p.tags and any(tag in p.tags for tag in tags)
            ]
        
        return prompts
    
    async def get_prompt(self, prompt_id: str) -> Optional[SystemPrompt]:
        """Get a specific prompt by ID"""
        return self.prompts.get(prompt_id)
    
    async def validate_prompt(self, content: str) -> Dict[str, Any]:
        """Validate a prompt template"""
        
        # Find all variables
        variables = re.findall(r'\{(\w+)\}', content)
        
        # Check for unclosed braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        
        is_valid = open_braces == close_braces
        
        return {
            "valid": is_valid,
            "variables": list(set(variables)),
            "errors": [] if is_valid else ["Mismatched braces in template"]
        }
    
    def get_prompt_statistics(self) -> Dict[str, Any]:
        """Get statistics about prompts"""
        
        total_prompts = len(self.prompts)
        default_prompts = len(self.default_prompts)
        custom_prompts = total_prompts - default_prompts
        
        tags_count = {}
        for prompt in self.prompts.values():
            if prompt.tags:
                for tag in prompt.tags:
                    tags_count[tag] = tags_count.get(tag, 0) + 1
        
        return {
            "total_prompts": total_prompts,
            "default_prompts": default_prompts,
            "custom_prompts": custom_prompts,
            "tags": tags_count
        }