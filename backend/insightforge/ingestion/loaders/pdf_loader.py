import os
import uuid

from pypdf import PdfReader

from backend.insightforge.ingestion.loaders.base_loader import BaseLoader
from backend.insightforge.ingestion.models.document import Document


class PDFLoader(BaseLoader):

    def load(self, path: str) -> Document:

        reader = PdfReader(path)

        content = ""

        for page in reader.pages:
            text = page.extract_text()

            if text:
                content += text + "\n"

        metadata = {
            "source": path,
            "file_name": os.path.basename(path),
            "file_type": "pdf",
            "page_count": len(reader.pages)
        }

        return Document(
            id=str(uuid.uuid4()),
            content=content,
            metadata=metadata
        )