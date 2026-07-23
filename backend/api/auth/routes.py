"""Auth routes."""
import logging
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.deps import get_current_active_user, get_db
from api.auth.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    TokenRefresh,
    ChangePassword,
    UserUpdate,
)
from core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from core.rate_limit import limiter
from db.models.user import User
from jose import JWTError, jwt
from core.config import settings
from core.exceptions import UnauthorizedError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
    response: Response,
    user_in: UserCreate, db: AsyncSession = Depends(get_db)
) -> Any:
    """Register a new user."""
    stmt = select(User).where(User.email == user_in.email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        logger.warning(
            "Registration failed: Email %s already exists", user_in.email,
            extra={"request_id": request.headers.get("X-Request-ID"), "method": request.method, "path": request.url.path}
        )
        raise HTTPException(
            status_code=409,
            detail="A user with this email already exists.",
        )
    
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(
    request: Request,
    response: Response,
    login_data: UserLogin, db: AsyncSession = Depends(get_db)
) -> Any:
    """Login and get access and refresh tokens."""
    stmt = select(User).where(User.email == login_data.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        client_ip = request.headers.get("X-Forwarded-For", getattr(request.client, "host", "unknown"))
        logger.warning(
            "Login failed for email %s from IP %s", login_data.email, client_ip,
            extra={"request_id": request.headers.get("X-Request-ID"), "method": request.method, "path": request.url.path}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        logger.warning(
            "Login failed: User %s is inactive", user.id,
            extra={"request_id": request.headers.get("X-Request-ID"), "method": request.method, "path": request.url.path}
        )
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user,
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request, data: TokenRefresh, db: AsyncSession = Depends(get_db)
) -> Any:
    """Refresh an access token."""
    credentials_exception = UnauthorizedError(detail="Invalid authentication credentials")
    try:
        payload = jwt.decode(
            data.refresh_token, 
            settings.JWT_SECRET_KEY, 
            algorithms=["HS256"],
            options={"verify_exp": True, "leeway": 10}
        )
        user_id = payload.get("sub")
        token_type = payload.get("type")
        if user_id is None or token_type != "refresh":
            logger.warning("Invalid refresh token payload", extra={"request_id": request.headers.get("X-Request-ID"), "method": request.method, "path": request.url.path})
            raise credentials_exception
    except JWTError as e:
        logger.warning("Refresh token validation failed: %s", str(e), extra={"request_id": request.headers.get("X-Request-ID"), "method": request.method, "path": request.url.path})
        raise credentials_exception
        
    stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise credentials_exception
        
    access_token = create_access_token(subject=user.id)
    new_refresh_token = create_refresh_token(subject=user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user,
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Logout (client discards token). Server-side blacklist can be added here if needed."""
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def read_current_user(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get current user."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update current user profile."""
    if update_data.full_name is not None:
        current_user.full_name = update_data.full_name
    if update_data.avatar_url is not None:
        current_user.avatar_url = update_data.avatar_url
        
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.post("/change-password")
async def change_password(
    request: Request,
    data: ChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Change current user password."""
    if not verify_password(data.current_password, current_user.hashed_password):
        logger.warning(
            "Password change failed for user %s: incorrect current password", current_user.id,
            extra={"request_id": request.headers.get("X-Request-ID"), "method": request.method, "path": request.url.path}
        )
        raise HTTPException(status_code=400, detail="Incorrect password")
        
    current_user.hashed_password = get_password_hash(data.new_password)
    db.add(current_user)
    await db.commit()
    return {"message": "Password changed successfully"}
