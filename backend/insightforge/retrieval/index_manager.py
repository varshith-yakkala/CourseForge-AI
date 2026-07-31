from .faiss_store import FAISSStore
from .bm25 import BM25Retriever
from .metadata_store import MetadataStore
from .id_mapper import IDMapper
from .retriever import Retriever
from .hybrid_retriever import HybridRetriever


class IndexManager:

    def __init__(self):

        self.faiss = FAISSStore()

        self.bm25 = BM25Retriever()

        self.metadata = MetadataStore()

        self.mapper = IDMapper()

    def add_embeddings(
        self,
        embeddings,
    ):

        self.faiss.add(embeddings)

        self.bm25.add(embeddings)

        for embedding in embeddings:

            self.metadata.add(
                embedding.chunk
            )

            self.mapper.add(
                embedding.chunk.id
            )

    def get_retriever(self):

        semantic = Retriever(
            self.faiss
        )

        return HybridRetriever(
            semantic,
            self.bm25,
        )

    def save(
        self,
        path,
    ):

        self.faiss.save(path)

        self.metadata.save(path)

        self.mapper.save(path)

    def load(
        self,
        path,
    ):

        self.faiss.load(path)

        self.metadata.load(path)

        self.mapper.load(path)