import uuid
from sqlalchemy import ForeignKey, Integer, String, Text, Numeric, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin

class ChatMessage(Base, UUIDMixin):
    __tablename__ = "chat_messages"

    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sources = mapped_column(JSONB, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    generation_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at = mapped_column(DateTime(timezone=True), nullable=False)

    session = relationship("ChatSession", back_populates="messages")
