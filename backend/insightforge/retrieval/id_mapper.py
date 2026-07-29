import pickle
from pathlib import Path


class IDMapper:

    def __init__(self):

        self.chunk_to_index = {}

        self.index_to_chunk = {}

        self.next_index = 0

    def add(
        self,
        chunk_id: str,
    ):

        if chunk_id in self.chunk_to_index:

            return self.chunk_to_index[
                chunk_id
            ]

        index = self.next_index

        self.chunk_to_index[
            chunk_id
        ] = index

        self.index_to_chunk[
            index
        ] = chunk_id

        self.next_index += 1

        return index

    def get_chunk_id(
        self,
        index: int,
    ):

        return self.index_to_chunk.get(
            index
        )

    def get_index(
        self,
        chunk_id: str,
    ):

        return self.chunk_to_index.get(
            chunk_id
        )

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
            path / "id_mapper.pkl",
            "wb",
        ) as f:

            pickle.dump(
                (
                    self.chunk_to_index,
                    self.index_to_chunk,
                    self.next_index,
                ),
                f,
            )

    def load(
        self,
        path: str,
    ):

        path = Path(path)

        file = path / "id_mapper.pkl"

        if file.exists():

            with open(
                file,
                "rb",
            ) as f:

                (
                    self.chunk_to_index,
                    self.index_to_chunk,
                    self.next_index,
                ) = pickle.load(
                    f
                )