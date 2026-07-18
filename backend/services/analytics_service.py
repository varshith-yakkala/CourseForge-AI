"""
CourseForge AI — Analytics Service

Responsibility: Aggregate and compute learning analytics from raw progress events.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Learning analytics aggregation. Implemented in Phase 2."""

    def get_dashboard_stats(self, user_id: str) -> dict:
        """Return high-level dashboard stats. Implemented in Phase 2."""
        raise NotImplementedError("Implemented in Phase 2.")

    def get_heatmap(self, user_id: str) -> list[dict]:
        """Return daily study activity. Implemented in Phase 2."""
        raise NotImplementedError("Implemented in Phase 2.")

    def get_topic_performance(self, user_id: str, course_id: str) -> list[dict]:
        """Return per-topic quiz score aggregates. Implemented in Phase 2."""
        raise NotImplementedError("Implemented in Phase 2.")
