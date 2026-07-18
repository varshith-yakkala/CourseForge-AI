"""
CourseForge AI — Quiz Generator Service

Responsibility: Generate MCQ, True/False, and open-ended questions per lesson.

Flow (Phase 2):
    - For each lesson: retrieve topic chunks
    - Build quiz prompt (mcq / tf / open)
    - LLM call → parse JSON array of questions
    - Validate structure → store in quiz_questions table
    - Create quiz record linked to lesson
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class QuizGeneratorService:
    """Generates quiz questions from lesson content. Implemented in Phase 2."""

    def generate_for_lesson(self, lesson_id: str, doc_id: str) -> dict:
        """
        Generate a complete quiz for a lesson.
        Returns {quiz_id, question_count}.
        Implemented in Phase 2.
        """
        raise NotImplementedError("Implemented in Phase 2.")
