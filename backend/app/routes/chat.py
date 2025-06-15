from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import json
from app.models import ChatRequest, ChatResponse, Message, Conversation
from app.agents import ChatAgent
from app.config import settings

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Global chat agent instance
chat_agent = None


async def get_chat_agent() -> ChatAgent:
    """Get or create chat agent instance"""
    global chat_agent
    if not chat_agent:
        chat_agent = ChatAgent()
        await chat_agent.initialize()
    return chat_agent


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    agent: ChatAgent = Depends(get_chat_agent)
):
    """Send a chat message and get response"""
    
    try:
        context = {
            "conversation_id": request.conversation_id,
            "provider": request.provider,
            "model": request.model,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "top_k": request.top_k,
            "max_tokens": request.max_tokens,
            "system_prompt_id": request.system_prompt_id,
            "stream": False
        }
        
        result = await agent.process_messages(request.messages, context)
        
        return ChatResponse(
            message=result["message"],
            provider=result["provider"],
            model=result["model"],
            conversation_id=result["conversation_id"],
            usage=result.get("usage")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def generate_stream(generator: AsyncGenerator[str, None]) -> AsyncGenerator[str, None]:
    """Generate SSE stream from chat response"""
    try:
        async for chunk in generator:
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    agent: ChatAgent = Depends(get_chat_agent)
):
    """Stream chat response using Server-Sent Events"""
    
    if not request.stream:
        request.stream = True
    
    try:
        context = {
            "conversation_id": request.conversation_id,
            "provider": request.provider,
            "model": request.model,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "top_k": request.top_k,
            "max_tokens": request.max_tokens,
            "system_prompt_id": request.system_prompt_id,
            "stream": True
        }
        
        result = await agent.process_messages(request.messages, context)
        
        return StreamingResponse(
            generate_stream(result["stream"]),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: str,
    agent: ChatAgent = Depends(get_chat_agent)
):
    """Get conversation history by ID"""
    
    conversation = await agent.get_conversation(conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return Conversation(
        id=conversation["id"],
        messages=conversation["messages"],
        created_at=conversation["created_at"],
        updated_at=conversation["updated_at"],
        metadata=conversation.get("metadata")
    )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    agent: ChatAgent = Depends(get_chat_agent)
):
    """Delete a conversation"""
    
    # For now, just remove from memory
    if conversation_id in agent.conversations:
        del agent.conversations[conversation_id]
        await agent.memory_agent.clear_conversation(conversation_id)
        return {"message": "Conversation deleted successfully"}
    
    raise HTTPException(status_code=404, detail="Conversation not found")