"""
CourseForge AI — Flashcard Generator Service

Responsibility: Generate term/definition flashcards from topic content.

Flow (Phase 2):
    - retrieve_chunks() per topic
    - PromptManager.build("flashcard", ...)
    - Parse JSON array of {front, back}
    - Store in flashcards table
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class FlashcardGeneratorService:
    """Generates flashcards from topic content. Implemented in Phase 2."""

    def generate_for_topic(self, topic_id: str, doc_id: str) -> list[dict]:
        """
        Generate flashcards for a single topic.
        Returns list of {front, back} dicts.
        Implemented in Phase 2.
        """
        raise NotImplementedError("Implemented in Phase 2.")
