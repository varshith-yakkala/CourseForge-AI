from dataclasses import dataclass


@dataclass
class IndexedDocument:

    id: str

    file_name: str

    file_type: str

    path: str

    chunk_count: int

    indexed_at: str

    status: str = "indexed"

    size_bytes: int = 0

    def to_dict(self):

        return {

            "id": self.id,

            "file_name": self.file_name,

            "file_type": self.file_type,

            "path": self.path,

            "chunk_count": self.chunk_count,

            "indexed_at": self.indexed_at,

            "status": self.status,

            "size_bytes": self.size_bytes,

        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ):

        return cls(

            id=data["id"],

            file_name=data["file_name"],

            file_type=data["file_type"],

            path=data["path"],

            chunk_count=data["chunk_count"],

            indexed_at=data["indexed_at"],

            status=data.get(
                "status",
                "indexed",
            ),

            size_bytes=data.get(
                "size_bytes",
                0,
            ),

        )