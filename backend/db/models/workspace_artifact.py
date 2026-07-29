import uuid
from sqlalchemy import ForeignKey, String, Text, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin, TimestampMixin

class WorkspaceArtifact(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "workspace_artifacts"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    lesson_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("lessons.id", ondelete="SET NULL"), index=True, nullable=True)
    
    artifact_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. mind_map, cheat_sheet, timeline, comparison_table, pinned_answer
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_json = mapped_column(JSON, nullable=True)
    sources_json = mapped_column(JSON, nullable=True)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user = relationship("User")
    course = relationship("Course")
    lesson = relationship("Lesson")
