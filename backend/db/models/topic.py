import uuid
from sqlalchemy import ForeignKey, Integer, String, Text, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin

class Topic(Base, UUIDMixin):
    __tablename__ = "topics"

    lesson_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    key_terms = mapped_column(ARRAY(Text), nullable=True)
    created_at = mapped_column(Text)

    lesson = relationship("Lesson", back_populates="topics")
    subtopics = relationship("Subtopic", back_populates="topic", cascade="all, delete-orphan")
