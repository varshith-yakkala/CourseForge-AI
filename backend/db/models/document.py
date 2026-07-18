import uuid
from sqlalchemy import BigInteger, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin

class Document(Base, UUIDMixin):
    __tablename__ = "documents"

    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), unique=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    stored_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    insightforge_doc_id: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    index_status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    chunk_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    indexed_at = mapped_column(DateTime(timezone=True), nullable=True)
    created_at = mapped_column(DateTime(timezone=True), nullable=False)

    course = relationship("Course", back_populates="document")
