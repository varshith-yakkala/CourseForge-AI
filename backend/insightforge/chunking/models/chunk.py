from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Chunk:

    id: str

    document_id: str

    content: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    chunk_index: int = 0

    start_offset: int = 0

    end_offset: int = 0

    checksum: str = ""

    def to_dict(self):

        return {

            "id": self.id,

            "document_id": self.document_id,

            "content": self.content,

            "metadata": self.metadata,

            "chunk_index": self.chunk_index,

            "start_offset": self.start_offset,

            "end_offset": self.end_offset,

            "checksum": self.checksum,

        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ):

        return cls(

            id=data["id"],

            document_id=data["document_id"],

            content=data["content"],

            metadata=data.get(
                "metadata",
                {},
            ),

            chunk_index=data.get(
                "chunk_index",
                0,
            ),

            start_offset=data.get(
                "start_offset",
                0,
            ),

            end_offset=data.get(
                "end_offset",
                0,
            ),

            checksum=data.get(
                "checksum",
                "",
            ),

        )