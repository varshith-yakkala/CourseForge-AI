from abc import ABC, abstractmethod

from ..embeddings.models.embedding import Embedding


class VectorStore(ABC):

    @abstractmethod
    def add(
        self,
        embeddings: list[Embedding],
    ):
        pass

    @abstractmethod
    def search(
        self,
        query_vector,
        top_k: int = 5,
    ):
        pass

    @abstractmethod
    def save(
        self,
        path: str,
    ):
        pass

    @abstractmethod
    def load(
        self,
        path: str,
    ):
        pass