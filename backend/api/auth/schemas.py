"""Auth request/response Pydantic schemas."""
from datetime import datetime
import uuid
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2, max_length=255)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    avatar_url: str | None = None
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenRefresh(BaseModel):
    refresh_token: str


class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    avatar_url: str | None = None

