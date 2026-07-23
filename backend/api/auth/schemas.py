"""Auth request/response Pydantic schemas."""
from datetime import datetime
import uuid
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="The user's email address")
    password: str = Field(..., min_length=8, description="Strong password (min 8 characters)")
    full_name: str = Field(..., min_length=2, max_length=255, description="The user's full name")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "jane@example.com",
                "password": "strongpassword123",
                "full_name": "Jane Doe"
            }
        }
    )


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="The user's email address")
    password: str = Field(..., description="The user's password")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "jane@example.com",
                "password": "strongpassword123"
            }
        }
    )


class UserResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Unique identifier for the user")
    email: EmailStr = Field(..., description="The user's email address")
    full_name: str = Field(..., description="The user's full name")
    avatar_url: str | None = Field(default=None, description="URL to the user's avatar image")
    role: str = Field(..., description="User role (e.g. 'user', 'admin')")
    is_active: bool = Field(..., description="Whether the user account is active")
    is_verified: bool = Field(..., description="Whether the user's email is verified")
    created_at: datetime = Field(..., description="Timestamp of account creation")
    updated_at: datetime = Field(..., description="Timestamp of last update")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "jane@example.com",
                "full_name": "Jane Doe",
                "avatar_url": "https://example.com/avatar.jpg",
                "role": "user",
                "is_active": True,
                "is_verified": False,
                "created_at": "2026-07-23T00:00:00Z",
                "updated_at": "2026-07-23T00:00:00Z"
            }
        }
    )


class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Type of token")
    expires_in: int = Field(..., description="Token expiration in seconds")
    user: UserResponse = Field(..., description="User profile data")


class TokenRefresh(BaseModel):
    refresh_token: str = Field(..., description="A valid JWT refresh token")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )


class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255, description="New full name")
    avatar_url: str | None = Field(default=None, description="New avatar URL")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "Jane Smith",
                "avatar_url": "https://example.com/new-avatar.jpg"
            }
        }
    )

