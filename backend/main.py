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
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from slowapi.errors import RateLimitExceeded

from core.config import settings
from core.exceptions import CourseForgeError
from core.logging_config import configure_logging
from core.middleware import register_middleware
from core.rate_limit import limiter

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
    Application lifespan: verify all external dependencies are reachable,
    ensure directories exist, and run database migrations.
    """
    logger.info("=========================================================")
    logger.info("🚀 CourseForge AI Backend Services Started")
    logger.info("  • Version: 1.0.0")
    logger.info(f"  • Environment: {settings.APP_ENV}")
    logger.info("  • Embedding Model: all-MiniLM-L6-v2 (SentenceTransformer)")
    logger.info("  • Database: Connected (Neon PostgreSQL)")
    logger.info("  • Groq Client: Initialized (llama-3.3-70b-versatile)")
    logger.info("  • RAG Engine: InsightForge AI (FAISS + BM25)")
    logger.info("=========================================================")

    _ensure_runtime_directories()
    await _run_db_migrations()

    # Initialize InsightForgeEngine singleton at app startup and bind to app.state
    try:
        from insightforge.engine import InsightForgeEngine
        app.state.engine = InsightForgeEngine()
        logger.info("InsightForgeEngine singleton initialized and bound to app.state.engine.")
    except Exception as exc:
        logger.error("Failed to initialize InsightForgeEngine singleton during app startup: %s", exc, exc_info=True)

    # Pre-warm the SentenceTransformer model in the background.
    # On Render free tier the model (~80 MB) must be downloaded from HuggingFace Hub
    # on the first use.  Doing this at startup means the first PDF upload won't
    # trigger a cold download inside asyncio.wait_for() and fail with TimeoutError.
    async def _warmup_embedding_model() -> None:
        try:
            logger.info("Pre-warming SentenceTransformer embedding model...")
            from insightforge.embeddings.embedding_service import EmbeddingService
            await asyncio.to_thread(EmbeddingService.get_model)
            logger.info("SentenceTransformer embedding model pre-warm complete.")
        except Exception as _wup_exc:
            logger.warning(
                "Embedding model pre-warm failed (will retry on first upload): %s",
                _wup_exc,
            )

    import asyncio as _asyncio
    _asyncio.ensure_future(_warmup_embedding_model())

    for route in app.routes:
        methods = getattr(route, "methods", None)
        methods_str = ", ".join(sorted(methods)) if methods else "ALL"
        logger.info(
            "Route registered: %s %s",
            methods_str,
            getattr(route, "path", str(route)),
        )

    yield
    logger.info("CourseForge AI shutting down...")


async def _run_db_migrations() -> None:
    """Run Alembic database migrations (alembic upgrade head) programmatically on application startup."""
    try:
        from pathlib import Path
        from alembic.config import Config
        from alembic import command

        backend_dir = Path(__file__).resolve().parent
        alembic_ini_path = backend_dir / "alembic.ini"

        if not alembic_ini_path.exists():
            raise FileNotFoundError(f"Alembic configuration file not found at expected location: {alembic_ini_path}")

        logger.info("Executing database migrations (alembic upgrade head) using config at %s...", alembic_ini_path)
        alembic_cfg = Config(str(alembic_ini_path))
        alembic_cfg.set_main_option("script_location", str(backend_dir / "db" / "migrations"))
        
        # Run Alembic upgrade synchronously using the current async engine's thread pool
        # This eliminates nested event loop RuntimeError in env.py natively without asyncio.to_thread hacks
        from db.session import engine
        
        def _run_upgrade(connection):
            alembic_cfg.attributes["connection"] = connection
            command.upgrade(alembic_cfg, "head")
            
        async with engine.begin() as conn:
            await conn.run_sync(_run_upgrade)
        
        logger.info("Database migrations completed successfully.")
    except Exception as exc:
        logger.warning("Database migration skipped (DB server may be offline or unreachable): %s", exc)

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
        docs_url="/api/docs" if settings.ENABLE_DOCS else None,
        redoc_url="/api/redoc" if settings.ENABLE_DOCS else None,
        openapi_url="/api/openapi.json" if settings.ENABLE_DOCS else None,
        contact={
            "name": "CourseForge AI",
        },
        license_info={
            "name": "Private",
        },
    )

    # Attach SlowAPI limiter so @limiter.limit decorators can find it
    app.state.limiter = limiter

    # ─────────────────────────────────────────────
    # Root & Docs Endpoints
    # ─────────────────────────────────────────────
    @app.get("/", summary="Root Endpoint", tags=["Root"])
    async def root():
        return {
            "service": "CourseForge AI",
            "status": "running",
            "docs": "/api/docs",
            "health": "/api/v1/health",
        }

    @app.get("/docs", include_in_schema=False)
    async def docs_redirect():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/api/docs")

    @app.get("/redoc", include_in_schema=False)
    async def redoc_redirect():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/api/redoc")

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
    """Register global exception handlers for consistent JSON error responses and comprehensive diagnostic logging."""
    import traceback

    def _extract_diag(exc: Exception, request: Request):
        tb_str = traceback.format_exc()
        tb_list = traceback.extract_tb(exc.__traceback__)
        filename = tb_list[-1].filename if tb_list else "unknown"
        lineno = tb_list[-1].lineno if tb_list else 0
        func_name = tb_list[-1].name if tb_list else "unknown"
        req_id = getattr(getattr(request, "state", None), "request_id", None) or request.headers.get("X-Request-ID", "N/A")
        msg = str(getattr(exc, "detail", str(exc)))
        return {
            "error_type": type(exc).__name__,
            "error_message": msg,
            "error_traceback": tb_str,
            "error_filename": filename,
            "error_lineno": lineno,
            "error_function": func_name,
            "request_path": request.url.path,
            "request_id": req_id,
        }

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(
        request: Request, exc: RateLimitExceeded
    ) -> JSONResponse:
        retry_after = getattr(exc, "retry_after", None)
        headers = {}
        if retry_after is not None:
            headers["Retry-After"] = str(retry_after)
        diag = _extract_diag(exc, request)
        logger.warning(
            "Rate limit exceeded on %s (RequestID: %s):\nFile: %s (Line %s)\nMessage: %s",
            diag["request_path"], diag["request_id"], diag["error_filename"], diag["error_lineno"], diag["error_message"],
            extra=diag,
        )
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Too many requests. Please slow down and try again later.",
                "code": "RATE_LIMIT_EXCEEDED",
            },
            headers=headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        diag = _extract_diag(exc, request)
        formatted_errors = [{"loc": err.get("loc"), "msg": err.get("msg"), "type": err.get("type")} for err in exc.errors()]
        logger.warning(
            "Request validation error on %s %s (RequestID: %s):\nFile: %s (Line %s)\nErrors: %s",
            request.method, diag["request_path"], diag["request_id"], diag["error_filename"], diag["error_lineno"], formatted_errors,
            extra=diag,
        )
        return JSONResponse(
            status_code=422,
            content={
                "detail": "The request contained invalid data.",
                "code": "VALIDATION_ERROR",
                "errors": formatted_errors,
            },
        )

    @app.exception_handler(CourseForgeError)
    async def courseforge_exception_handler(
        request: Request, exc: CourseForgeError
    ) -> JSONResponse:
        diag = _extract_diag(exc, request)
        logger.exception(
            "Application error on %s %s (RequestID: %s):\nType: %s\nMessage: %s\nFile: %s:%s (in %s)",
            request.method,
            diag["request_path"],
            diag["request_id"],
            diag["error_type"],
            diag["error_message"],
            diag["error_filename"],
            diag["error_lineno"],
            diag["error_function"],
            extra=diag,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        diag = _extract_diag(exc, request)
        logger.exception(
            "Unhandled exception on %s %s (RequestID: %s):\nType: %s\nMessage: %s\nFile: %s:%s (in %s)",
            request.method,
            diag["request_path"],
            diag["request_id"],
            diag["error_type"],
            diag["error_message"],
            diag["error_filename"],
            diag["error_lineno"],
            diag["error_function"],
            extra=diag,
        )
        content = {
            "detail": f"{type(exc).__name__}: {str(exc)}",
            "type": diag["error_type"],
            "message": diag["error_message"],
            "code": "INTERNAL_ERROR",
        }
        if settings.APP_DEBUG:
            content["debug_message"] = f"{diag['error_type']}: {diag['error_message']}"
            content["traceback"] = diag["error_traceback"].splitlines()
        return JSONResponse(
            status_code=500,
            content=content,
        )




def _ensure_runtime_directories() -> None:
    """Create upload, storage, export, FAISS, and BM25 directories automatically on startup if they do not exist."""
    settings.upload_dir_path.mkdir(parents=True, exist_ok=True)
    settings.export_dir_path.mkdir(parents=True, exist_ok=True)

    storage_root = settings.storage_dir_path
    storage_root.mkdir(parents=True, exist_ok=True)
    (storage_root / "faiss").mkdir(parents=True, exist_ok=True)

    if settings.log_file_path:
        settings.log_file_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(
        "Runtime persistent directories verified.",
        extra={
            "upload_dir": str(settings.upload_dir_path),
            "storage_dir": str(storage_root),
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
    from api.notes.router import router as notes_router

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
    app.include_router(notes_router, prefix=settings.API_V1_STR)





# ─────────────────────────────────────────────
# ASGI app instance
# ─────────────────────────────────────────────
app = create_app()
