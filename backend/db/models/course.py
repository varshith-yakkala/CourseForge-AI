import uuid
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, Numeric, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

class Course(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "courses"

    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="processing", index=True, nullable=False)
    generation_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str | None] = mapped_column(String(20), nullable=True)
    estimated_duration_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tags = mapped_column(ARRAY(Text), nullable=True, index=True)

    owner = relationship("User", back_populates="courses")
    document = relationship("Document", back_populates="course", uselist=False)
    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")
