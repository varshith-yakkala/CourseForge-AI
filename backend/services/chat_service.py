"""
CourseForge AI — Chat Service

Responsibility: Handle AI Tutor conversations scoped to a course.

Flow per message (Phase 2):
    - Load session history (last 10 turns)
    - InsightForgeEngine.query(question, doc_ids=[course_doc_id])
    - Build chat_tutor prompt with history + retrieved chunks
    - Call LLM with prompt_override
    - Save message + response to chat_messages table
    - Return {answer, confidence, sources, citations}
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class ChatService:
    """AI Tutor conversation handler. Implemented in Phase 2."""

    def handle_message(
        self,
        session_id: str,
        user_message: str,
        course_id: str,
    ) -> dict:
        """
        Process a user message and return an AI response.
        Returns {answer, confidence, sources, session_id, message_id}.
        Implemented in Phase 2.
        """
        raise NotImplementedError("Implemented in Phase 2.")
