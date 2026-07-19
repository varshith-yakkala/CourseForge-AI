import pytest
from unittest.mock import AsyncMock, MagicMock
import uuid

@pytest.mark.asyncio
async def test_calculate_predictions(mocker):
    from services.learning_prediction_service import LearningPredictionService

    mock_db = AsyncMock()
    u_id = str(uuid.uuid4())
    c_id = str(uuid.uuid4())

    mock_analytics = {
        "completed_lessons": 3,
        "total_lessons": 5,
        "avg_quiz_score": 88.0,
    }

    mocker.patch(
        "services.learning_prediction_service.AnalyticsService.get_course_analytics",
        return_value=mock_analytics,
    )

    service = LearningPredictionService(mock_db)
    res = await service.calculate_predictions(u_id, c_id)

    assert res["on_time_probability_pct"] >= 70.0
    assert res["predicted_quiz_score_pct"] == 88.0
    assert res["confidence_level"] == "High"
