import uuid
from sqlalchemy import ForeignKey, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin, TimestampMixin

class ChatSession(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "chat_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_chat_sessions_user_course", "user_id", "course_id"),)
