from sqlalchemy import Column, String, Text, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.db import Base


class VerseTranslation(Base):
    __tablename__ = "verse_translations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    verse_id = Column(UUID(as_uuid=True), ForeignKey("verses.id"), nullable=False, index=True)
    language_code = Column(String(10), nullable=False)  # e.g. "en", "hi", "te", "gu", "sa"
    author = Column(String, nullable=True)               # e.g. "Swami Sivananda"
    translation = Column(Text, nullable=False)
    meaning = Column(Text, nullable=True)               # Commentary/deeper explanation in that language
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("verse_id", "language_code", "author", name="uq_verse_language_author"),
    )

    verse = relationship("Verse", back_populates="translations")
