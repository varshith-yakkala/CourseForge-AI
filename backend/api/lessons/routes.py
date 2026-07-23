"""
CourseForge AI — Lesson & Progress API Routes
"""
import uuid
from datetime import datetime, timezone
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from api.deps import get_current_active_user, get_db
from core.rate_limit import limiter, _get_user_or_ip
from api.lessons.schemas import (
    LessonDetailResponse,
    UpdateProgressRequest,
    ProgressResponse,
    CourseProgressOverview,
    AskTutorRequest,
    AskTutorResponse,
)
from db.models.user import User
from db.models.lesson import Lesson
from db.models.course import Course
from db.models.progress import UserProgress
from services.lesson_generator import LessonGeneratorService
from services.lesson_tutor import LessonTutorService

router = APIRouter(tags=["Lessons"])


@router.get("/courses/{course_id}/lessons/{lesson_id}", response_model=LessonDetailResponse)
async def get_lesson_detail(
    course_id: uuid.UUID,
    lesson_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get lesson details and content.
    If the lesson status is 'pending', automatically trigger on-demand generation.
    """
    stmt = select(Lesson).where(Lesson.id == lesson_id, Lesson.course_id == course_id)
    res = await db.execute(stmt)
    lesson = res.scalar_one_or_none()

    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # On-demand generation if pending
    if lesson.status == "pending" or not lesson.content_markdown:
        service = LessonGeneratorService(db)
        try:
            lesson = await service.generate_lesson(str(course_id), str(lesson_id), force_regenerate=False)
        except Exception as exc:
            await db.rollback()
            # If generation fails, return the lesson object with status="failed"
            stmt_refreshed = select(Lesson).where(Lesson.id == lesson_id)
            res_refreshed = await db.execute(stmt_refreshed)
            lesson = res_refreshed.scalar_one_or_none() or lesson

    # Track last_opened_at in progress
    stmt_prog = select(UserProgress).where(
        UserProgress.user_id == current_user.id,
        UserProgress.lesson_id == lesson_id,
    )
    res_prog = await db.execute(stmt_prog)
    prog = res_prog.scalar_one_or_none()

    now = datetime.now(timezone.utc)
    if not prog:
        prog = UserProgress(
            user_id=current_user.id,
            course_id=course_id,
            lesson_id=lesson_id,
            entity_type="lesson",
            status="in_progress",
            started_at=now,
            last_opened_at=now,
        )
        db.add(prog)
    else:
        prog.last_opened_at = now
        if prog.status == "not_started":
            prog.status = "in_progress"
            prog.started_at = now
        db.add(prog)

    await db.commit()
    return lesson


@router.post("/courses/{course_id}/lessons/{lesson_id}/generate", response_model=LessonDetailResponse)
@limiter.limit("30/hour", key_func=_get_user_or_ip)
async def generate_lesson(
    request: Request,
    response: Response,
    course_id: uuid.UUID,
    lesson_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Generate or retrieve cached lesson content."""
    service = LessonGeneratorService(db)
    lesson = await service.generate_lesson(str(course_id), str(lesson_id), force_regenerate=False)
    return lesson


@router.post("/courses/{course_id}/lessons/{lesson_id}/regenerate", response_model=LessonDetailResponse)
@limiter.limit("30/hour", key_func=_get_user_or_ip)
async def regenerate_lesson(
    request: Request,
    response: Response,
    course_id: uuid.UUID,
    lesson_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Force regenerate lesson content, incrementing lesson version."""
    service = LessonGeneratorService(db)
    lesson = await service.generate_lesson(str(course_id), str(lesson_id), force_regenerate=True)
    return lesson


@router.post("/courses/{course_id}/lessons/{lesson_id}/progress", response_model=ProgressResponse)
async def update_lesson_progress(
    course_id: uuid.UUID,
    lesson_id: uuid.UUID,
    req: UpdateProgressRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update learning progress for a specific lesson."""
    stmt = select(UserProgress).where(
        UserProgress.user_id == current_user.id,
        UserProgress.lesson_id == lesson_id,
    )
    res = await db.execute(stmt)
    prog = res.scalar_one_or_none()

    now = datetime.now(timezone.utc)
    if not prog:
        prog = UserProgress(
            user_id=current_user.id,
            course_id=course_id,
            lesson_id=lesson_id,
            entity_type="lesson",
            status=req.status,
            completed=req.completed,
            completion_percentage=100 if req.completed else req.completion_percentage,
            started_at=now,
            completed_at=now if req.completed else None,
            last_opened_at=now,
            last_scroll_position=req.last_scroll_position,
            time_spent_sec=req.time_spent_sec,
        )
    else:
        prog.status = req.status
        prog.completed = req.completed or prog.completed
        prog.completion_percentage = 100 if prog.completed else max(prog.completion_percentage, req.completion_percentage)
        if req.completed and not prog.completed_at:
            prog.completed_at = now
        prog.last_opened_at = now
        if req.last_scroll_position is not None:
            prog.last_scroll_position = req.last_scroll_position
        if req.time_spent_sec > 0:
            prog.time_spent_sec = (prog.time_spent_sec or 0) + req.time_spent_sec

    db.add(prog)
    await db.commit()
    await db.refresh(prog)
    return prog


@router.get("/courses/{course_id}/progress", response_model=CourseProgressOverview)
async def get_course_progress(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get total learning progress overview for a course."""
    # Count total lessons in course
    stmt_count = select(func.count(Lesson.id)).where(Lesson.course_id == course_id)
    res_count = await db.execute(stmt_count)
    total_lessons = res_count.scalar() or 0

    # Fetch progress entries
    stmt_prog = select(UserProgress).where(
        UserProgress.user_id == current_user.id,
        UserProgress.course_id == course_id,
        UserProgress.entity_type == "lesson",
    )
    res_prog = await db.execute(stmt_prog)
    progress_entries = res_prog.scalars().all()

    completed_lessons = sum(1 for p in progress_entries if p.completed or p.status == "completed")
    progress_percentage = int((completed_lessons / total_lessons * 100)) if total_lessons > 0 else 0

    # Find last opened lesson
    sorted_entries = sorted(
        [p for p in progress_entries if p.last_opened_at],
        key=lambda x: x.last_opened_at,
        reverse=True,
    )
    last_opened_id = sorted_entries[0].lesson_id if sorted_entries else None

    return CourseProgressOverview(
        course_id=course_id,
        total_lessons=total_lessons,
        completed_lessons=completed_lessons,
        progress_percentage=progress_percentage,
        last_opened_lesson_id=last_opened_id,
        lessons_progress=progress_entries,
    )


@router.post("/courses/{course_id}/lessons/{lesson_id}/ask", response_model=AskTutorResponse)
@limiter.limit("60/hour", key_func=_get_user_or_ip)
async def ask_lesson_tutor(
    request: Request,
    response: Response,
    course_id: uuid.UUID,
    lesson_id: uuid.UUID,
    req: AskTutorRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Ask a question to the AI tutor scoped strictly to the current lesson."""
    tutor_service = LessonTutorService(db)
    res = await tutor_service.ask_question(str(course_id), str(lesson_id), req.question)
    return AskTutorResponse(answer=res["answer"], lesson_id=lesson_id)
