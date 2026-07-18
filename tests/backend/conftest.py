"""
CourseForge AI — Pytest Global Configuration

This conftest.py is loaded automatically by pytest for all test files.

Provides:
    - Shared fixtures available to all tests
    - Application settings override for test environment
    - Async event loop configuration
    - Test database fixtures (Phase 2)
    - Test client fixtures

Usage in test files:
    def test_something(app_client, settings_override):
        response = app_client.get("/api/v1/health")
        assert response.status_code == 200
"""

from __future__ import annotations

import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient


# ─────────────────────────────────────────────
# Test environment overrides
# Set BEFORE importing the application so Settings picks them up.
# ─────────────────────────────────────────────
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("APP_SECRET_KEY", "test-secret-key-at-least-32-chars-long-for-testing")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-key-at-least-32-chars-long-for-testing")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PASSWORD", "test_password")
os.environ.setdefault("INSIGHTFORGE_PATH", str(
    # Use a relative stub path in tests to avoid requiring the real InsightForge
    # Phase 2: Use a real test instance or mock
    os.path.join(os.path.dirname(__file__), "stubs", "insightforge")
))
os.environ.setdefault("GROQ_API_KEY", "test-groq-api-key")
os.environ.setdefault("LOG_FORMAT", "text")
os.environ.setdefault("LOG_LEVEL", "DEBUG")


@pytest.fixture(scope="session")
def app():
    """
    Create the FastAPI application for testing.

    Scope: session — one app instance for all tests in the session.
    This avoids the cost of re-creating and re-configuring the app per test.
    """
    from main import app as fastapi_app
    return fastapi_app


@pytest.fixture(scope="session")
def app_client(app) -> Generator:
    """
    Synchronous HTTP test client for the FastAPI application.

    Use for testing API endpoints that don't require async.
    Scope: session — shared across all tests.

    Example:
        def test_health(app_client):
            response = app_client.get("/api/v1/health")
            assert response.status_code == 200
    """
    with TestClient(app, raise_server_exceptions=True) as client:
        yield client


@pytest.fixture(autouse=True)
def reset_state():
    """
    Auto-used fixture that runs before every test.
    Resets any global state that could bleed between tests.
    Phase 2: Add database transaction rollback here.
    """
    yield
    # Teardown: nothing to reset in Phase 1


@pytest.fixture
def sample_pdf_path(tmp_path) -> str:
    """
    Create a minimal valid PDF file for upload tests.

    Returns:
        Absolute path to a temporary PDF file.
    """
    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\n"
        b"xref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n"
        b"0000000115 00000 n\ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n190\n%%EOF"
    )
    pdf_file = tmp_path / "test_document.pdf"
    pdf_file.write_bytes(pdf_content)
    return str(pdf_file)
