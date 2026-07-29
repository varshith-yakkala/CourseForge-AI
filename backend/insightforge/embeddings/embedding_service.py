from sentence_transformers import SentenceTransformer

from backend.insightforge.chunking.models.chunk import Chunk
from backend.insightforge.embeddings.models.embedding import Embedding


class EmbeddingService:

    _model = None

    def __init__(self):

        if EmbeddingService._model is None:
            print("Loading embedding model...")
            EmbeddingService._model = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2"
            )
            print("Embedding model loaded.")

        self.model = EmbeddingService._model

    def embed(self, text: str):

        return self.model.encode(
            text,
            convert_to_numpy=True
        ).tolist()

    def embed_chunks(
        self,
        chunks: list[Chunk],
    ):

        embeddings = []

        for chunk in chunks:

            vector = self.embed(
                chunk.content
            )

            embeddings.append(
                Embedding(
                    chunk=chunk,
                    vector=vector,
                )
            )

        return embeddings