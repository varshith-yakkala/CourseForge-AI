import pytest
from unittest.mock import AsyncMock, MagicMock
import uuid

@pytest.mark.asyncio
async def test_sm2_spaced_repetition_logic(mocker):
    from services.flashcard_service import FlashcardService

    mock_db = AsyncMock()
    u_id = str(uuid.uuid4())
    fc_id = str(uuid.uuid4())

    mock_res_last = MagicMock()
    mock_res_last.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_res_last

    mocker.patch("services.flashcard_service.InsightForgeEngine")

    service = FlashcardService(mock_db)

    # Test 'good' review (q=4)
    rev = await service.review_flashcard(user_id=u_id, flashcard_id=fc_id, rating_key="good")
    assert rev.rating == "good"
    assert rev.interval_days == 1
    assert float(rev.ease_factor) >= 1.3
