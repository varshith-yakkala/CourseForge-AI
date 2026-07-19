from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from db.session import get_db
from core.dependencies import get_current_user
from db.models.user import User
from services.analytics_service import AnalyticsService
from services.achievement_service import AchievementService
from services.export_service import ExportService
from api.analytics.schemas import (
    CourseAnalyticsResponse,
    RevisionRecommendationResponse,
    UserAchievementResponse,
    ExportSummaryResponse,
)

router = APIRouter(tags=["analytics"])


@router.get("/courses/{course_id}/analytics", response_model=CourseAnalyticsResponse)
async def get_course_analytics(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AnalyticsService(db)
    res = await service.get_course_analytics(user_id=str(current_user.id), course_id=str(course_id))
    return CourseAnalyticsResponse(**res)


@router.get("/courses/{course_id}/recommendations", response_model=list[RevisionRecommendationResponse])
async def get_revision_recommendations(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AnalyticsService(db)
    recs = await service.get_revision_recommendations(user_id=str(current_user.id), course_id=str(course_id))
    return recs


@router.get("/user/achievements", response_model=list[UserAchievementResponse])
async def get_user_achievements(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AchievementService(db)
    # Ensure default first_lesson badge if user has progress
    await service.check_and_unlock(str(current_user.id), "first_lesson")
    achievements = await service.get_user_achievements(str(current_user.id))
    return achievements


@router.get("/courses/{course_id}/export", response_model=ExportSummaryResponse)
async def export_course_summary(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ExportService(db)
    md = await service.export_markdown_summary(user_id=str(current_user.id), course_id=str(course_id))
    return ExportSummaryResponse(markdown_content=md)
