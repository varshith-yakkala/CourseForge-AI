from backend.insightforge.retrieval.retriever import Retriever
from backend.insightforge.retrieval.bm25 import BM25Retriever


class HybridRetriever:

    def __init__(
        self,
        semantic_retriever: Retriever,
        bm25_retriever: BM25Retriever,
    ):

        self.semantic = semantic_retriever
        self.bm25 = bm25_retriever

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ):

        semantic_results = self.semantic.retrieve(
            query,
            top_k * 3,
        )

        bm25_results = self.bm25.search(
            query,
            top_k * 3,
        )

        scores = {}

        for embedding, distance in semantic_results:

            chunk_id = embedding.chunk.id

            score = 1 / (1 + distance)

            if chunk_id not in scores:

                scores[chunk_id] = {
                    "embedding": embedding,
                    "score": score,
                }

            else:

                scores[chunk_id]["score"] += score

        for bm25_score, embedding in bm25_results:

            chunk_id = embedding.chunk.id

            if chunk_id not in scores:

                scores[chunk_id] = {
                    "embedding": embedding,
                    "score": bm25_score,
                }

            else:

                scores[chunk_id]["score"] += bm25_score

        ranked = sorted(
            scores.values(),
            key=lambda item: item["score"],
            reverse=True,
        )

        return ranked[:top_k]