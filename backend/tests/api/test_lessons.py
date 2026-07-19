import pytest
from unittest.mock import AsyncMock, MagicMock
import uuid

@pytest.mark.asyncio
async def test_get_lesson_detail(mocker):
    from api.lessons.routes import get_lesson_detail
    
    mock_db = AsyncMock()
    mock_user = type("User", (), {"id": uuid.uuid4()})()
    
    l_id = uuid.uuid4()
    c_id = uuid.uuid4()
    
    mock_lesson = type("Lesson", (), {
        "id": l_id,
        "course_id": c_id,
        "title": "Lesson 1",
        "summary": "Summary 1",
        "status": "ready",
        "order_index": 0,
        "estimated_duration_min": 15,
        "content_markdown": "# Lesson 1 Content",
        "version": 1,
        "generated_at": None,
        "generation_error": None,
        "topics": [],
    })()
    
    mock_res_lesson = MagicMock()
    mock_res_lesson.scalar_one_or_none.return_value = mock_lesson
    
    mock_res_prog = MagicMock()
    mock_res_prog.scalar_one_or_none.return_value = None
    
    mock_db.execute.side_effect = [mock_res_lesson, mock_res_prog]
    
    result = await get_lesson_detail(course_id=c_id, lesson_id=l_id, db=mock_db, current_user=mock_user)
    assert result.title == "Lesson 1"
    assert result.content_markdown == "# Lesson 1 Content"

@pytest.mark.asyncio
async def test_update_lesson_progress(mocker):
    from api.lessons.routes import update_lesson_progress
    from api.lessons.schemas import UpdateProgressRequest
    
    mock_db = AsyncMock()
    mock_user = type("User", (), {"id": uuid.uuid4()})()
    
    l_id = uuid.uuid4()
    c_id = uuid.uuid4()
    
    mock_res_prog = MagicMock()
    mock_res_prog.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_res_prog
    
    req = UpdateProgressRequest(status="completed", completed=True, completion_percentage=100, time_spent_sec=60)
    result = await update_lesson_progress(course_id=c_id, lesson_id=l_id, req=req, db=mock_db, current_user=mock_user)
    
    assert result.status == "completed"
    assert result.completed is True
