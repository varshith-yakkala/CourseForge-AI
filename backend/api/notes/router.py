import uuid
from typing import Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db, get_current_active_user
from db.models.user import User
from services.note_service import NoteService

router = APIRouter(prefix="/notes", tags=["Notes"])

class CreateNoteRequest(BaseModel):
    course_id: uuid.UUID
    lesson_id: uuid.UUID | None = None
    topic_id: uuid.UUID | None = None
    subtopic_id: uuid.UUID | None = None
    content: str
    highlight_text: str | None = None
    color: str = "yellow"
    is_pinned: bool = False

class UpdateNoteRequest(BaseModel):
    content: str | None = None
    color: str | None = None
    is_pinned: bool | None = None

class NoteResponse(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    lesson_id: uuid.UUID | None = None
    topic_id: uuid.UUID | None = None
    content: str
    highlight_text: str | None = None
    color: str
    is_pinned: bool
    created_at: Any

    class Config:
        from_attributes = True

@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    req: CreateNoteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = NoteService(db)
    note = await service.create_note(
        user_id=str(current_user.id),
        course_id=str(req.course_id),
        content=req.content,
        lesson_id=str(req.lesson_id) if req.lesson_id else None,
        topic_id=str(req.topic_id) if req.topic_id else None,
        subtopic_id=str(req.subtopic_id) if req.subtopic_id else None,
        highlight_text=req.highlight_text,
        color=req.color,
        is_pinned=req.is_pinned,
    )
    return note

@router.get("/course/{course_id}", response_model=list[NoteResponse])
async def get_course_notes(
    course_id: uuid.UUID,
    lesson_id: uuid.UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = NoteService(db)
    notes = await service.get_course_notes(
        user_id=str(current_user.id),
        course_id=str(course_id),
        lesson_id=str(lesson_id) if lesson_id else None,
    )
    return notes

@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: uuid.UUID,
    req: UpdateNoteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = NoteService(db)
    note = await service.update_note(
        user_id=str(current_user.id),
        note_id=str(note_id),
        content=req.content,
        color=req.color,
        is_pinned=req.is_pinned,
    )
    return note

@router.delete("/{note_id}")
async def delete_note(
    note_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = NoteService(db)
    await service.delete_note(user_id=str(current_user.id), note_id=str(note_id))
    return {"message": "Note deleted successfully"}
