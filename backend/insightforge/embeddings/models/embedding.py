from dataclasses import dataclass

from backend.insightforge.chunking.models.chunk import Chunk


@dataclass
class Embedding:

    chunk: Chunk

    vector: list[float]