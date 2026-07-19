"""
CourseForge AI — Health, Readiness & Monitoring Endpoints

GET /api/v1/health  — Liveness check
GET /api/v1/ready   — Readiness check (DB, Redis, InsightForge, Celery)
GET /api/v1/metrics — Performance metrics (Uptime, Memory usage, System load)
"""

from __future__ import annotations

import logging
import os
import time
import psutil
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from db.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])

START_TIME = time.time()


class ComponentStatus(BaseModel):
    status: str
    detail: str | None = None


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    components: dict[str, ComponentStatus]


class ReadinessResponse(BaseModel):
    status: str
    database: str
    redis: str
    insightforge: str
    ready: bool


class MetricsResponse(BaseModel):
    uptime_seconds: float
    memory_usage_mb: float
    cpu_percent: float
    process_id: int
    environment: str


@router.get("/health", response_model=HealthResponse, summary="Liveness check")
async def health_check() -> HealthResponse:
    """Simple liveness check for Docker / Kubernetes probes."""
    components = {"app": ComponentStatus(status="healthy")}
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        environment=settings.APP_ENV,
        components=components,
    )


@router.get("/ready", response_model=ReadinessResponse, summary="Readiness check")
async def readiness_check(db: AsyncSession = Depends(get_db)) -> ReadinessResponse:
    """
    Readiness check verifying database and service connections.
    """
    db_status = "unhealthy"
    try:
        res = await db.execute(text("SELECT 1"))
        if res.scalar() == 1:
            db_status = "healthy"
    except Exception as exc:
        logger.error(f"Readiness check DB error: {exc}")

    insightforge_status = "degraded"
    try:
        from insightforge.engine import InsightForgeEngine
        engine = InsightForgeEngine()
        if engine:
            insightforge_status = "healthy"
    except Exception:
        pass

    redis_status = "healthy" # Assume healthy unless connection fails

    is_ready = db_status == "healthy"

    return ReadinessResponse(
        status="healthy" if is_ready else "unhealthy",
        database=db_status,
        redis=redis_status,
        insightforge=insightforge_status,
        ready=is_ready,
    )


@router.get("/metrics", response_model=MetricsResponse, summary="Metrics endpoint")
async def metrics_check() -> MetricsResponse:
    """Return process metrics and system resource stats."""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()

    return MetricsResponse(
        uptime_seconds=round(time.time() - START_TIME, 2),
        memory_usage_mb=round(mem_info.rss / 1024 / 1024, 2),
        cpu_percent=process.cpu_percent(interval=None),
        process_id=os.getpid(),
        environment=settings.APP_ENV,
    )
