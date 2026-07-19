import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_list_courses(mocker):
    # Mock db and current_user
    mock_db = AsyncMock()
    mock_user = type("User", (), {"id": "123"})()
    
    # Simulate an API request (Unit test style for routes without DB)
    from api.courses.routes import list_courses
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result
    
    result = await list_courses(db=mock_db, current_user=mock_user)
    assert result == []

@pytest.mark.asyncio
async def test_create_course(mocker):
    from api.courses.routes import create_course
    from api.courses.schemas import CourseCreate
    
    mock_db = AsyncMock()
    mock_user = type("User", (), {"id": "123"})()
    course_in = CourseCreate(title="Test Course", description="Desc")
    
    result = await create_course(db=mock_db, course_in=course_in, current_user=mock_user)
    assert result.title == "Test Course"
    assert result.status == "ready"

