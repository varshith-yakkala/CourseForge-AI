from ..chunking.models.chunk import Chunk
from .models.embedding import Embedding


class EmbeddingService:

    _model = None

    def __init__(self):
        pass

    @classmethod
    def get_model(cls):
        if cls._model is None:
            print("Loading embedding model lazily...")
            from sentence_transformers import SentenceTransformer
            cls._model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            print("Embedding model loaded.")
        return cls._model

    def embed(self, text: str):
        model = self.get_model()
        return model.encode(
            text,
            convert_to_numpy=True
        ).tolist()

    def embed_chunks(
        self,
        chunks: list[Chunk],
    ):
        if not chunks:
            return []

        import gc
        import logging
        logger = logging.getLogger(__name__)

        model = self.get_model()
        texts = [chunk.content for chunk in chunks]
        
        logger.info(f"Encoding {len(texts)} chunks in batches of 32...")
        # Batch size of 32 drastically reduces intermediate tensor allocations
        # compared to looping one-by-one.
        vectors = model.encode(
            texts,
            batch_size=32,
            convert_to_numpy=True
        )
        
        # Free string list and force GC to clear any intermediate tensors
        del texts
        gc.collect()

        embeddings = []
        for chunk, vector in zip(chunks, vectors):
            embeddings.append(
                Embedding(
                    chunk=chunk,
                    vector=vector.tolist(),
                )
            )

        # Force GC again after list comprehension
        del vectors
        gc.collect()

        return embeddings