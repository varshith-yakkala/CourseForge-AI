from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from db.session import get_db
from core.dependencies import get_current_user
from db.models.user import User
from services.coach_service import AICoachService
from services.habit_tracking_service import HabitTrackingService
from services.notification_service import NotificationService
from api.coach.schemas import CoachAdviceResponse, HabitStatsResponse, NotificationResponse

router = APIRouter(tags=["coach"])


@router.get("/coach/advice", response_model=CoachAdviceResponse)
async def get_coach_advice(
    course_id: uuid.UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AICoachService(db)
    res = await service.get_coach_advice(user_id=str(current_user.id), course_id=str(course_id) if course_id else None)
    return CoachAdviceResponse(**res)


@router.get("/coach/habits/{course_id}", response_model=HabitStatsResponse)
async def get_habit_stats(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = HabitTrackingService(db)
    res = await service.get_habit_stats(user_id=str(current_user.id), course_id=str(course_id))
    return HabitStatsResponse(**res)


@router.get("/notifications", response_model=list[NotificationResponse])
async def get_notifications(
    priority: str | None = Query(None, description="critical, high, medium, low"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)
    res = await service.get_user_notifications(user_id=str(current_user.id), priority=priority)
    return res


@router.post("/notifications/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)
    res = await service.mark_as_read(user_id=str(current_user.id), notification_id=str(notification_id))
    return res
