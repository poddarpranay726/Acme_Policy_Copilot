from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class ChatRequest(BaseModel):
    query: str = Field(min_length=1)
    conversation_id: UUID


class Source(BaseModel):
    source: str
    page: int
    chunk_id: str


class ChatResponse(BaseModel):
    query: str
    rewritten_query: Optional[str] = None
    answer: str
    sources: List[Source]

class MessageResponse(BaseModel):
    message_id: UUID
    role: str
    content: str
    created_at: datetime