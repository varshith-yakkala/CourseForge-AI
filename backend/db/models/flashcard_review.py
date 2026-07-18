import uuid
from sqlalchemy import ForeignKey, Integer, String, Numeric, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin

class FlashcardReview(Base, UUIDMixin):
    __tablename__ = "flashcard_reviews"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    flashcard_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("flashcards.id", ondelete="CASCADE"))
    rating: Mapped[str] = mapped_column(String(10), nullable=False)
    next_review_at = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    interval_days: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    ease_factor: Mapped[float] = mapped_column(Numeric(4, 2), default=2.5, nullable=False)
    reviewed_at = mapped_column(DateTime(timezone=True), nullable=False)

    flashcard = relationship("Flashcard", back_populates="reviews")

    __table_args__ = (Index("idx_flashcard_reviews_user_card", "user_id", "flashcard_id"),)
