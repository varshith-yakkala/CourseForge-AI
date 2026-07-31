import uuid
from typing import List

from .base_chunker import BaseChunker
from ..models.chunk import Chunk
from ...ingestion.models.document import Document


class RecursiveChunker(BaseChunker):

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        separators: List[str] | None = None,
    ):

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size."
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.separators = separators or [
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]

    def chunk(self, document: Document) -> List[Chunk]:

        splits = self._split_text(
            document.content,
            self.separators,
        )

        merged = self._merge_splits(splits)

        chunks = []

        for index, text in enumerate(merged):

            chunks.append(
                Chunk(
                    id=str(uuid.uuid4()),
                    document_id=document.id,
                    content=text,
                    metadata={
                        **document.metadata,
                        "chunk_number": index,
                        "length": len(text),
                    },
                )
            )

        return chunks

    def _split_text(
        self,
        text: str,
        separators: List[str],
    ) -> List[str]:

        if len(text) <= self.chunk_size:
            return [text]

        if not separators:
            return [
                text[i:i + self.chunk_size]
                for i in range(
                    0,
                    len(text),
                    self.chunk_size,
                )
            ]

        separator = separators[0]

        if separator == "":
            splits = list(text)
        else:
            splits = text.split(separator)

        good_splits = []

        for split in splits:

            if len(split) <= self.chunk_size:

                good_splits.append(split)

            else:

                good_splits.extend(
                    self._split_text(
                        split,
                        separators[1:],
                    )
                )

        return good_splits

    def _merge_splits(
        self,
        splits: List[str],
    ) -> List[str]:

        chunks = []

        current = ""

        for split in splits:

            separator = " "

            if (
                len(current)
                + len(separator)
                + len(split)
                <= self.chunk_size
            ):

                if current:

                    current += separator + split

                else:

                    current = split

            else:

                if current:

                    chunks.append(current)

                current = split

        if current:

            chunks.append(current)

        return self._apply_overlap(chunks)

    def _apply_overlap(
        self,
        chunks: List[str],
    ) -> List[str]:

        if (
            self.chunk_overlap == 0
            or len(chunks) <= 1
        ):
            return chunks

        overlapped = []

        for i, chunk in enumerate(chunks):

            if i == 0:

                overlapped.append(chunk)

                continue

            previous = overlapped[-1]

            overlap = previous[-self.chunk_overlap:]

            overlapped.append(
                overlap + chunk
            )

        return overlapped