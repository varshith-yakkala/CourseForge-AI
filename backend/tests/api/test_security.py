import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from main import app
from api.deps import get_db, get_current_user, get_current_active_user

from datetime import datetime, timezone

# Mock user for dependencies
mock_user = type("User", (), {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "test@example.com", 
    "is_active": True,
    "role": "student",
    "is_verified": True,
    "created_at": datetime.now(timezone.utc),
    "updated_at": datetime.now(timezone.utc)
})()

async def override_get_current_user():
    return mock_user

class MockResult:
    def __init__(self, scalar_val=None, scalars_val=None):
        self._scalar_val = scalar_val
        self._scalars_val = scalars_val or []
        
    def scalar_one_or_none(self):
        return self._scalar_val
        
    def scalars(self):
        class MockScalars:
            def __init__(self, val):
                self._val = val
            def all(self):
                return self._val
        return MockScalars(self._scalars_val)

async def override_get_db():
    mock_db = AsyncMock()
    mock_db.execute.return_value = MockResult()
    yield mock_db

# Override dependencies for test client
app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[get_current_active_user] = override_get_current_user
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_rate_limiting_auth_routes():
    """Test that auth routes are rate limited (e.g. 5/minute)."""
    user_data = {"email": "rate_limit_test@example.com", "password": "Password123!", "full_name": "Test"}
    
    # We override the app dependency for get_db temporarily for this test
    # to return a mock user so it raises 409
    async def get_db_override():
        mock_db = AsyncMock()
        mock_db.execute.return_value = MockResult(scalar_val=mock_user)
        yield mock_db
        
    app.dependency_overrides[get_db] = get_db_override
    
    try:
        # Hit 5 times (should return 409 Conflict)
        for _ in range(5):
            client.post("/api/v1/auth/register", json=user_data)
            
        # 6th hit should be rate limited 429
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 429
        assert "Too many requests" in response.json()["detail"]
    finally:
        # Restore default override
        app.dependency_overrides[get_db] = override_get_db

def test_upload_magic_byte_validation():
    """Test that uploads without PDF magic bytes are rejected."""
    # We override get_db to return a mock course then None for document
    async def get_db_course_override():
        mock_db = AsyncMock()
        mock_db.execute.side_effect = [
            MockResult(scalar_val=type("Course", (), {"id": "c"})()),
            MockResult(scalar_val=None)
        ]
        yield mock_db
        
    app.dependency_overrides[get_db] = get_db_course_override
    
    try:
        response = client.post(
            "/api/v1/documents/upload",
            data={"course_id": "123e4567-e89b-12d3-a456-426614174000"},
            files={"file": ("test.pdf", b"NOT A PDF FILE", "application/pdf")}
        )
        assert response.status_code == 415
        assert "not appear to be a valid PDF" in response.json()["detail"]
    finally:
        app.dependency_overrides[get_db] = override_get_db

def test_upload_file_size_validation():
    """Test that uploads exceeding the size limit are rejected."""
    # Generate 11MB of data (limit is 10MB)
    large_data = b"%PDF-1.4\n" + b"0" * (11 * 1024 * 1024)
    
    # We override get_db to return a mock course then None for document
    async def get_db_course_override():
        mock_db = AsyncMock()
        mock_db.execute.side_effect = [
            MockResult(scalar_val=type("Course", (), {"id": "c"})()),
            MockResult(scalar_val=None)
        ]
        yield mock_db
        
    app.dependency_overrides[get_db] = get_db_course_override
    
    try:
        response = client.post(
            "/api/v1/documents/upload",
            data={"course_id": "123e4567-e89b-12d3-a456-426614174000"},
            files={"file": ("large.pdf", large_data, "application/pdf")}
        )
        assert response.status_code == 413
        assert "File too large" in response.json()["detail"]
    finally:
        app.dependency_overrides[get_db] = override_get_db

def test_search_error_leakage():
    """Test that generic exceptions in search route do not leak internal details."""
    # We override get_db to return a valid document so it doesn't short-circuit
    async def get_db_docs_override():
        mock_db = AsyncMock()
        mock_doc = type("Document", (), {"insightforge_doc_id": "doc123"})()
        mock_db.execute.return_value = MockResult(scalars_val=[mock_doc])
        yield mock_db
        
    app.dependency_overrides[get_db] = get_db_docs_override
    
    with patch("api.search.routes.InsightForgeEngine.retrieve_chunks") as mock_retrieve:
        mock_retrieve.side_effect = Exception("Database connection string leaked: postgres://admin:secret@host")
        
        try:
            response = client.post("/api/v1/search", json={"query": "test"})
            
            assert response.status_code == 500
            assert "Database connection string leaked" not in response.json()["detail"]
            assert "Search is temporarily unavailable" in response.json()["detail"]
        finally:
            app.dependency_overrides[get_db] = override_get_db
