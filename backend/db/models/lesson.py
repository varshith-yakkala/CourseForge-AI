import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, Integer, String, Text, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin, TimestampMixin

class Lesson(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "lessons"

    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False) # pending, generating, ready, failed
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_duration_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Phase 7: Interactive Lesson Content & Versioning
    content_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    generated_at = mapped_column(DateTime(timezone=True), nullable=True)
    generation_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    llm_metadata: Mapped[str | None] = mapped_column(Text, nullable=True)

    course = relationship("Course", back_populates="lessons")
    topics = relationship("Topic", back_populates="lesson", cascade="all, delete-orphan")
    quiz = relationship("Quiz", back_populates="lesson", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (Index("idx_lessons_course_order", "course_id", "order_index"),)

