"""
CourseForge AI - Shared FastAPI Dependencies

This module provides reusable dependency functions injected via FastAPI's
Dependency Injection system.

Usage in route handlers:
    from api.deps import get_db, get_current_user

    @router.get("/example")
    async def example(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        ...
"""

import logging
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.config import settings
from db.models.user import User
from core.exceptions import UnauthorizedError

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async database session dependency.
    Yields an AsyncSession and ensures it is closed after the request.
    """
    from db.session import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def get_current_user(
    request: Request, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    """
    JWT authentication dependency.
    Decodes the Bearer token from Authorization header and returns the user.
    """
    credentials_exception = UnauthorizedError(detail="Invalid authentication credentials")
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"],
            options={"verify_exp": True, "leeway": 10}
        )
        user_id: str | None = payload.get("sub")
        token_type: str | None = payload.get("type")
        if user_id is None or token_type != "access":
            logger.warning("Invalid JWT payload: missing sub or incorrect token type", extra={"request_id": request.headers.get("X-Request-ID"), "method": request.method, "path": request.url.path})
            raise credentials_exception
    except JWTError as e:
        logger.warning("JWT validation failed: %s", str(e), extra={"request_id": request.headers.get("X-Request-ID"), "method": request.method, "path": request.url.path})
        raise credentials_exception

    stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Like get_current_user but also verifies user is active (not deleted/banned).
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

