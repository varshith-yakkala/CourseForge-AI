from dataclasses import dataclass

from ...chunking.models.chunk import Chunk


@dataclass
class Embedding:

    chunk: Chunk

    vector: list[float]