import uuid

from .base_chunker import BaseChunker
from ..models.chunk import Chunk
from ...ingestion.models.document import Document


class CharacterChunker(BaseChunker):

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
    ):

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size."
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, document: Document) -> list[Chunk]:

        chunks = []

        text = document.content

        start = 0

        chunk_number = 0

        while start < len(text):

            end = start + self.chunk_size

            chunk_text = text[start:end]

            chunk = Chunk(
                id=str(uuid.uuid4()),
                document_id=document.id,
                content=chunk_text,
                metadata={
                    **document.metadata,
                    "chunk_number": chunk_number,
                    "start_char": start,
                    "end_char": start + len(chunk_text),
                },
            )

            chunks.append(chunk)

            chunk_number += 1

            start += self.chunk_size - self.chunk_overlap

        return chunks