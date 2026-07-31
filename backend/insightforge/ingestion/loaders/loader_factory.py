import os

from .base_loader import BaseLoader
from .markdown_loader import MarkdownLoader
from .pdf_loader import PDFLoader
from .text_loader import TextLoader


class LoaderFactory:

    @staticmethod
    def get_loader(path: str) -> BaseLoader:

        extension = os.path.splitext(path)[1].lower()

        if extension == ".txt":
            return TextLoader()

        elif extension == ".md":
            return MarkdownLoader()

        elif extension == ".pdf":
            return PDFLoader()

        raise ValueError(f"Unsupported file type: {extension}")