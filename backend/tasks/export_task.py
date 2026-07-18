"""Export background task \u2014 Phase 3 implementation."""

from __future__ import annotations

from tasks.celery_app import celery_app


@celery_app.task(
    name="tasks.export_course",
    bind=True,
    max_retries=3,
    default_retry_delay=5,
)
def export_task(self, course_id: str, format: str, user_id: str) -> dict:  # type: ignore[override]
    """
    Background task: export a course to PDF or Markdown.
    Implemented in Phase 3.
    """
    raise NotImplementedError("export_task implemented in Phase 3.")
