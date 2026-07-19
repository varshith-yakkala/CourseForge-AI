from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from db.session import get_db
from core.dependencies import get_current_user
from db.models.user import User
from services.study_planner_service import StudyPlannerService
from services.learning_prediction_service import LearningPredictionService
from api.planner.schemas import (
    StudyPlanRequest,
    AdaptiveScheduleResponse,
    CalendarEventResponse,
    LearningPredictionsResponse,
)

router = APIRouter(tags=["planner"])


@router.get("/courses/{course_id}/planner", response_model=AdaptiveScheduleResponse)
async def get_adaptive_study_plan(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = StudyPlannerService(db)
    sched = await service.get_adaptive_schedule(user_id=str(current_user.id), course_id=str(course_id))
    return AdaptiveScheduleResponse(**sched)


@router.post("/courses/{course_id}/planner", response_model=AdaptiveScheduleResponse)
async def update_study_plan(
    course_id: uuid.UUID,
    req: StudyPlanRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = StudyPlannerService(db)
    await service.update_plan(
        user_id=str(current_user.id),
        course_id=str(course_id),
        daily_goal_min=req.daily_goal_min,
        target_date=req.target_completion_date,
        preferred_days=req.preferred_study_days,
    )
    sched = await service.get_adaptive_schedule(user_id=str(current_user.id), course_id=str(course_id))
    return AdaptiveScheduleResponse(**sched)


@router.get("/courses/{course_id}/calendar", response_model=list[CalendarEventResponse])
async def get_calendar_events(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = StudyPlannerService(db)
    events = await service.get_calendar_events(user_id=str(current_user.id), course_id=str(course_id))
    return events


@router.get("/courses/{course_id}/predictions", response_model=LearningPredictionsResponse)
async def get_learning_predictions(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = LearningPredictionService(db)
    preds = await service.calculate_predictions(user_id=str(current_user.id), course_id=str(course_id))
    return LearningPredictionsResponse(**preds)
