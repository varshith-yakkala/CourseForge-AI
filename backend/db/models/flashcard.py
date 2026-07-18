import uuid
from sqlalchemy import ForeignKey, Integer, Text, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin, TimestampMixin

class Flashcard(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "flashcards"

    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    lesson_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("lessons.id", ondelete="SET NULL"), index=True, nullable=True)
    front: Mapped[str] = mapped_column(Text, nullable=False)
    back: Mapped[str] = mapped_column(Text, nullable=False)
    source_chunk_ids = mapped_column(ARRAY(Text), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)

    reviews = relationship("FlashcardReview", back_populates="flashcard", cascade="all, delete-orphan")
