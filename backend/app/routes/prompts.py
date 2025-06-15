from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from app.models import SystemPrompt
from app.agents import ChatAgent
from app.routes.chat import get_chat_agent

router = APIRouter(prefix="/api/prompts", tags=["prompts"])


@router.get("/", response_model=List[SystemPrompt])
async def list_prompts(
    tags: Optional[List[str]] = Query(None),
    agent: ChatAgent = Depends(get_chat_agent)
):
    """List all available system prompts"""
    
    try:
        prompts = await agent.prompt_agent.list_prompts(tags)
        return prompts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{prompt_id}", response_model=SystemPrompt)
async def get_prompt(
    prompt_id: str,
    agent: ChatAgent = Depends(get_chat_agent)
):
    """Get a specific system prompt by ID"""
    
    prompt = await agent.prompt_agent.get_prompt(prompt_id)
    
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    return prompt


@router.post("/", response_model=SystemPrompt)
async def create_prompt(
    prompt: SystemPrompt,
    agent: ChatAgent = Depends(get_chat_agent)
):
    """Create a new system prompt"""
    
    try:
        # Validate prompt content
        validation = await agent.prompt_agent.validate_prompt(prompt.content)
        if not validation["valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid prompt template: {', '.join(validation['errors'])}"
            )
        
        created_prompt = await agent.prompt_agent.create_prompt(prompt.dict())
        return created_prompt
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{prompt_id}", response_model=SystemPrompt)
async def update_prompt(
    prompt_id: str,
    prompt: SystemPrompt,
    agent: ChatAgent = Depends(get_chat_agent)
):
    """Update an existing system prompt"""
    
    try:
        # Validate prompt content
        validation = await agent.prompt_agent.validate_prompt(prompt.content)
        if not validation["valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid prompt template: {', '.join(validation['errors'])}"
            )
        
        updated_prompt = await agent.prompt_agent.update_prompt(prompt_id, prompt.dict())
        
        if not updated_prompt:
            raise HTTPException(status_code=404, detail="Prompt not found or cannot be updated")
        
        return updated_prompt
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{prompt_id}")
async def delete_prompt(
    prompt_id: str,
    agent: ChatAgent = Depends(get_chat_agent)
):
    """Delete a system prompt"""
    
    success = await agent.prompt_agent.delete_prompt(prompt_id)
    
    if not success:
        raise HTTPException(
            status_code=400, 
            detail="Prompt not found or is a default prompt that cannot be deleted"
        )
    
    return {"message": "Prompt deleted successfully"}


@router.post("/validate")
async def validate_prompt(
    content: str,
    agent: ChatAgent = Depends(get_chat_agent)
):
    """Validate a prompt template"""
    
    validation = await agent.prompt_agent.validate_prompt(content)
    return validation


@router.get("/stats/summary")
async def get_prompt_statistics(
    agent: ChatAgent = Depends(get_chat_agent)
):
    """Get statistics about system prompts"""
    
    stats = agent.prompt_agent.get_prompt_statistics()
    return stats