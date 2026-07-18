import uuid
from sqlalchemy import ForeignKey, Numeric, UniqueConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin

class CourseEnrollment(Base, UUIDMixin):
    __tablename__ = "course_enrollments"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    enrolled_at = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at = mapped_column(DateTime(timezone=True), nullable=True)
    progress_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=0.00, nullable=False)
    last_accessed_at = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (UniqueConstraint("user_id", "course_id"),)
