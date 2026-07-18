import uuid
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin

class Subtopic(Base, UUIDMixin):
    __tablename__ = "subtopics"

    topic_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), index=True)
    lesson_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lessons.id"))
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id"))
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at = mapped_column(Text)

    topic = relationship("Topic", back_populates="subtopics")
