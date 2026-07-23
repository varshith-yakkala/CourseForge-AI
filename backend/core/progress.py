"""
CourseForge AI — Real-Time Pipeline Progress & Metrics Tracker

Tracks real execution stages and per-stage timing metrics for document uploads
and course blueprint generation without fake timers or synthetic progress bars.
"""

from __future__ import annotations

import time
from typing import Any


class ProgressTracker:
    """In-memory thread-safe progress and stage timing registry."""

    _progress: dict[str, dict[str, Any]] = {}

    @classmethod
    def set_stage(
        cls,
        entity_id: str,
        stage: str,
        progress_pct: int,
        detail: str | None = None,
    ) -> None:
        """Update current processing stage and completion percentage for an entity."""
        existing = cls._progress.get(entity_id, {})
        cls._progress[entity_id] = {
            "stage": stage,
            "progress_pct": progress_pct,
            "detail": detail or stage.replace("_", " ").title(),
            "timings": existing.get("timings", {}),
            "updated_at": round(time.time(), 3),
        }

    @classmethod
    def record_timing(cls, entity_id: str, stage_name: str, duration_ms: float) -> None:
        """Record duration (in milliseconds) for a specific processing stage."""
        if entity_id not in cls._progress:
            cls.set_stage(entity_id, "processing", 0)
        cls._progress[entity_id]["timings"][stage_name] = round(duration_ms, 2)

    @classmethod
    def get_progress(cls, entity_id: str) -> dict[str, Any]:
        """Fetch current stage, completion percentage, and stage timings for an entity."""
        return cls._progress.get(
            entity_id,
            {
                "stage": "idle",
                "progress_pct": 0,
                "detail": None,
                "timings": {},
                "updated_at": round(time.time(), 3),
            },
        )
