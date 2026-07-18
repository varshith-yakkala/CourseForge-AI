"""Auth routes."""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
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
from db.models.user import User
from jose import JWTError, jwt
from core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate, db: AsyncSession = Depends(get_db)
) -> Any:
    """Register a new user."""
    stmt = select(User).where(User.email == user_in.email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
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
async def login(
    login_data: UserLogin, db: AsyncSession = Depends(get_db)
) -> Any:
    """Login and get access and refresh tokens."""
    stmt = select(User).where(User.email == login_data.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user,
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    data: TokenRefresh, db: AsyncSession = Depends(get_db)
) -> Any:
    """Refresh an access token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(data.refresh_token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        token_type = payload.get("type")
        if user_id is None or token_type != "refresh":
            raise credentials_exception
    except JWTError:
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
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
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
    data: ChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Change current user password."""
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
        
    current_user.hashed_password = get_password_hash(data.new_password)
    db.add(current_user)
    await db.commit()
    return {"message": "Password changed successfully"}
