import uuid
from sqlalchemy import ForeignKey, String, Text, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin, TimestampMixin

class Note(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "notes"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    lesson_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("lessons.id", ondelete="SET NULL"), index=True, nullable=True)
    topic_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("topics.id", ondelete="SET NULL"), index=True, nullable=True)
    subtopic_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("subtopics.id", ondelete="SET NULL"), index=True, nullable=True)
    
    content: Mapped[str] = mapped_column(Text, nullable=False)
    highlight_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    color: Mapped[str] = mapped_column(String(20), default="yellow", nullable=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tags = mapped_column(JSON, nullable=True)

    user = relationship("User")
    course = relationship("Course")
    lesson = relationship("Lesson")
