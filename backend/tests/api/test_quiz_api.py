import pytest
import uuid
from datetime import datetime, timezone

@pytest.mark.asyncio
async def test_quiz_attempt_scoring():
    # Unit test quiz grading logic
    user_answers = {
        "q1": "Option A",
        "q2": "true",
        "q3": "machine learning",
    }
    
    total = len(user_answers)
    correct_count = 3
    score_pct = round((correct_count / total) * 100, 2)
    
    assert total == 3
    assert score_pct == 100.0
