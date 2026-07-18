"""
CourseForge AI — InsightForge Engine Adapter

This module defines the InsightForgeEngine class — the single integration
point between CourseForge and the InsightForge-AI RAG engine.

Design decisions (from architecture spec Section 5):
    - Zero modifications to InsightForge source code.
    - CourseForge services only call methods on InsightForgeEngine.
    - doc_ids filter: post-retrieval filter scopes results to a user's course.
    - prompt_override: bypasses InsightForge's PromptBuilder for custom prompts.
    - retrieve_chunks(): raw chunk access without LLM spend.

This file defines the interface and types only.
The concrete implementation lives in adapter.py and is instantiated here.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Return type contracts
# These are plain dataclasses — not ORM models.
# They are the stable interface between InsightForge and CourseForge.
# ─────────────────────────────────────────────


@dataclass(frozen=True)
class ChunkResult:
    """
    A single retrieved chunk from InsightForge.

    Fields:
        chunk_id:       Unique chunk identifier from InsightForge.
        document_id:    InsightForge document ID this chunk belongs to.
        content:        The text content of the chunk.
        score:          Hybrid retrieval score (higher = more relevant).
        page:           PDF page number if available.
        file_name:      Original filename.
        chunk_number:   Index of this chunk within the document.
        metadata:       Raw metadata dict from InsightForge for extensibility.
    """

    chunk_id: str
    document_id: str
    content: str
    score: float
    page: int | None = None
    file_name: str = ""
    chunk_number: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class QueryResult:
    """
    The result of a full RAG query (retrieval + LLM generation).

    Fields:
        answer:             LLM-generated answer text.
        confidence:         Estimated confidence score (0.0–1.0).
        sources:            Unique source documents used.
        chunks:             All retrieved chunks used to build the answer.
        generation_time_ms: Total time taken for retrieval + generation.
        llm_available:      False if LLM failed and answer is a fallback.
    """

    answer: str
    confidence: float
    sources: list[dict[str, Any]]
    chunks: list[ChunkResult]
    generation_time_ms: int
    llm_available: bool = True


@dataclass(frozen=True)
class IndexResult:
    """
    The result of indexing a document into InsightForge.

    Fields:
        doc_id:       InsightForge document registry ID.
        chunk_count:  Number of chunks created.
        indexed:      False if document was already indexed (skipped).
    """

    doc_id: str
    chunk_count: int
    indexed: bool


# ─────────────────────────────────────────────
# Engine
# ─────────────────────────────────────────────


class InsightForgeEngine:
    """
    Adapter wrapping InsightForge-AI internals for use by CourseForge services.

    This class is a SINGLETON — one instance is created at app startup
    and shared across all services via FastAPI dependency injection.

    All methods are synchronous because InsightForge itself is synchronous.
    Async wrappers are handled at the FastAPI route layer via run_in_executor.

    Raises:
        InsightForgeError: If InsightForge cannot be imported or initialized.
    """

    def __init__(self) -> None:
        from insightforge.adapter import InsightForgeAdapter

        self._adapter = InsightForgeAdapter()
        logger.info("InsightForgeEngine initialized successfully.")

    # ─────────────────────────────────────────────
    # Public API — called by CourseForge services
    # ─────────────────────────────────────────────

    def index_document(self, file_path: str) -> IndexResult:
        """
        Ingest a PDF/text/markdown file into FAISS + BM25.

        Args:
            file_path: Absolute path to the file to index.

        Returns:
            IndexResult with doc_id, chunk_count, indexed flag.

        Raises:
            InsightForgeError: If indexing fails.
        """
        return self._adapter.index_document(file_path)

    def query(
        self,
        question: str,
        doc_ids: list[str] | None = None,
        prompt_override: str | None = None,
    ) -> QueryResult:
        """
        Run the full RAG pipeline: retrieve → rerank → compress → LLM generate.

        Args:
            question:        The user's question or generation prompt.
            doc_ids:         If provided, only retrieve chunks from these documents.
                             This is how CourseForge scopes queries to a specific course.
            prompt_override: A fully-built prompt string. If provided, bypasses
                             InsightForge's PromptBuilder and passes directly to the LLM.
                             Used by CourseForge's PromptManager.

        Returns:
            QueryResult with answer, confidence, sources, chunks.

        Raises:
            InsightForgeError: If the query pipeline fails.
        """
        return self._adapter.query(question, doc_ids=doc_ids, prompt_override=prompt_override)

    def retrieve_chunks(
        self,
        query: str,
        doc_ids: list[str] | None = None,
        top_k: int = 10,
    ) -> list[ChunkResult]:
        """
        Retrieve raw chunks WITHOUT LLM generation.

        Use this for:
        - Course structure generation (need chunks, not an LLM answer)
        - Quiz generation (iterate over chunks per topic)
        - Flashcard generation (extract key terms from chunks)
        - Search (return chunks directly to user)

        This avoids unnecessary LLM token spend for tasks that only
        need the retrieved context, not a synthesized answer.

        Args:
            query:   The retrieval query string.
            doc_ids: Scope retrieval to these document IDs.
            top_k:   Maximum number of chunks to return.

        Returns:
            List of ChunkResult, sorted by hybrid score descending.
        """
        return self._adapter.retrieve_chunks(query, doc_ids=doc_ids, top_k=top_k)

    def get_document(self, doc_id: str) -> dict[str, Any] | None:
        """
        Retrieve document metadata from InsightForge registry.

        Returns:
            Document dict with id, file_name, file_type, path, chunk_count.
            None if the document does not exist in the registry.
        """
        return self._adapter.get_document(doc_id)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove a document from the InsightForge FAISS + BM25 index.

        Called when a user deletes a course — cleans up the AI engine index.

        Returns:
            True if deleted, False if document was not found.
        """
        return self._adapter.delete_document(doc_id)

    def health_check(self) -> dict[str, str]:
        """
        Verify InsightForge is operational.

        Returns:
            Dict with embedding_model, llm_model, status.
        """
        return self._adapter.health_check()
