from backend.insightforge.pipelines.indexing_pipeline import IndexingPipeline
from backend.insightforge.pipelines.query_pipeline import QueryPipeline


class RAGService:

    def __init__(self):

        self.indexer = IndexingPipeline()

        self.query_pipeline = QueryPipeline(
            self.indexer.get_retriever()
        )

    def load_document(
        self,
        path: str,
    ):

        return self.indexer.index(
            path
        )

    def load_documents(
        self,
        paths: list[str],
    ):

        documents = []

        for path in paths:

            result = self.indexer.index(path)

            if result["indexed"]:

                documents.append(
                    result["document"]
                )

        return documents

    def get_documents(self):

        return self.indexer.get_documents()

    def get_document(
        self,
        document_id: str,
    ):

        return self.indexer.get_document(
            document_id
        )

    def get_stats(self):

        documents = self.indexer.get_documents()

        return {

            "documentsIndexed": len(documents),

            "totalChunks": sum(
                d["chunk_count"]
                for d in documents
            ),

            "totalEmbeddings": sum(
                d["chunk_count"]
                for d in documents
            ),

            "totalQueries": 0,

            "avgRetrievalMs": 0,

            "avgLlmResponseMs": 0,
        }

    def query(
        self,
        question: str,
    ):

        return self.query_pipeline.query(
            question
        )