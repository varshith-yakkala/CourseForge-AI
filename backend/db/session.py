"""
CourseForge AI — Database Session Factory

Provides:
    - AsyncEngine: SQLAlchemy async engine (one per process)
    - AsyncSessionLocal: Session factory for all database operations
    - get_db(): FastAPI dependency that yields a managed session per request

Usage in FastAPI routes (via dependency injection):
    from api.deps import get_db  # wraps this module
    from sqlalchemy.ext.asyncio import AsyncSession

    @router.get("/example")
    async def example(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(User).where(User.id == user_id))
        ...

Design:
    - One engine per process (created at module import)
    - One session per request (created by get_db() dependency)
    - Sessions are always closed — even on exceptions — via try/finally
    - Commit is the caller's responsibility (not auto-committed)
"""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.config import settings

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Engine — one per application process
# ─────────────────────────────────────────────
engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=settings.APP_DEBUG,            # Log all SQL in debug mode
    pool_size=3,                        # Connections kept open in pool (lower for Render/Neon scaling)
    max_overflow=5,                     # Extra connections allowed above pool_size
    pool_timeout=30,                    # Seconds to wait before giving up on getting a connection
    pool_pre_ping=True,                 # Validate connection before use (avoids stale connections)
    pool_recycle=1800,                  # Recycle connections after 30 minutes
)

# ─────────────────────────────────────────────
# Session factory — produces per-request sessions
# ─────────────────────────────────────────────
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit (allows access post-commit)
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:  # type: ignore[return]
    """
    FastAPI dependency that provides a database session for a single request.

    Yields:
        AsyncSession: An active database session.

    Guarantees:
        - Session is always closed after the request (via finally block).
        - Caller is responsible for commit/rollback.
        - On unhandled exception, session is rolled back before close.

    Usage:
        @router.get("/example")
        async def example(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_db_session() -> AsyncSession:
    """
    Return a new database session context manager.

    Usage in Celery tasks:
        async with get_db_session() as session:
            ...
    """
    return AsyncSessionLocal()
