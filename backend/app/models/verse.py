from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid
from app.db import Base


class Verse(Base):
    __tablename__ = "verses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scripture_id = Column(UUID(as_uuid=True), ForeignKey("scriptures.id"), nullable=False, index=True)
    chapter = Column(Integer, nullable=True)        # e.g. 2 (not all scriptures have chapters)
    verse_number = Column(String, nullable=False)   # String to support formats like "2.47"
    sanskrit = Column(Text, nullable=True)          # Original Sanskrit text
    transliteration = Column(Text, nullable=True)   # Roman transliteration
    embedding = Column(Vector(1536), nullable=True) # For semantic search (OpenAI/Claude embedding dim)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    scripture = relationship("Scripture", back_populates="verses")
    translations = relationship("VerseTranslation", back_populates="verse")
