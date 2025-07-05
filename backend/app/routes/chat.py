from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse, Response
from typing import AsyncGenerator, List, Dict, Any
import json
import datetime
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
            "provider": request.provider.value if request.provider else None,
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
        import traceback
        error_detail = traceback.format_exc()
        print(f"Streaming error: {error_detail}")
        yield f"data: {json.dumps({'error': str(e), 'detail': error_detail})}\n\n"


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
            "provider": request.provider.value if request.provider else None,
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


@router.put("/conversations/{conversation_id}/rename")
async def rename_conversation(
    conversation_id: str,
    data: Dict[str, str],
    agent: ChatAgent = Depends(get_chat_agent)
):
    """Rename a conversation"""
    new_title = data.get("title", "").strip()
    
    if not new_title:
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    
    # For now, just update in memory
    if conversation_id in agent.conversations:
        if "metadata" not in agent.conversations[conversation_id]:
            agent.conversations[conversation_id]["metadata"] = {}
        agent.conversations[conversation_id]["metadata"]["title"] = new_title
        agent.conversations[conversation_id]["updated_at"] = datetime.datetime.utcnow()
        
        return {"message": "Conversation renamed successfully", "title": new_title}
    
    raise HTTPException(status_code=404, detail="Conversation not found")


@router.get("/conversations/{conversation_id}/export")
async def export_conversation(
    conversation_id: str,
    format: str = Query("json", regex="^(json|markdown|txt)$"),
    agent: ChatAgent = Depends(get_chat_agent)
):
    """Export conversation in different formats"""
    
    if conversation_id not in agent.conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation = agent.conversations[conversation_id]
    title = conversation.get("metadata", {}).get("title", f"Conversation {conversation_id}")
    
    if format == "json":
        content = json.dumps(conversation, indent=2, default=str)
        media_type = "application/json"
        filename = f"{title.replace(' ', '_')}.json"
    
    elif format == "markdown":
        content = f"# {title}\n\n"
        for msg in conversation.get("messages", []):
            content += f"## {msg['role'].upper()}\n{msg['content']}\n\n"
        media_type = "text/markdown"
        filename = f"{title.replace(' ', '_')}.md"
    
    elif format == "txt":
        content = f"{title}\n{'=' * len(title)}\n\n"
        for msg in conversation.get("messages", []):
            content += f"{msg['role'].upper()}: {msg['content']}\n\n"
        media_type = "text/plain"
        filename = f"{title.replace(' ', '_')}.txt"
    
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/search")
async def search_conversations(
    query: str = Query(..., min_length=1),
    chat_id: str = Query(None),
    agent: ChatAgent = Depends(get_chat_agent)
):
    """Search within conversations"""
    
    results = []
    query_lower = query.lower()
    
    conversations_to_search = [chat_id] if chat_id else agent.conversations.keys()
    
    for conv_id in conversations_to_search:
        if conv_id in agent.conversations:
            conversation = agent.conversations[conv_id]
            conv_title = conversation.get("metadata", {}).get("title", f"Conversation {conv_id}")
            
            for msg in conversation.get("messages", []):
                if query_lower in msg.get("content", "").lower():
                    results.append({
                        "conversation_id": conv_id,
                        "conversation_title": conv_title,
                        "message_id": msg.get("id"),
                        "content": msg.get("content", ""),
                        "role": msg.get("role"),
                        "timestamp": msg.get("timestamp")
                    })
    
    return {"results": results, "total": len(results)}


@router.get("/conversations")
async def list_conversations(
    agent: ChatAgent = Depends(get_chat_agent)
):
    """List all conversations"""
    
    conversations = []
    for conv_id, conversation in agent.conversations.items():
        title = conversation.get("metadata", {}).get("title", f"Conversation {conv_id}")
        message_count = len(conversation.get("messages", []))
        
        conversations.append({
            "id": conv_id,
            "title": title,
            "message_count": message_count,
            "created_at": conversation.get("created_at"),
            "updated_at": conversation.get("updated_at"),
            "last_message": conversation.get("messages", [])[-1] if conversation.get("messages") else None
        })
    
    # Sort by updated_at descending
    conversations.sort(key=lambda x: x.get("updated_at", datetime.datetime.min), reverse=True)
    
    return {"conversations": conversations}