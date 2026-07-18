"""
CourseForge AI — InsightForge Low-Level Adapter

This module handles the actual import and wiring of InsightForge-AI internals.
It is the ONLY file that directly imports from InsightForge.

If InsightForge changes its internal module structure, only this file needs updating.

Key design: doc_ids filtering
    InsightForge's HybridRetriever uses a single shared FAISS index for all documents.
    To scope queries to a specific course, we post-filter retrieved chunks by checking
    chunk.metadata["document_id"] against the provided doc_ids list.
    This avoids maintaining separate indexes per course/user.

Key design: prompt_override
    InsightForge's QueryPipeline uses its own PromptBuilder. CourseForge has a
    PromptManager with versioned, purpose-specific prompts. When prompt_override
    is provided, we call GeminiGenerator.generate() directly, bypassing PromptBuilder.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

from core.config import settings
from core.exceptions import InsightForgeError
from insightforge.engine import ChunkResult, IndexResult, QueryResult

logger = logging.getLogger(__name__)


class InsightForgeAdapter:
    """
    Low-level adapter that imports and wraps InsightForge internals.

    Instantiated once by InsightForgeEngine. Never instantiated directly
    by services — always go through InsightForgeEngine.
    """

    def __init__(self) -> None:
        self._rag = self._initialize_rag_service()

    def _initialize_rag_service(self) -> Any:
        """
        Import InsightForge RAGService and initialize it.

        InsightForge path is added to sys.path by Settings.ensure_insightforge_on_sys_path().
        This runs automatically when settings is imported.

        Raises:
            InsightForgeError: If InsightForge cannot be imported or initialized.
        """
        try:
            # These imports resolve because Settings added the InsightForge root to sys.path
            from backend.services.rag_service import RAGService  # type: ignore[import]

            rag = RAGService()
            logger.info(
                "InsightForge RAGService loaded.",
                extra={"insightforge_path": str(settings.insightforge_path)},
            )
            return rag

        except ImportError as exc:
            raise InsightForgeError(
                f"Failed to import InsightForge modules from {settings.insightforge_path}. "
                f"Ensure the project exists and all dependencies are installed. "
                f"Original error: {exc}"
            ) from exc

        except Exception as exc:
            raise InsightForgeError(
                f"InsightForge RAGService initialization failed: {exc}"
            ) from exc

    # ─────────────────────────────────────────────
    # Index
    # ─────────────────────────────────────────────

    def index_document(self, file_path: str) -> IndexResult:
        """Wrap InsightForge RAGService.load_document()."""
        try:
            result = self._rag.load_document(file_path)

            return IndexResult(
                doc_id=result["document"]["id"] if result.get("document") else "",
                chunk_count=result.get("chunks", 0),
                indexed=result.get("indexed", False),
            )

        except InsightForgeError:
            raise
        except Exception as exc:
            raise InsightForgeError(f"Failed to index document '{file_path}': {exc}") from exc

    # ─────────────────────────────────────────────
    # Query (full RAG pipeline)
    # ─────────────────────────────────────────────

    def query(
        self,
        question: str,
        doc_ids: list[str] | None = None,
        prompt_override: str | None = None,
    ) -> QueryResult:
        """
        Run full RAG pipeline with optional doc_id filtering and prompt override.
        """
        try:
            if prompt_override is not None:
                # Bypass InsightForge's PromptBuilder — use our versioned prompt directly.
                raw = self._query_with_prompt_override(question, prompt_override, doc_ids)
            else:
                raw = self._rag.query(question)

            # Post-filter by doc_ids if specified
            sources = raw.get("sources", [])
            chunks_raw = raw.get("retrievedChunks", [])

            if doc_ids:
                sources = [s for s in sources if s.get("documentId") in doc_ids]

            chunks = [
                ChunkResult(
                    chunk_id=c.get("id", ""),
                    document_id=c.get("documentId", ""),
                    content=c.get("text", ""),
                    score=c.get("similarity", 0.0),
                    page=c.get("page"),
                    chunk_number=c.get("chunkIndex", 0),
                )
                for c in chunks_raw
                if not doc_ids or c.get("documentId") in (doc_ids or [])
            ]

            return QueryResult(
                answer=raw.get("answer", ""),
                confidence=raw.get("confidence", 0.0),
                sources=sources,
                chunks=chunks,
                generation_time_ms=raw.get("generationTimeMs", 0),
                llm_available=raw.get("llmAvailable", True),
            )

        except InsightForgeError:
            raise
        except Exception as exc:
            raise InsightForgeError(f"Query pipeline failed: {exc}") from exc

    def _query_with_prompt_override(
        self,
        question: str,
        prompt: str,
        doc_ids: list[str] | None,
    ) -> dict[str, Any]:
        """
        Use InsightForge's retrieval stack but replace its prompt with ours.

        Steps:
        1. Retrieve chunks via HybridRetriever
        2. Apply doc_ids filter
        3. Call GeminiGenerator.generate() with our prompt
        """
        try:
            from backend.retrieval.hybrid_retriever import HybridRetriever  # type: ignore[import]
            from backend.llm.generator import GeminiGenerator  # type: ignore[import]
            from backend.retrieval.confidence import ConfidenceEstimator  # type: ignore[import]
            import time

            start = time.time()

            retriever = self._rag.indexer.get_retriever()
            candidates = retriever.retrieve(question, top_k=30)

            if doc_ids:
                candidates = [
                    c for c in candidates
                    if c["embedding"].chunk.metadata.get("document_id") in doc_ids
                    or c["embedding"].chunk.document_id in doc_ids
                ]

            confidence_estimator = ConfidenceEstimator()
            confidence = confidence_estimator.estimate(candidates[:5])

            generator = GeminiGenerator()
            generation = generator.generate(prompt)

            generation_time_ms = int((time.time() - start) * 1000)

            sources = []
            chunks_raw = []
            seen = set()

            for result in candidates[:5]:
                embedding = result["embedding"]
                chunk = embedding.chunk
                meta = chunk.metadata
                filename = meta.get("file_name", "Unknown")

                if filename not in seen:
                    seen.add(filename)
                    sources.append({
                        "id": chunk.id,
                        "documentId": chunk.document_id,
                        "filename": filename,
                        "page": meta.get("page"),
                        "similarity": round(result.get("score", 0.0), 4),
                    })

                chunks_raw.append({
                    "id": chunk.id,
                    "documentId": chunk.document_id,
                    "text": chunk.content,
                    "page": meta.get("page"),
                    "chunkIndex": meta.get("chunk_number", 0),
                    "similarity": round(result.get("score", 0.0), 4),
                })

            return {
                "answer": generation.get("answer", "") if generation.get("success") else "",
                "confidence": confidence,
                "sources": sources,
                "retrievedChunks": chunks_raw,
                "generationTimeMs": generation_time_ms,
                "llmAvailable": generation.get("success", False),
            }

        except Exception as exc:
            raise InsightForgeError(f"Prompt-override query failed: {exc}") from exc

    # ─────────────────────────────────────────────
    # Retrieve chunks (no LLM)
    # ─────────────────────────────────────────────

    def retrieve_chunks(
        self,
        query: str,
        doc_ids: list[str] | None = None,
        top_k: int = 10,
    ) -> list[ChunkResult]:
        """Retrieve chunks without LLM generation."""
        try:
            retriever = self._rag.indexer.get_retriever()
            candidates = retriever.retrieve(query, top_k=top_k * 3)

            results: list[ChunkResult] = []

            for result in candidates:
                embedding = result["embedding"]
                chunk = embedding.chunk
                meta = chunk.metadata

                doc_id = chunk.document_id

                if doc_ids and doc_id not in doc_ids:
                    continue

                results.append(
                    ChunkResult(
                        chunk_id=chunk.id,
                        document_id=doc_id,
                        content=chunk.content,
                        score=round(result.get("score", 0.0), 4),
                        page=meta.get("page"),
                        file_name=meta.get("file_name", ""),
                        chunk_number=meta.get("chunk_number", 0),
                        metadata=meta,
                    )
                )

                if len(results) >= top_k:
                    break

            return results

        except InsightForgeError:
            raise
        except Exception as exc:
            raise InsightForgeError(f"Chunk retrieval failed: {exc}") from exc

    # ─────────────────────────────────────────────
    # Document registry
    # ─────────────────────────────────────────────

    def get_document(self, doc_id: str) -> dict[str, Any] | None:
        """Look up a document in InsightForge registry."""
        try:
            return self._rag.get_document(doc_id)
        except Exception as exc:
            raise InsightForgeError(f"Failed to get document '{doc_id}': {exc}") from exc

    def delete_document(self, doc_id: str) -> bool:
        """Remove document from InsightForge index."""
        try:
            return self._rag.indexer.delete_document(doc_id)
        except Exception as exc:
            raise InsightForgeError(f"Failed to delete document '{doc_id}': {exc}") from exc

    def health_check(self) -> dict[str, str]:
        """Return InsightForge component status."""
        return {
            "status": "healthy",
            "embedding_model": settings.EMBEDDING_MODEL,
            "llm_model": settings.GROQ_MODEL,
        }
