from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    phone_number: str
    name: str | None = None
    email: EmailStr | None = None


class UserResponse(BaseModel):
    id: UUID
    phone_number: str
    name: str | None
    email: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
