import pytest
from unittest.mock import Mock, patch
from core.config import settings

def test_adapter_initialization(monkeypatch):
    monkeypatch.setattr(settings, "INSIGHTFORGE_PATH", "/fake/path")
    mock_rag_class = Mock()
    mock_module = Mock(RAGService=mock_rag_class)
    
    with patch.dict('sys.modules', {'services.rag_service': mock_module}):
        from insightforge.adapter import InsightForgeAdapter
        adapter = InsightForgeAdapter()
        assert adapter._rag is not None

def test_adapter_index_document():
    mock_rag_service = Mock()
    mock_rag_service.load_document.return_value = {"document": {"id": "123"}, "chunks": 5, "indexed": True}
    mock_rag_class = Mock(return_value=mock_rag_service)
    mock_module = Mock(RAGService=mock_rag_class)
    
    with patch.dict('sys.modules', {'services.rag_service': mock_module}):
        from insightforge.adapter import InsightForgeAdapter
        adapter = InsightForgeAdapter()
        
        result = adapter.index_document("test.pdf")
        
        assert result.doc_id == "123"
        assert result.chunk_count == 5
        assert result.indexed is True

def test_adapter_bundled_fallback():
    from insightforge.adapter import InsightForgeAdapter
    from core.exceptions import InsightForgeError
    adapter = InsightForgeAdapter()
    assert adapter.health_check()["status"] == "degraded"
    with pytest.raises(InsightForgeError):
        adapter.index_document("test.pdf")

