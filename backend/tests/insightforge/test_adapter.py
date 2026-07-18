import pytest
from unittest.mock import Mock, patch

def test_adapter_initialization(mocker):
    # Mock settings and import
    mocker.patch("core.config.settings.insightforge_path", "/fake/path")
    mock_rag_service = mocker.patch("backend.services.rag_service.RAGService")
    
    with patch.dict('sys.modules', {'backend.services.rag_service': Mock(RAGService=mock_rag_service)}):
        from insightforge.adapter import InsightForgeAdapter
        adapter = InsightForgeAdapter()
        assert adapter._rag is not None

def test_adapter_index_document(mocker):
    # Mock RAGService
    mock_rag_service = Mock()
    mock_rag_service.load_document.return_value = {"document": {"id": "123"}, "chunks": 5, "indexed": True}
    
    with patch.dict('sys.modules', {'backend.services.rag_service': Mock(RAGService=Mock(return_value=mock_rag_service))}):
        from insightforge.adapter import InsightForgeAdapter
        adapter = InsightForgeAdapter()
        
        result = adapter.index_document("test.pdf")
        
        assert result.doc_id == "123"
        assert result.chunk_count == 5
        assert result.indexed is True
