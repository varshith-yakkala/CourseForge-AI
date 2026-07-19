import pytest
from unittest.mock import AsyncMock, MagicMock
import json

@pytest.mark.asyncio
async def test_generate_blueprint_success(mocker):
    from services.course_generator import CourseGeneratorService
    
    mock_db = AsyncMock()
    
    # Mock Course
    mock_course = type("Course", (), {"id": "123", "status": "processing", "title": "", "description": "", "difficulty": "", "estimated_duration_min": 0, "tags": []})()
    # Mock Document
    mock_doc = type("Document", (), {"course_id": "123", "insightforge_doc_id": "if123", "index_status": "ready"})()
    
    # Setup mock_db execute to return course, doc, and empty lessons
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.side_effect = [mock_course, mock_doc]
    mock_db.execute.return_value = mock_result
    
    mock_engine_instance = mocker.patch("services.course_generator.InsightForgeEngine")
    
    mock_chunk = type("Chunk", (), {"content": "Test context"})()
    mock_engine_instance.return_value.retrieve_chunks.return_value = [mock_chunk]
    
    mock_query_result = type("QueryResult", (), {
        "answer": json.dumps({
            "title": "Test Course",
            "description": "Desc",
            "difficulty": "Beginner",
            "learning_objectives": ["Obj 1"],
            "estimated_duration_min": 60,
            "tags": ["tag1"],
            "lessons": [
                {
                    "title": "Lesson 1",
                    "summary": "Sum 1",
                    "estimated_duration_min": 30,
                    "topics": [
                        {
                            "title": "Topic 1",
                            "description": "Topic sum",
                            "key_terms": [],
                            "subtopics": []
                        }
                    ]
                }
            ]
        })
    })()
    mock_engine_instance.return_value.query.return_value = mock_query_result
    
    service = CourseGeneratorService(mock_db)
    result = await service.generate_blueprint("123")
    
    assert result == {"status": "success", "course_id": "123"}
    assert mock_course.title == "Test Course"
    assert mock_course.status == "ready"
    assert mock_db.add.call_count >= 2 # Lesson and Topic

