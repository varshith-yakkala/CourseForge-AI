"""
CourseForge AI — Health Check Endpoint

GET /api/v1/health

Returns the operational status of all system components:
    - Application
    - Database (Phase 2+)
    - Redis (Phase 2+)
    - InsightForge AI Engine

This endpoint is public (no authentication required).
Used by Docker health checks, monitoring, and the frontend status indicator.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter
from pydantic import BaseModel

from core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])


class ComponentStatus(BaseModel):
    status: str
    detail: str | None = None


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    components: dict[str, ComponentStatus]


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description=(
        "Returns operational status of the application and all dependent services. "
        "Status values: 'healthy' | 'degraded' | 'unhealthy'"
    ),
)
async def health_check() -> HealthResponse:
    """
    Public health check endpoint.

    Component checks:
        - app:          Always healthy if this endpoint responds.
        - insightforge: Verifies InsightForge adapter can report status.

    Full component checks (database, redis) added in Phase 2
    when those connections are configured.
    """
    components: dict[str, ComponentStatus] = {}

    # Application
    components["app"] = ComponentStatus(status="healthy")

    # InsightForge
    components["insightforge"] = _check_insightforge()

    overall = _compute_overall_status(components)

    return HealthResponse(
        status=overall,
        version="1.0.0",
        environment=settings.APP_ENV,
        components=components,
    )


def _check_insightforge() -> ComponentStatus:
    """
    Attempt to get InsightForge health status.
    Returns degraded (not unhealthy) because InsightForge loads lazily.
    """
    try:
        from insightforge.engine import InsightForgeEngine

        engine = InsightForgeEngine()
        info = engine.health_check()
        return ComponentStatus(
            status="healthy",
            detail=f"model={info.get('llm_model', 'unknown')}",
        )
    except Exception as exc:
        logger.warning("InsightForge health check failed", extra={"error": str(exc)})
        return ComponentStatus(
            status="degraded",
            detail=str(exc)[:200],
        )


def _compute_overall_status(components: dict[str, ComponentStatus]) -> str:
    """
    Compute overall status from component statuses.
    'unhealthy' if any critical component is unhealthy.
    'degraded'  if any component is degraded.
    'healthy'   otherwise.
    """
    statuses = {c.status for c in components.values()}
    if "unhealthy" in statuses:
        return "unhealthy"
    if "degraded" in statuses:
        return "degraded"
    return "healthy"
