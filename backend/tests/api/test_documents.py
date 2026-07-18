import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_upload_document(mocker):
    from api.documents.routes import upload_document
    
    mock_db = AsyncMock()
    mock_user = type("User", (), {"id": "123"})()
    mock_file = AsyncMock()
    mock_file.content_type = "application/pdf"
    mock_file.filename = "test.pdf"
    mock_file.read.side_effect = [b"mock data", b""] # 1 chunk, then EOF
    
    # Mock course retrieval to return a valid course
    mock_course = type("Course", (), {"id": "c_id", "owner_id": "123"})()
    mock_result_course = AsyncMock()
    mock_result_course.scalar_one_or_none.return_value = mock_course
    
    # Mock doc retrieval to return None (no existing doc)
    mock_result_doc = AsyncMock()
    mock_result_doc.scalar_one_or_none.return_value = None
    
    mock_db.execute.side_effect = [mock_result_course, mock_result_doc]
    
    with patch("builtins.open", mocker.mock_open()), patch("os.makedirs"):
        result = await upload_document(course_id="c_id", file=mock_file, db=mock_db, current_user=mock_user)
        
        assert result.original_filename == "test.pdf"
        assert result.mime_type == "application/pdf"
        assert result.course_id == "c_id"
