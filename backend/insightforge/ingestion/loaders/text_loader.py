import os
import uuid

from .base_loader import BaseLoader
from ..models.document import Document


class TextLoader(BaseLoader):

    def load(self, path: str) -> Document:

        with open(path, "r", encoding="utf-8") as file:
            content = file.read()

        filename = os.path.basename(path)

        metadata = {
            "source": path,
            "file_name": filename,
            "file_type": "txt",
        }

        return Document(
            id=str(uuid.uuid4()),
            content=content,
            metadata=metadata,
            filename=filename,
            file_type="txt",
            size_bytes=os.path.getsize(path),
        )