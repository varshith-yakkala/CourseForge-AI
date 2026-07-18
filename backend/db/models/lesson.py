import uuid
from sqlalchemy import ForeignKey, Integer, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin, TimestampMixin

class Lesson(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "lessons"

    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_duration_min: Mapped[int | None] = mapped_column(Integer, nullable=True)

    course = relationship("Course", back_populates="lessons")
    topics = relationship("Topic", back_populates="lesson", cascade="all, delete-orphan")
    quiz = relationship("Quiz", back_populates="lesson", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (Index("idx_lessons_course_order", "course_id", "order_index"),)
