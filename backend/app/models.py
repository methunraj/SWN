from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum


class Provider(str, Enum):
    OLLAMA = "ollama"
    LLAMACPP = "llamacpp"


class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    id: Optional[str] = None
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    messages: List[Message]
    stream: bool = True
    model: Optional[str] = None
    provider: Optional[Provider] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, gt=0)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    top_k: Optional[int] = Field(None, gt=0)
    system_prompt_id: Optional[str] = None
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    message: Message
    conversation_id: Optional[str] = None
    model: Optional[str] = None
    provider: Optional[str] = None
    usage: Optional[Dict[str, int]] = None


class StreamChunk(BaseModel):
    content: str
    done: bool = False
    metadata: Optional[Dict[str, Any]] = None


class Conversation(BaseModel):
    id: str
    title: str
    messages: List[Message]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None


class Model(BaseModel):
    name: str
    provider: Provider
    description: Optional[str] = None
    context_length: Optional[int] = None
    available: bool = True


class ModelInfo(BaseModel):
    name: str
    provider: Provider
    description: Optional[str] = None
    context_length: Optional[int] = None
    available: bool = True


class ProviderStatus(BaseModel):
    provider: Provider
    available: bool
    models: List[ModelInfo]
    error: Optional[str] = None


class SystemPrompt(BaseModel):
    id: Optional[str] = None
    name: str
    content: str
    description: Optional[str] = None
    category: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_default: bool = False


class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    content_type: str
    size: int
    upload_time: datetime


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    status_code: int


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime
    services: Dict[str, bool]