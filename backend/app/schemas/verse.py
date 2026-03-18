from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class VerseTranslationCreate(BaseModel):
    language_code: str
    translation: str
    meaning: str | None = None


class VerseTranslationResponse(BaseModel):
    id: UUID
    language_code: str
    translation: str
    meaning: str | None

    model_config = {"from_attributes": True}


class VerseCreate(BaseModel):
    scripture_id: UUID
    chapter: int | None = None
    verse_number: str
    sanskrit: str | None = None
    transliteration: str | None = None
    translations: list[VerseTranslationCreate] = []


class VerseResponse(BaseModel):
    id: UUID
    scripture_id: UUID
    chapter: int | None
    verse_number: str
    sanskrit: str | None
    transliteration: str | None
    translations: list[VerseTranslationResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}
