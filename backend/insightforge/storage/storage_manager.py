from pathlib import Path
from .document_registry import DocumentRegistry
from .chunks.chunk_store import ChunkStore
from ..retrieval.faiss_store import FAISSStore
from ..retrieval.bm25 import BM25Retriever

class StorageManager:
    """Storage manager coordinating DocumentRegistry, ChunkStore, FAISS index, and BM25 index."""

    def __init__(self, data_dir: str | Path | None = None):
        if data_dir is None:
            try:
                from core.config import settings
                data_dir = settings.storage_dir_path
            except Exception:
                data_dir = Path(__file__).resolve().parent / "data"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.registry = DocumentRegistry(self.data_dir / "documents.json")
        self.chunk_store = ChunkStore(self.data_dir / "chunks")

    def save_chunks(self, document_id: str, chunks: list):
        self.chunk_store.save_chunks(document_id, chunks)

    def load_chunks(self, document_id: str) -> list:
        return self.chunk_store.load_chunks(document_id)

    def save_indexes(self, faiss_store: FAISSStore, bm25: BM25Retriever):
        faiss_dir = self.data_dir / "faiss"
        faiss_dir.mkdir(parents=True, exist_ok=True)
        faiss_store.save(str(faiss_dir))
        bm25.save(str(self.data_dir / "bm25.pkl"))

    def load_indexes(self, faiss_store: FAISSStore, bm25: BM25Retriever):
        faiss_dir = self.data_dir / "faiss"
        bm25_path = self.data_dir / "bm25.pkl"

        if (faiss_dir / "index.faiss").exists():
            try:
                faiss_store.load(str(faiss_dir))
            except Exception as e:
                print(f"Warning: Failed to load FAISS index from {faiss_dir}: {e}")

        if bm25_path.exists():
            try:
                bm25.load(str(bm25_path))
            except Exception as e:
                print(f"Warning: Failed to load BM25 index from {bm25_path}: {e}")
