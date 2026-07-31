import json
from pathlib import Path

from ...chunking.models.chunk import Chunk


class ChunkStore:

    def __init__(self, data_dir: str | Path | None = None):
        if data_dir is None:
            try:
                from core.config import settings
                data_dir = settings.storage_dir_path / "chunks"
            except Exception:
                data_dir = Path(__file__).resolve().parent.parent / "data" / "chunks"
        self.root = Path(data_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    def save_chunks(
        self,
        document_id: str,
        chunks: list[Chunk],
    ):

        path = self.root / f"{document_id}.json"

        with open(
            path,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(

                [

                    chunk.to_dict()

                    for chunk in chunks

                ],

                f,

                indent=2,

                ensure_ascii=False,

            )

    def load_chunks(
        self,
        document_id: str,
    ):

        path = self.root / f"{document_id}.json"

        if not path.exists():

            return []

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as f:

            data = json.load(f)

        return [

            Chunk.from_dict(item)

            for item in data

        ]

    def delete_chunks(
        self,
        document_id: str,
    ):

        path = self.root / f"{document_id}.json"

        if path.exists():

            path.unlink()

    def all_documents(self):

        return [

            file.stem

            for file in self.root.glob("*.json")

        ]