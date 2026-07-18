import uuid
from sqlalchemy import ForeignKey, String, Text, UniqueConstraint, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base, UUIDMixin

class Bookmark(Base, UUIDMixin):
    __tablename__ = "bookmarks"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    entity_type: Mapped[str] = mapped_column(String(20), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "entity_type", "entity_id"),
        Index("idx_bookmarks_user_course", "user_id", "course_id"),
    )
