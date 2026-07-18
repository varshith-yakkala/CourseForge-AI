import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_process_document_success(mocker):
    from tasks.document_tasks import _process_document_async
    
    # Mock DB Session
    mock_session = AsyncMock()
    mock_session_cm = AsyncMock()
    mock_session_cm.__aenter__.return_value = mock_session
    mocker.patch("db.session.get_db_session", return_value=mock_session_cm)
    
    # Mock Document
    mock_doc = type("Document", (), {"id": "123", "stored_path": "test.pdf", "index_status": "pending"})()
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = mock_doc
    mock_session.execute.return_value = mock_result
    
    # Mock InsightForgeEngine
    mock_engine_instance = mocker.patch("tasks.document_tasks.InsightForgeEngine")
    mock_adapter = mock_engine_instance.return_value.adapter
    mock_index_result = type("IndexResult", (), {"doc_id": "if_123", "chunk_count": 10})()
    mock_adapter.index_document.return_value = mock_index_result
    
    result = await _process_document_async("123")
    
    assert result == {"status": "success", "doc_id": "123"}
    assert mock_doc.index_status == "ready"
    assert mock_doc.insightforge_doc_id == "if_123"
    assert mock_doc.chunk_count == 10

@pytest.mark.asyncio
async def test_process_document_not_found(mocker):
    from tasks.document_tasks import _process_document_async
    
    # Mock DB Session
    mock_session = AsyncMock()
    mock_session_cm = AsyncMock()
    mock_session_cm.__aenter__.return_value = mock_session
    mocker.patch("db.session.get_db_session", return_value=mock_session_cm)
    
    # Mock Document Not Found
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result
    
    result = await _process_document_async("123")
    
    assert result == {"status": "error", "message": "Document not found"}
