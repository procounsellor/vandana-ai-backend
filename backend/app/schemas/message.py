from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.models.message import MessageRole


class ChatRequest(BaseModel):
    conversation_id: UUID | None = None
    message: str
    language_code: str = "en"
    scripture_short_name: str | None = None


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
