import logging
from pathlib import Path

logger = logging.getLogger(__name__)

from ..chunking.chunkers.character_chunker import CharacterChunker
from ..embeddings.embedding_service import EmbeddingService
from ..ingestion.loaders.loader_factory import LoaderFactory
from ..recovery.recovery_manager import RecoveryManager
from ..retrieval.faiss_store import FAISSStore
from ..retrieval.bm25 import BM25Retriever
from ..retrieval.retriever import Retriever
from ..retrieval.hybrid_retriever import HybridRetriever

from ..storage.storage_manager import StorageManager
from ..storage.models.indexed_document import IndexedDocument


class IndexingPipeline:

    def __init__(self):

        self.loader_factory = LoaderFactory()

        self.chunker = CharacterChunker(
            chunk_size=500,
            chunk_overlap=100,
        )

        self.embedding_service = EmbeddingService()

        self.faiss_store = FAISSStore()

        self.bm25 = BM25Retriever()

        self.semantic_retriever = Retriever(
            self.faiss_store
        )

        self.hybrid_retriever = HybridRetriever(
            self.semantic_retriever,
            self.bm25,
        )

        self.storage = StorageManager()
        self.recovery = RecoveryManager()

        self.registry = self.storage.registry

        self.indexed_files = set()

        self._restore_indexes()

    def _restore_indexes(self):

        self.storage.load_indexes(
            self.faiss_store,
            self.bm25,
        )

        for document in self.registry.all():

            self.indexed_files.add(
                document.path
            )

        print(
            f"Loaded {self.registry.count()} documents."
        )

    def index(
        self,
        file_path: str,
    ):

        file_path = str(
            Path(file_path)
        )

        if file_path in self.indexed_files:

            return {

                "retriever": self.hybrid_retriever,

                "document": None,

                "chunks": 0,

                "indexed": False,

            }

        logger.info("Stage 1: Extracting PDF")
        loader = self.loader_factory.get_loader(
            file_path
        )

        document = loader.load(
            file_path
        )

        if not document.content or not document.content.strip():
            raise ValueError("The uploaded document contains no extractable text. Please upload a document with readable text.")

        logger.info("Stage 2: Chunking Document")
        chunks = self.chunker.chunk(
            document
        )
        self.storage.save_chunks(
    document.id,
    chunks,
)

        logger.info("Stage 3: Generating Embeddings")
        embeddings = self.embedding_service.embed_chunks(
            chunks
        )

        logger.info("Stage 4: Building Vector Index (FAISS)")
        self.faiss_store.add(
            embeddings
        )

        logger.info("Stage 5: Building Vector Index (BM25)")
        self.bm25.add(
            embeddings
        )

        logger.info("Stage 6: Saving Index")
        indexed_document = IndexedDocument(

            id=document.id,

            file_name=document.filename,

            file_type=document.file_type,

            path=file_path,

            chunk_count=len(chunks),

            indexed_at=document.uploaded_at,

            size_bytes=document.size_bytes,

        )

        self.registry.add(
            indexed_document
        )

        self.storage.save_indexes(
            self.faiss_store,
            self.bm25,
        )

        self.indexed_files.add(
            file_path
        )

        logger.info("Stage 7: Completed Indexing")
        return {

            "retriever": self.hybrid_retriever,

            "document": indexed_document.to_dict(),

            "chunks": len(chunks),

            "indexed": True,

        }

    def get_documents(self):

        return [

            document.to_dict()

            for document in self.registry.all()

        ]

    def get_document(
        self,
        document_id: str,
    ):

        document = self.registry.get(
            document_id
        )

        if document is None:

            return None

        return document.to_dict()

    def delete_document(
        self,
        document_id: str,
    ):

        document = self.registry.get(
            document_id
        )

        if document is None:

            return False

        self.registry.remove(
            document_id
        )

        if document.path in self.indexed_files:

            self.indexed_files.remove(
                document.path
            )

        return True

    def get_document_count(self):

        return self.registry.count()

    def get_retriever(self):

        return self.hybrid_retriever