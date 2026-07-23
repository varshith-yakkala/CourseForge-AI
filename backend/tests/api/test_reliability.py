import os
import pytest

os.environ["APP_SECRET_KEY"] = "x" * 32
os.environ["JWT_SECRET_KEY"] = "y" * 32
os.environ["GROQ_API_KEY"] = "valid_groq_api_key_here"

from fastapi.testclient import TestClient
from main import app

client = TestClient(app, raise_server_exceptions=False)

def test_request_validation_error_format():
    """Test that RequestValidationError is caught and formatted to the standard schema."""
    # Sending invalid data to login to trigger a validation error (missing password)
    response = client.post("/api/v1/auth/login", json={"email": "invalid"})
    
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"
    assert "detail" in data
    assert isinstance(data["errors"], list)
    
    # Check that error structure matches the mapped schema
    first_error = data["errors"][0]
    assert "loc" in first_error
    assert "msg" in first_error
    assert "type" in first_error

def test_unhandled_exception_format():
    """Test that generic exceptions are caught and formatted."""
    # Temporarily add a breaking route
    @app.get("/api/v1/health/break")
    async def break_route():
        raise Exception("This is an unhandled exception")
    
    response = client.get("/api/v1/health/break")
    assert response.status_code == 500
    data = response.json()
    assert data["code"] == "INTERNAL_ERROR"
    assert "An unexpected error occurred" in data["detail"]
    assert "This is an unhandled exception" not in data["detail"] # Do not leak internal error message
