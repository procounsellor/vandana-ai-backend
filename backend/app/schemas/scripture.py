from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ScriptureCreate(BaseModel):
    name: str
    short_name: str
    description: str | None = None
    language: str = "Sanskrit"


class ScriptureResponse(BaseModel):
    id: UUID
    name: str
    short_name: str
    description: str | None
    language: str
    created_at: datetime

    model_config = {"from_attributes": True}
