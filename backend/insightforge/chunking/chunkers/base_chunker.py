from abc import ABC, abstractmethod

from ...ingestion.models.document import Document
from ..models.chunk import Chunk


class BaseChunker(ABC):

    @abstractmethod
    def chunk(self, document: Document) -> list[Chunk]:
        """
        Split a document into chunks.

        Args:
            document: Input document.

        Returns:
            List of Chunk objects.
        """
        pass