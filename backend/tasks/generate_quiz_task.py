"""Quiz generation background task \u2014 Phase 2 implementation."""

from __future__ import annotations

from tasks.celery_app import celery_app


@celery_app.task(
    name="tasks.generate_quiz",
    bind=True,
    max_retries=3,
    default_retry_delay=5,
)
def generate_quiz_task(self, lesson_id: str) -> dict:  # type: ignore[override]
    """
    Background task: generate quiz questions for a lesson.
    Implemented in Phase 2.
    """
    raise NotImplementedError("generate_quiz_task implemented in Phase 2.")
