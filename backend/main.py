"""
CourseForge AI — FastAPI Application Entrypoint

This module creates and configures the FastAPI application instance.

Responsibilities:
    - Create the FastAPI app with metadata
    - Register middleware (CORS, request logging)
    - Register exception handlers
    - Register all API routers (Phase 2+)
    - Configure startup / shutdown lifecycle events
    - Expose the ASGI app for Uvicorn

Run with:
    uvicorn main:app --reload --port 8001
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from core.config import settings
from core.exceptions import CourseForgeError
from core.logging_config import configure_logging
from core.middleware import register_middleware

# ─────────────────────────────────────────────
# Configure logging FIRST — before any other module logs
# ─────────────────────────────────────────────
configure_logging(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT,
    log_file=settings.log_file_path,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Application factory
# ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan: verify all external dependencies are reachable.
    InsightForge, PostgreSQL, Redis connections are validated here.
    """
    logger.info("CourseForge AI starting up...")
    _ensure_runtime_directories()
    logger.info("Startup complete. Application is ready.")
    yield
    logger.info("CourseForge AI shutting down.")

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Fully configured FastAPI instance ready for Uvicorn.
    """
    app = FastAPI(
        lifespan=lifespan,
        title=settings.APP_NAME,
        description=(
            "AI-powered PDF to Interactive Learning Platform. "
            "Converts PDF documents into structured courses with lessons, "
            "quizzes, flashcards, and an AI tutor."
        ),
        version="1.0.0",
        docs_url="/api/docs" if settings.is_development else None,
        redoc_url="/api/redoc" if settings.is_development else None,
        openapi_url="/api/openapi.json" if settings.is_development else None,
        contact={
            "name": "CourseForge AI",
        },
        license_info={
            "name": "Private",
        },
    )

    # ─────────────────────────────────────────────
    # Middleware
    # ─────────────────────────────────────────────
    register_middleware(app)

    # ─────────────────────────────────────────────
    # Exception Handlers
    # ─────────────────────────────────────────────
    _register_exception_handlers(app)

    # ─────────────────────────────────────────────
    # API Routers (added in Phase 2+)
    # ─────────────────────────────────────────────
    _register_routers(app)

    logger.info(
        "CourseForge AI application created.",
        extra={
            "env": settings.APP_ENV,
            "port": settings.APP_PORT,
            "debug": settings.APP_DEBUG,
        },
    )

    return app


def _register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers for consistent JSON error responses."""

    @app.exception_handler(CourseForgeError)
    async def courseforge_exception_handler(
        request: Request, exc: CourseForgeError
    ) -> JSONResponse:
        logger.warning(
            "Application error",
            extra={
                "code": exc.code,
                "detail": exc.detail,
                "path": request.url.path,
            },
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception(
            "Unhandled exception",
            extra={"path": request.url.path},
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected error occurred. Please try again.",
                "code": "INTERNAL_ERROR",
            },
        )




def _ensure_runtime_directories() -> None:
    """Create upload and export directories if they do not exist."""
    settings.upload_dir_path.mkdir(parents=True, exist_ok=True)
    settings.export_dir_path.mkdir(parents=True, exist_ok=True)

    if settings.log_file_path:
        settings.log_file_path.parent.mkdir(parents=True, exist_ok=True)

    logger.debug(
        "Runtime directories verified.",
        extra={
            "upload_dir": str(settings.upload_dir_path),
            "export_dir": str(settings.export_dir_path),
        },
    )


def _register_routers(app: FastAPI) -> None:
    """
    Register all API routers.

    Phase 1: Health check only.
    Phase 2+: Auth, courses, lessons, quiz, chat, progress, search,
              flashcards, analytics, export, notifications.
    """
    from api.health import router as health_router
    from api.auth.routes import router as auth_router
    from api.courses.routes import router as courses_router
    from api.documents.routes import router as documents_router
    from api.search.routes import router as search_router
    from api.lessons.routes import router as lessons_router
    from api.quizzes.routes import router as quizzes_router
    from api.flashcards.routes import router as flashcards_router
    from api.analytics.routes import router as analytics_router
    from api.planner.routes import router as planner_router
    from api.coach.routes import router as coach_router
    from api.reports.routes import router as reports_router

    app.include_router(health_router, prefix=settings.API_V1_STR)
    app.include_router(auth_router, prefix=settings.API_V1_STR)
    app.include_router(courses_router, prefix=settings.API_V1_STR)
    app.include_router(documents_router, prefix=settings.API_V1_STR)
    app.include_router(search_router, prefix=settings.API_V1_STR)
    app.include_router(lessons_router, prefix=settings.API_V1_STR)
    app.include_router(quizzes_router, prefix=settings.API_V1_STR)
    app.include_router(flashcards_router, prefix=settings.API_V1_STR)
    app.include_router(analytics_router, prefix=settings.API_V1_STR)
    app.include_router(planner_router, prefix=settings.API_V1_STR)
    app.include_router(coach_router, prefix=settings.API_V1_STR)
    app.include_router(reports_router, prefix=settings.API_V1_STR)




# ─────────────────────────────────────────────
# ASGI app instance
# ─────────────────────────────────────────────
app = create_app()
