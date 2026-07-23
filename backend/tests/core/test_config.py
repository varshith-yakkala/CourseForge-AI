import os
import pytest
from pydantic import ValidationError

os.environ["APP_SECRET_KEY"] = "x" * 32
os.environ["JWT_SECRET_KEY"] = "y" * 32
os.environ["GROQ_API_KEY"] = "valid_groq_api_key_here"

from core.config import Settings


def test_missing_required_secrets(monkeypatch):
    """Test that missing required secrets raises ValidationError."""
    monkeypatch.delenv("APP_SECRET_KEY", raising=False)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    
    with pytest.raises(ValidationError) as exc:
        Settings()
    
    errors = str(exc.value)
    assert "app_secret_key" in errors.lower()
    assert "jwt_secret_key" in errors.lower()
    assert "groq_api_key" in errors.lower()


def test_weak_placeholder_secrets(monkeypatch):
    """Test that weak placeholder secrets are rejected."""
    weak_secrets = ["change_me", "password", "secret", "123456", "production_secret", "example_key"]
    for secret in weak_secrets:
        monkeypatch.setenv("APP_SECRET_KEY", secret)
        monkeypatch.setenv("JWT_SECRET_KEY", "x" * 32)
        monkeypatch.setenv("GROQ_API_KEY", "valid_groq_api_key_here")
        with pytest.raises(ValidationError) as exc:
            Settings()
        assert "uses a weak or placeholder value" in str(exc.value)
        
        monkeypatch.setenv("APP_SECRET_KEY", "x" * 32)
        monkeypatch.setenv("JWT_SECRET_KEY", "y" * 32)
        monkeypatch.setenv("GROQ_API_KEY", "valid_groq_api_key_here")
        monkeypatch.setenv("POSTGRES_PASSWORD", secret)
        with pytest.raises(ValidationError) as exc_db:
            Settings()
        assert "uses a weak or placeholder value" in str(exc_db.value)


def test_short_secrets(monkeypatch):
    """Test that secrets must be at least 32 characters."""
    monkeypatch.setenv("APP_SECRET_KEY", "short_key_123")
    monkeypatch.setenv("JWT_SECRET_KEY", "x" * 32)
    monkeypatch.setenv("GROQ_API_KEY", "valid_groq_api_key_here")
    with pytest.raises(ValidationError) as exc:
        Settings()
    assert "at least 32 characters long" in str(exc.value)


def test_negative_numeric_values(monkeypatch):
    """Test that numeric values must be positive."""
    monkeypatch.setenv("APP_SECRET_KEY", "x" * 32)
    monkeypatch.setenv("JWT_SECRET_KEY", "y" * 32)
    monkeypatch.setenv("GROQ_API_KEY", "valid_groq_api_key_here")
    monkeypatch.setenv("APP_PORT", "-8000")
    with pytest.raises(ValidationError) as exc:
        Settings()
    assert "Input should be greater than 0" in str(exc.value)
    
    monkeypatch.setenv("APP_PORT", "8000")
    monkeypatch.setenv("MAX_UPLOAD_SIZE_MB", "0")
    with pytest.raises(ValidationError) as exc2:
        Settings()
    assert "Input should be greater than 0" in str(exc2.value)


def test_production_safety_rules_debug_docs(monkeypatch):
    """Test that APP_DEBUG and ENABLE_DOCS must be False in production."""
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("APP_SECRET_KEY", "x" * 32)
    monkeypatch.setenv("JWT_SECRET_KEY", "y" * 32)
    monkeypatch.setenv("GROQ_API_KEY", "valid_groq_api_key_here")
    monkeypatch.setenv("APP_DEBUG", "true")
    monkeypatch.setenv("ENABLE_DOCS", "false")
    monkeypatch.setenv("CORS_ORIGINS", "https://example.com")
    with pytest.raises(ValidationError) as exc:
        Settings()
    assert "APP_DEBUG must be False in production" in str(exc.value)

    monkeypatch.setenv("APP_DEBUG", "false")
    monkeypatch.setenv("ENABLE_DOCS", "true")
    with pytest.raises(ValidationError) as exc2:
        Settings()
    assert "ENABLE_DOCS must be False in production" in str(exc2.value)


def test_production_safety_rules_cors(monkeypatch):
    """Test that localhost CORS is rejected in production."""
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("APP_SECRET_KEY", "x" * 32)
    monkeypatch.setenv("JWT_SECRET_KEY", "y" * 32)
    monkeypatch.setenv("GROQ_API_KEY", "valid_groq_api_key_here")
    monkeypatch.setenv("APP_DEBUG", "false")
    monkeypatch.setenv("ENABLE_DOCS", "false")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000,https://example.com")
    with pytest.raises(ValidationError) as exc:
        Settings()
    assert "is not allowed in production" in str(exc.value)


def test_environment_consistency_redis(monkeypatch):
    """Test that Redis must be configured if Celery timeouts > 0."""
    monkeypatch.setenv("APP_SECRET_KEY", "x" * 32)
    monkeypatch.setenv("JWT_SECRET_KEY", "y" * 32)
    monkeypatch.setenv("GROQ_API_KEY", "valid_groq_api_key_here")
    monkeypatch.setenv("CELERY_TASK_TIMEOUT_SECONDS", "600")
    monkeypatch.setenv("REDIS_HOST", "")
    with pytest.raises(ValidationError) as exc:
        Settings()
    assert "Celery requires REDIS_HOST" in str(exc.value)


def test_startup_report_valid_config(monkeypatch):
    """Test that a valid config produces the correct startup report."""
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("APP_SECRET_KEY", "x" * 32)
    monkeypatch.setenv("JWT_SECRET_KEY", "y" * 32)
    monkeypatch.setenv("GROQ_API_KEY", "valid_groq_api_key_here")
    monkeypatch.setenv("APP_DEBUG", "false")
    monkeypatch.setenv("ENABLE_DOCS", "false")
    monkeypatch.setenv("CORS_ORIGINS", "https://example.com")
    
    settings = Settings()
    report = settings.get_startup_report()
    assert report["Application Environment"] == "production"
    assert report["Configuration Loaded"] == "Successfully"
    assert report["Debug Mode"] == "False"
    assert report["Docs"] == "Disabled"
    # Ensure no secrets are in the report
    for v in report.values():
        assert "x"*32 not in str(v)
        assert "y"*32 not in str(v)
        assert "valid_groq_api_key_here" not in str(v)
