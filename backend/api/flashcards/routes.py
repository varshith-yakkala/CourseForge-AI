from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from api.deps import get_db, get_current_user
from core.rate_limit import limiter, _get_user_or_ip
from db.models.user import User
from services.flashcard_service import FlashcardService
from api.flashcards.schemas import FlashcardResponse, ReviewFlashcardRequest, ReviewFlashcardResponse

router = APIRouter(tags=["flashcards"])


@router.get("/courses/{course_id}/flashcards", response_model=list[FlashcardResponse])
@limiter.limit("30/hour", key_func=_get_user_or_ip)
async def get_or_generate_flashcards(
    request: Request,
    response: Response,
    course_id: uuid.UUID,
    lesson_id: uuid.UUID | None = Query(None),
    mode: str = Query("all", description="all, shuffle, due_today, weak_topics, mastered"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = FlashcardService(db)
    cards = await service.get_or_generate_deck(
        course_id=str(course_id),
        lesson_id=str(lesson_id) if lesson_id else None,
    )
    filtered = await service.get_mode_deck(
        course_id=str(course_id),
        mode=mode,
        user_id=str(current_user.id),
    )
    return filtered


@router.post("/flashcards/{flashcard_id}/review", response_model=ReviewFlashcardResponse)
async def review_flashcard(
    flashcard_id: uuid.UUID,
    req: ReviewFlashcardRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = FlashcardService(db)
    review = await service.review_flashcard(
        user_id=str(current_user.id),
        flashcard_id=str(flashcard_id),
        rating_key=req.rating,
    )
    return review
