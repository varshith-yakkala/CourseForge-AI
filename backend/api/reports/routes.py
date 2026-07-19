from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from api.deps import get_db, get_current_user
from db.models.user import User
from services.weekly_report_service import WeeklyReportService
from api.reports.schemas import WeeklyReportResponse

router = APIRouter(tags=["reports"])


@router.get("/courses/{course_id}/weekly-report", response_model=WeeklyReportResponse)
async def get_weekly_report(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = WeeklyReportService(db)
    report = await service.get_or_generate_weekly_report(user_id=str(current_user.id), course_id=str(course_id))
    return report
