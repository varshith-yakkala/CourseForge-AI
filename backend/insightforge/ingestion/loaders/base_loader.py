from abc import ABC, abstractmethod

from ..models.document import Document


class BaseLoader(ABC):

    @abstractmethod
    def load(self, path: str) -> Document:
        """
        Load a document from the given path.

        Args:
            path (str): Path to the file.

        Returns:
            Document: Parsed document object.
        """
        pass