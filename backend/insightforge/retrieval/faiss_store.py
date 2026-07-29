import pickle
from pathlib import Path

import faiss
import numpy as np

from backend.insightforge.embeddings.models.embedding import Embedding
from backend.insightforge.retrieval.vector_store import VectorStore


class FAISSStore(VectorStore):

    def __init__(
        self,
        dimension: int = 384,
    ):

        self.dimension = dimension

        self.index = faiss.IndexFlatL2(
            dimension
        )

        self.embeddings = []

    def add(
        self,
        embeddings: list[Embedding],
    ):

        if len(embeddings) == 0:
            return

        vectors = np.array(
            [e.vector for e in embeddings],
            dtype=np.float32,
        )

        self.index.add(vectors)

        self.embeddings.extend(
            embeddings
        )

    def search(
        self,
        query_vector,
        top_k: int = 5,
    ):

        query = np.array(
            [query_vector],
            dtype=np.float32,
        )

        distances, indices = self.index.search(
            query,
            top_k,
        )

        results = []

        for distance, index in zip(
            distances[0],
            indices[0],
        ):

            if index == -1:
                continue

            results.append(
                (
                    self.embeddings[index],
                    float(distance),
                )
            )

        return results

    def save(
        self,
        path: str,
    ):

        path = Path(path)

        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        faiss.write_index(
            self.index,
            str(path / "index.faiss")
        )

        with open(
            path / "metadata.pkl",
            "wb",
        ) as f:

            pickle.dump(
                self.embeddings,
                f
            )

    def load(
        self,
        path: str,
    ):

        path = Path(path)

        self.index = faiss.read_index(
            str(path / "index.faiss")
        )

        with open(
            path / "metadata.pkl",
            "rb",
        ) as f:

            self.embeddings = pickle.load(f)