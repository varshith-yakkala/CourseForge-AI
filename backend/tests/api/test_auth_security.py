import os
import pytest

os.environ["APP_SECRET_KEY"] = "x" * 32
os.environ["JWT_SECRET_KEY"] = "y" * 32
os.environ["GROQ_API_KEY"] = "valid_groq_api_key_here"

from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
from jose import jwt

from main import app
from core.config import settings
from db.models.user import User
from core.security import create_access_token
from api.deps import get_db

client = TestClient(app)

from unittest.mock import AsyncMock
class MockResult:
    def scalar_one_or_none(self):
        return None

async def override_get_db():
    mock_db = AsyncMock()
    mock_db.execute.return_value = MockResult()
    yield mock_db

app.dependency_overrides[get_db] = override_get_db

def test_missing_jwt():
    """Test accessing a protected endpoint without a token."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_invalid_jwt():
    """Test accessing a protected endpoint with an invalid token."""
    headers = {"Authorization": "Bearer invalid.token.here"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"
    assert response.json()["code"] == "UNAUTHORIZED"

def test_expired_jwt():
    """Test accessing a protected endpoint with an expired token."""
    # Create an expired token
    expire = datetime.now(timezone.utc) - timedelta(minutes=10)
    to_encode = {"exp": expire, "sub": "123e4567-e89b-12d3-a456-426614174000", "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")
    
    headers = {"Authorization": f"Bearer {encoded_jwt}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"
    assert response.json()["code"] == "UNAUTHORIZED"

def test_missing_claims_jwt():
    """Test accessing a protected endpoint with a token missing 'sub' or 'type'."""
    # Missing 'sub'
    expire = datetime.now(timezone.utc) + timedelta(minutes=10)
    to_encode = {"exp": expire, "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")
    
    headers = {"Authorization": f"Bearer {encoded_jwt}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"
    assert response.json()["code"] == "UNAUTHORIZED"

    # Wrong type
    to_encode = {"exp": expire, "sub": "123e4567-e89b-12d3-a456-426614174000", "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")
    
    headers = {"Authorization": f"Bearer {encoded_jwt}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"
    assert response.json()["code"] == "UNAUTHORIZED"

def test_invalid_login():
    """Test logging in with invalid credentials."""
    response = client.post("/api/v1/auth/login", json={"email": "nonexistent@example.com", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"
