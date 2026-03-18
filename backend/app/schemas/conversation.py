from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ConversationCreate(BaseModel):
    language_code: str = "en"


class ConversationResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str | None
    language_code: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
