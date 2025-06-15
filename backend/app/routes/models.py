from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models import ModelInfo, ProviderStatus
from app.agents import ChatAgent
from app.routes.chat import get_chat_agent

router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("/", response_model=List[ModelInfo])
async def list_models(
    agent: ChatAgent = Depends(get_chat_agent)
):
    """List all available models from all providers"""
    
    try:
        models = await agent.list_models()
        return models
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers", response_model=List[ProviderStatus])
async def check_providers(
    agent: ChatAgent = Depends(get_chat_agent)
):
    """Check status of all configured providers"""
    
    try:
        status_list = await agent.check_providers_status()
        return status_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test/{provider}")
async def test_provider(
    provider: str,
    agent: ChatAgent = Depends(get_chat_agent)
):
    """Test a specific provider connectivity"""
    
    from app.models import Provider, Message, Role
    
    try:
        provider_enum = Provider(provider.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")
    
    if provider_enum not in agent.providers:
        raise HTTPException(status_code=404, detail=f"Provider {provider} not configured")
    
    try:
        # Test with a simple message
        test_message = [Message(role=Role.USER, content="Hello")]
        
        context = {
            "provider": provider_enum,
            "model": agent._get_default_model(provider_enum),
            "max_tokens": 10
        }
        
        result = await agent.process_messages(test_message, context)
        
        return {
            "provider": provider,
            "status": "success",
            "response": result["message"].content[:50] + "..." if len(result["message"].content) > 50 else result["message"].content
        }
        
    except Exception as e:
        return {
            "provider": provider,
            "status": "error",
            "error": str(e)
        }