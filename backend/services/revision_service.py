"""
CourseForge AI — Revision Service

Responsibility: Generate concise revision summaries per lesson.

Flow (Phase 2):
    - Aggregate topic content for a lesson
    - PromptManager.build("revision_summary", ...)
    - LLM call → plain text summary
    - Cache in Redis (TTL 24h)
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class RevisionService:
    """Generates revision summaries for lessons. Implemented in Phase 2."""

    def get_summary(self, lesson_id: str) -> str:
        """
        Return a revision summary for a lesson.
        Checks Redis cache first; generates via LLM if cache miss.
        Implemented in Phase 2.
        """
        raise NotImplementedError("Implemented in Phase 2.")
