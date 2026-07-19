import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.exceptions import InsightForgeError

@pytest.mark.asyncio
async def test_search_documents_success(mocker):
    from api.search.routes import search_documents, SearchRequest
    
    mock_db = AsyncMock()
    mock_user = type("User", (), {"id": "123"})()
    
    # Mock DB document retrieval
    mock_doc = type("Document", (), {"insightforge_doc_id": "doc1"})()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_doc]
    mock_db.execute.return_value = mock_result
    
    # Mock InsightForge engine
    mock_engine_instance = mocker.patch("api.search.routes.InsightForgeEngine")
    
    mock_chunk = type("Chunk", (), {"content": "Hello", "score": 0.9, "page": 1, "document_id": "doc1"})()
    mock_engine_instance.return_value.retrieve_chunks.return_value = [mock_chunk]
    
    request = SearchRequest(query="test query")
    response = await search_documents(request=request, db=mock_db, current_user=mock_user)
    
    assert "results" in response
    assert len(response["results"]) == 1
    assert response["results"][0]["content"] == "Hello"

@pytest.mark.asyncio
async def test_search_documents_no_docs(mocker):
    from api.search.routes import search_documents, SearchRequest
    
    mock_db = AsyncMock()
    mock_user = type("User", (), {"id": "123"})()
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result
    
    request = SearchRequest(query="test query")
    response = await search_documents(request=request, db=mock_db, current_user=mock_user)
    
    assert response == {"results": []}

