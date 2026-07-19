import pytest
from unittest.mock import AsyncMock, MagicMock
import uuid
from datetime import date

@pytest.mark.asyncio
async def test_get_adaptive_schedule(mocker):
    from services.study_planner_service import StudyPlannerService

    mock_db = AsyncMock()
    u_id = str(uuid.uuid4())
    c_id = str(uuid.uuid4())

    mock_plan = type("StudyPlan", (), {
        "user_id": u_id,
        "course_id": c_id,
        "daily_goal_min": 30,
        "weekly_goal_min": 210,
        "target_completion_date": date.today(),
        "preferred_study_days": ["Mon", "Tue"],
    })()

    mock_lesson = type("Lesson", (), {
        "id": "l1",
        "title": "Lesson 1",
        "estimated_duration_min": 15,
        "order_index": 0,
    })()

    mock_res_plan = MagicMock()
    mock_res_plan.scalar_one_or_none.return_value = mock_plan

    mock_res_lessons = MagicMock()
    mock_res_lessons.scalars.return_value.all.return_value = [mock_lesson]

    mock_res_progress = MagicMock()
    mock_res_progress.scalars.return_value.all.return_value = []

    mock_db.execute.side_effect = [
        mock_res_plan,
        mock_res_lessons,
        mock_res_progress,
    ]

    service = StudyPlannerService(mock_db)
    sched = await service.get_adaptive_schedule(u_id, c_id)

    assert sched["daily_goal_min"] == 30
    assert len(sched["schedule_blocks"]) >= 1
