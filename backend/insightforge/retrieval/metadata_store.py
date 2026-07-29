import pickle
from pathlib import Path

from backend.insightforge.chunking.models.chunk import Chunk


class MetadataStore:

    def __init__(self):

        self.store = {}

    def add(
        self,
        chunk: Chunk,
    ):

        self.store[chunk.id] = chunk

    def get(
        self,
        chunk_id: str,
    ):

        return self.store.get(chunk_id)

    def all(self):

        return self.store

    def save(
        self,
        path: str,
    ):

        path = Path(path)

        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            path / "metadata_store.pkl",
            "wb",
        ) as f:

            pickle.dump(
                self.store,
                f,
            )

    def load(
        self,
        path: str,
    ):

        path = Path(path)

        file = path / "metadata_store.pkl"

        if file.exists():

            with open(
                file,
                "rb",
            ) as f:

                self.store = pickle.load(
                    f
                )