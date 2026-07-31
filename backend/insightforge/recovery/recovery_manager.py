from ..retrieval.faiss_store import FAISSStore
from ..retrieval.bm25 import BM25Retriever
from ..storage.storage_manager import StorageManager


class RecoveryManager:

    def __init__(self):

        self.storage = StorageManager()

    def recover(
        self,
        faiss_store: FAISSStore,
        bm25: BM25Retriever,
    ):

        print("\n" + "=" * 60)
        print("Starting Recovery Manager...")
        print("=" * 60)

        self.storage.load_indexes(
            faiss_store,
            bm25,
        )

        documents = self.storage.registry.count()

        embeddings = len(
            faiss_store.embeddings
        )

        bm25_docs = len(
            bm25.embeddings
        )

        print()

        print(f"Documents : {documents}")
        print(f"Embeddings : {embeddings}")
        print(f"BM25 Docs  : {bm25_docs}")

        if embeddings != bm25_docs:

            print()
            print("WARNING:")
            print("FAISS and BM25 counts differ!")

        print()
        print("Recovery Complete.")
        print("=" * 60)