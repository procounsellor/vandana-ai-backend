from sqlalchemy import Column, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.db import Base


class Scripture(Base):
    __tablename__ = "scriptures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)        # e.g. "Bhagavad Gita"
    short_name = Column(String, unique=True, nullable=False)  # e.g. "gita"
    description = Column(Text, nullable=True)
    language = Column(String, nullable=False, default="Sanskrit")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    verses = relationship("Verse", back_populates="scripture")
