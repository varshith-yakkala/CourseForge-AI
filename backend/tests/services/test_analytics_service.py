import pytest
from unittest.mock import AsyncMock, MagicMock
import uuid

@pytest.mark.asyncio
async def test_get_course_analytics(mocker):
    from services.analytics_service import AnalyticsService

    mock_db = AsyncMock()
    c_id = str(uuid.uuid4())
    u_id = str(uuid.uuid4())

    mock_lesson = type("Lesson", (), {"id": "l1", "title": "Lesson 1", "course_id": c_id})()
    mock_prog = type("UserProgress", (), {"lesson_id": "l1", "completed": True, "time_spent_sec": 300})()

    mock_res_lessons = MagicMock()
    mock_res_lessons.scalars.return_value.all.return_value = [mock_lesson]

    mock_res_prog = MagicMock()
    mock_res_prog.scalars.return_value.all.return_value = [mock_prog]

    mock_res_quizzes = MagicMock()
    mock_res_quizzes.scalars.return_value.all.return_value = []

    mock_res_cards = MagicMock()
    mock_res_cards.scalars.return_value.all.return_value = []

    mock_db.execute.side_effect = [
        mock_res_lessons,
        mock_res_prog,
        mock_res_quizzes,
        mock_res_cards,
    ]

    service = AnalyticsService(mock_db)
    res = await service.get_course_analytics(user_id=u_id, course_id=c_id)

    assert res["overall_progress_pct"] == 100.0
    assert res["completed_lessons"] == 1
    assert res["total_time_spent_min"] == 5.0
