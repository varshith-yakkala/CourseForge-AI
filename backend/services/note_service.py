import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from db.models.note import Note
from core.exceptions import CourseForgeError

class NoteService:
    """Service to handle user Notes & Highlights CRUD operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_note(
        self,
        user_id: str,
        course_id: str,
        content: str,
        lesson_id: str | None = None,
        topic_id: str | None = None,
        subtopic_id: str | None = None,
        highlight_text: str | None = None,
        color: str = "yellow",
        is_pinned: bool = False,
    ) -> Note:
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        course_uuid = uuid.UUID(course_id) if isinstance(course_id, str) else course_id
        lesson_uuid = uuid.UUID(lesson_id) if lesson_id else None
        topic_uuid = uuid.UUID(topic_id) if topic_id else None
        subtopic_uuid = uuid.UUID(subtopic_id) if subtopic_id else None

        note = Note(
            user_id=user_uuid,
            course_id=course_uuid,
            lesson_id=lesson_uuid,
            topic_id=topic_uuid,
            subtopic_id=subtopic_uuid,
            content=content,
            highlight_text=highlight_text,
            color=color,
            is_pinned=is_pinned,
        )
        self.db.add(note)
        await self.db.commit()
        await self.db.refresh(note)
        return note

    async def get_course_notes(self, user_id: str, course_id: str, lesson_id: str | None = None) -> Sequence[Note]:
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        course_uuid = uuid.UUID(course_id) if isinstance(course_id, str) else course_id

        stmt = select(Note).where(Note.user_id == user_uuid, Note.course_id == course_uuid)
        if lesson_id:
            lesson_uuid = uuid.UUID(lesson_id) if isinstance(lesson_id, str) else lesson_id
            stmt = stmt.where(Note.lesson_id == lesson_uuid)

        stmt = stmt.order_by(Note.is_pinned.desc(), Note.created_at.desc())
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def update_note(self, user_id: str, note_id: str, content: str | None = None, color: str | None = None, is_pinned: bool | None = None) -> Note:
        note_uuid = uuid.UUID(note_id) if isinstance(note_id, str) else note_id
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id

        stmt = select(Note).where(Note.id == note_uuid, Note.user_id == user_uuid)
        res = await self.db.execute(stmt)
        note = res.scalar_one_or_none()
        if not note:
            raise CourseForgeError("Note not found", status_code=404)

        if content is not None:
            note.content = content
        if color is not None:
            note.color = color
        if is_pinned is not None:
            note.is_pinned = is_pinned

        self.db.add(note)
        await self.db.commit()
        await self.db.refresh(note)
        return note

    async def delete_note(self, user_id: str, note_id: str) -> bool:
        note_uuid = uuid.UUID(note_id) if isinstance(note_id, str) else note_id
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id

        stmt = delete(Note).where(Note.id == note_uuid, Note.user_id == user_uuid)
        await self.db.execute(stmt)
        await self.db.commit()
        return True
