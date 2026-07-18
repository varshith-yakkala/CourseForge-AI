"""
CourseForge AI — Celery Application

Configures the Celery task queue for background processing.

Tasks registered here:
    - generate_course_task   (Phase 2)
    - generate_quiz_task     (Phase 2)
    - export_task            (Phase 3)

Run a worker:
    celery -A tasks.celery_app worker --loglevel=info

Run with concurrency (production):
    celery -A tasks.celery_app worker --loglevel=info --concurrency=4
"""

from __future__ import annotations

from celery import Celery

from core.config import settings


def create_celery_app() -> Celery:
    """Create and configure the Celery application."""
    celery = Celery(
        "courseforge",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
        include=[
            "tasks.generate_course_task",
            "tasks.generate_quiz_task",
            "tasks.export_task",
            "tasks.document_tasks",
        ],
    )

    celery.conf.update(
        # Serialization
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        # Timezone
        timezone="UTC",
        enable_utc=True,
        # Task behavior
        task_acks_late=True,            # Acknowledge only after task completes
        task_reject_on_worker_lost=True, # Re-queue if worker crashes
        task_time_limit=settings.CELERY_TASK_TIMEOUT_SECONDS,
        task_soft_time_limit=settings.CELERY_TASK_TIMEOUT_SECONDS - 30,
        # Result storage
        result_expires=86400,           # 24 hours
        # Retry
        task_max_retries=settings.CELERY_MAX_RETRIES,
        # Worker
        worker_prefetch_multiplier=1,   # Process one task at a time per worker
        worker_max_tasks_per_child=100, # Restart worker after 100 tasks (prevent memory leaks)
    )

    return celery


celery_app = create_celery_app()
