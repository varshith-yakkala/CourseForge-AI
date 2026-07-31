from pathlib import Path
from typing import List, Optional
from .models.indexed_document import IndexedDocument
from .persistence.json_store import JSONStore

class DocumentRegistry:
    def __init__(self, file_path: str | Path | None = None):
        if file_path is None:
            file_path = Path(__file__).resolve().parent / "data" / "documents.json"
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.store = JSONStore(str(self.file_path))
        self._documents: dict[str, IndexedDocument] = {}
        self._load()

    def _load(self):
        data = self.store.load()
        if isinstance(data, list):
            for item in data:
                doc = IndexedDocument.from_dict(item)
                self._documents[doc.id] = doc

    def _save(self):
        data = [doc.to_dict() for doc in self._documents.values()]
        self.store.save(data)

    def all(self) -> List[IndexedDocument]:
        return list(self._documents.values())

    def get(self, document_id: str) -> Optional[IndexedDocument]:
        return self._documents.get(document_id)

    def add(self, document: IndexedDocument):
        self._documents[document.id] = document
        self._save()

    def remove(self, document_id: str) -> bool:
        if document_id in self._documents:
            del self._documents[document_id]
            self._save()
            return True
        return False

    def count(self) -> int:
        return len(self._documents)
