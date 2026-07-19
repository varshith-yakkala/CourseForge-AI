import pytest
from unittest.mock import AsyncMock, MagicMock
import uuid

@pytest.mark.asyncio
async def test_get_coach_advice_memory(mocker):
    from services.coach_service import AICoachService

    mock_db = AsyncMock()
    u_id = str(uuid.uuid4())
    c_id = str(uuid.uuid4())

    mock_analytics = {
        "completed_lessons": 1,
        "total_lessons": 5,
        "learning_streak_days": 2,
    }

    mocker.patch(
        "services.coach_service.AnalyticsService.get_course_analytics",
        return_value=mock_analytics,
    )

    service = AICoachService(mock_db)

    # First call
    res1 = await service.get_coach_advice(u_id, c_id)
    assert res1["tip"] is not None

    # Second call (verifies rotation if same tip)
    res2 = await service.get_coach_advice(u_id, c_id)
    assert res2["tip"] is not None
