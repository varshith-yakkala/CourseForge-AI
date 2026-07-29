import os
import uuid

from backend.insightforge.ingestion.loaders.base_loader import BaseLoader
from backend.insightforge.ingestion.models.document import Document


class MarkdownLoader(BaseLoader):

    def load(self, path: str) -> Document:

        with open(path, "r", encoding="utf-8") as file:
            content = file.read()

        metadata = {
            "source": path,
            "file_name": os.path.basename(path),
            "file_type": "markdown"
        }

        return Document(
            id=str(uuid.uuid4()),
            content=content,
            metadata=metadata
        )