import pickle
from pathlib import Path

from rank_bm25 import BM25Okapi

from ..embeddings.models.embedding import Embedding


class BM25Retriever:

    def __init__(self):

        self.documents = []

        self.embeddings = []

        self.bm25 = None

    def add(
        self,
        embeddings: list[Embedding],
    ):
        if not embeddings:
            return

        new_docs = [
            embedding.chunk.content.split()
            for embedding in embeddings
            if embedding.chunk.content and embedding.chunk.content.strip()
        ]
        if not new_docs:
            return

        self.embeddings.extend(embeddings)
        self.documents.extend(new_docs)

        if self.documents:
            self.bm25 = BM25Okapi(self.documents)

    def search(
        self,
        query: str,
        top_k: int = 5,
    ):

        if self.bm25 is None:

            return []

        tokenized_query = query.split()

        scores = self.bm25.get_scores(
            tokenized_query
        )

        ranked = sorted(

            zip(
                scores,
                self.embeddings,
            ),

            reverse=True,

            key=lambda x: x[0],

        )

        return ranked[:top_k]

    def save(
        self,
        path: str,
    ):

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            path,
            "wb",
        ) as f:

            pickle.dump(

                {

                    "documents": self.documents,

                    "embeddings": self.embeddings,

                },

                f,

            )

    def load(
        self,
        path: str,
    ):

        path = Path(path)

        if not path.exists():

            return

        with open(
            path,
            "rb",
        ) as f:

            data = pickle.load(
                f
            )

        self.documents = data[
            "documents"
        ]

        self.embeddings = data[
            "embeddings"
        ]

        if len(self.documents):

            self.bm25 = BM25Okapi(
                self.documents
            )