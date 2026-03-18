from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.models.message import MessageRole


class ChatRequest(BaseModel):
    conversation_id: UUID | None = None   # None = start a new conversation
    message: str
    language_code: str = "en"


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    cited_verses: list[str] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    conversation_id: UUID
    message: MessageResponse
