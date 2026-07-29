from backend.insightforge.embeddings.embedding_service import EmbeddingService
from backend.insightforge.retrieval.vector_store import VectorStore


class Retriever:

    def __init__(
        self,
        vector_store: VectorStore,
    ):

        self.vector_store = vector_store

        self.embedding_service = EmbeddingService()

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ):

        query_vector = self.embedding_service.embed(
            query
        )

        return self.vector_store.search(
            query_vector,
            top_k,
        )