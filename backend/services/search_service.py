"""
CourseForge AI — Search Service

Responsibility: Unified search across lessons, topics, and content chunks.

Flow (Phase 2):
    - InsightForgeEngine.retrieve_chunks(query, doc_ids=[...], top_k=10)
    - PostgreSQL ILIKE search against lesson/topic titles
    - Merge + deduplicate results by relevance
    - Return {lessons, topics, chunks} grouped response
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class SearchService:
    """Unified semantic + keyword search. Implemented in Phase 2."""

    def search(self, query: str, course_id: str | None = None) -> dict:
        """
        Search across all user content.
        Args:
            query:     Search query string.
            course_id: If set, scope results to this course.
        Returns:
            {lessons: [...], topics: [...], chunks: [...]}
        Implemented in Phase 2.
        """
        raise NotImplementedError("Implemented in Phase 2.")
