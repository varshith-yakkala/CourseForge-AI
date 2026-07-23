"""
CourseForge AI — Backend Application Configuration

Loads all settings from environment variables using Pydantic Settings.
This is the single source of truth for all configuration values.
All application code imports settings from this module — never from os.environ directly.
"""

from __future__ import annotations

import difflib
import logging
import os
import sys
from pathlib import Path
from typing import Literal, Any

from pydantic import AnyUrl, field_validator, model_validator, Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("courseforge.config")



class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Pydantic Settings automatically reads from:
    1. Environment variables (highest priority)
    2. .env file (lower priority)
    3. Default values (lowest priority)
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─────────────────────────────────────────────
    # APPLICATION
    # ─────────────────────────────────────────────
    APP_NAME: str = "CourseForge AI"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    APP_DEBUG: bool = True
    APP_PORT: int = Field(default=8001, gt=0, validation_alias=AliasChoices("port", "app_port"))
    ENABLE_DOCS: bool = Field(default=True, validation_alias=AliasChoices("enable_docs"))
    APP_SECRET_KEY: str = Field(validation_alias=AliasChoices("app_secret_key", "secret_key"))
    API_V1_STR: str = "/api/v1"

    # ─────────────────────────────────────────────
    # DATABASE — PostgreSQL
    # ─────────────────────────────────────────────
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "courseforge"
    POSTGRES_USER: str = "courseforge_user"
    POSTGRES_PASSWORD: str = "courseforge_pass"

    # ─────────────────────────────────────────────
    # REDIS
    # ─────────────────────────────────────────────
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0

    # ─────────────────────────────────────────────
    # CELERY
    # ─────────────────────────────────────────────
    CELERY_TASK_TIMEOUT_SECONDS: int = Field(default=600, gt=0)
    CELERY_MAX_RETRIES: int = Field(default=3, ge=0)

    # ─────────────────────────────────────────────
    # JWT AUTHENTICATION
    # ─────────────────────────────────────────────
    JWT_SECRET_KEY: str = Field(validation_alias=AliasChoices("jwt_secret_key", "jwt_secret"))
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ─────────────────────────────────────────────
    # INSIGHTFORGE INTEGRATION
    # ─────────────────────────────────────────────
    INSIGHTFORGE_PATH: str | None = None

    # ─────────────────────────────────────────────
    # AI — GROQ
    # ─────────────────────────────────────────────
    GROQ_API_KEY: str = Field(min_length=10)
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_MAX_TOKENS: int = Field(default=2048, gt=0)
    GROQ_TEMPERATURE: float = Field(default=0.2, ge=0.0, le=2.0)
    GROQ_REQUEST_TIMEOUT_SECONDS: int = Field(default=60, gt=0)

    # ─────────────────────────────────────────────
    # AI — EMBEDDING
    # ─────────────────────────────────────────────
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # ─────────────────────────────────────────────
    # FILE STORAGE
    # ─────────────────────────────────────────────
    UPLOAD_DIR: str = "./uploads"
    EXPORT_DIR: str = "./exports"
    MAX_UPLOAD_SIZE_MB: int = Field(default=50, gt=0)
    ALLOWED_UPLOAD_EXTENSIONS: str = ".pdf,.txt,.md"

    # ─────────────────────────────────────────────
    # CORS
    # ─────────────────────────────────────────────
    CORS_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:3000,https://course-forge-ai.vercel.app",
        validation_alias=AliasChoices("cors_origins"),
    )
    CORS_ORIGIN_REGEX: str = Field(
        default=r"^https://course-forge(-[a-zA-Z0-9-]+)?\.vercel\.app$",
        validation_alias=AliasChoices("cors_origin_regex"),
    )
    CORS_ALLOW_CREDENTIALS: bool = True

    # ─────────────────────────────────────────────
    # LOGGING
    # ─────────────────────────────────────────────
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMAT: Literal["json", "text"] = "json"
    LOG_FILE: str = "./logs/courseforge.log"

    # ─────────────────────────────────────────────
    # RATE LIMITING
    # ─────────────────────────────────────────────
    RATE_LIMIT_CHAT_MESSAGES_PER_HOUR: int = Field(default=60, gt=0)
    RATE_LIMIT_UPLOAD_PER_DAY: int = Field(default=10, gt=0)

    # ─────────────────────────────────────────────
    # COURSE GENERATION
    # ─────────────────────────────────────────────
    COURSE_GEN_MAX_LESSONS: int = 20
    COURSE_GEN_MAX_TOPICS_PER_LESSON: int = 8
    COURSE_GEN_RETRIEVAL_TOP_K: int = 20
    COURSE_GEN_LLM_RETRIES: int = 3

    # ─────────────────────────────────────────────
    # QUIZ
    # ─────────────────────────────────────────────
    QUIZ_DEFAULT_PASS_SCORE_PCT: float = 70.0
    QUIZ_DEFAULT_MAX_ATTEMPTS: int = 3
    QUIZ_MCQ_PER_LESSON: int = 3
    QUIZ_TF_PER_LESSON: int = 2
    QUIZ_OPEN_PER_LESSON: int = 2

    # ─────────────────────────────────────────────
    # FLASHCARDS
    # ─────────────────────────────────────────────
    FLASHCARD_MAX_PER_TOPIC: int = 5

    # ─────────────────────────────────────────────
    # GAMIFICATION
    # ─────────────────────────────────────────────
    XP_COMPLETE_TOPIC: int = 10
    XP_COMPLETE_LESSON: int = 50
    XP_PASS_QUIZ_FIRST_TRY: int = 100
    XP_PASS_QUIZ_RETRY: int = 50
    XP_REVIEW_10_FLASHCARDS: int = 20
    XP_STREAK_7_DAYS: int = 200
    XP_COMPLETE_COURSE: int = 500
    STUDY_GOAL_DEFAULT_MINUTES: int = 30
    STREAK_GRACE_PERIOD_DAYS: int = 1

    # ─────────────────────────────────────────────
    # COMPUTED PROPERTIES
    # ─────────────────────────────────────────────

    DATABASE_URL: str | None = Field(default=None, validation_alias=AliasChoices("database_url"))

    @property
    def database_url(self) -> str:
        """Async PostgreSQL URL for SQLAlchemy with asyncpg driver."""
        if self.DATABASE_URL:
            url = self.DATABASE_URL.strip()
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def database_url_sync(self) -> str:
        """Sync PostgreSQL URL for Alembic migrations."""
        if self.DATABASE_URL:
            url = self.DATABASE_URL.strip()
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            elif url.startswith("postgresql+asyncpg://"):
                url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
            return url
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def redis_url(self) -> str:
        """Redis connection URL constructed from individual parts."""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def celery_broker_url(self) -> str:
        return self.redis_url

    @property
    def celery_result_backend(self) -> str:
        return self.redis_url

    @property
    def allowed_extensions(self) -> list[str]:
        """Parse ALLOWED_UPLOAD_EXTENSIONS into a list."""
        return [ext.strip() for ext in self.ALLOWED_UPLOAD_EXTENSIONS.split(",")]

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS into a list of clean origin strings."""
        if not self.CORS_ORIGINS:
            return []
        return [origin.strip().rstrip("/") for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def insightforge_path(self) -> Path | None:
        """Resolved absolute path to InsightForge-AI project if configured."""
        if not self.INSIGHTFORGE_PATH:
            return None
        return Path(self.INSIGHTFORGE_PATH).resolve()

    @property
    def upload_dir_path(self) -> Path:
        return Path(self.UPLOAD_DIR).resolve()

    @property
    def export_dir_path(self) -> Path:
        return Path(self.EXPORT_DIR).resolve()

    @property
    def log_file_path(self) -> Path | None:
        if not self.LOG_FILE:
            return None
        return Path(self.LOG_FILE).resolve()

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    # ─────────────────────────────────────────────
    # VALIDATORS
    # ─────────────────────────────────────────────

    @classmethod
    def _is_weak_secret(cls, secret: str) -> bool:
        forbidden = {"change_me", "password", "secret", "123456", "production_secret", "example_key", "your_postgres_password_here"}
        return secret.lower() in forbidden or secret.strip() == ""

    @field_validator("APP_SECRET_KEY", "JWT_SECRET_KEY")
    @classmethod
    def validate_strong_secret_key(cls, v: str, info: Any) -> str:
        if cls._is_weak_secret(v):
            raise ValueError(f"{info.field_name} uses a weak or placeholder value.")
        if len(v) < 32:
            raise ValueError(f"{info.field_name} must be at least 32 characters long.")
        return v

    @field_validator("POSTGRES_PASSWORD", "REDIS_PASSWORD")
    @classmethod
    def validate_password_not_placeholder(cls, v: str, info: Any) -> str:
        if v and cls._is_weak_secret(v):
            raise ValueError(f"{info.field_name} uses a weak or placeholder value.")
        return v

    @model_validator(mode="after")
    def validate_environment_consistency(self) -> "Settings":
        # Production Safety Rules
        if self.APP_ENV == "production":
            if self.APP_DEBUG:
                raise ValueError("APP_DEBUG must be False in production environment.")
            if self.ENABLE_DOCS:
                raise ValueError("ENABLE_DOCS must be False in production environment.")
            
            # Strict CORS in production
            forbidden_cors = ["localhost", "127.0.0.1", "0.0.0.0", "*"]
            for origin in self.cors_origins_list:
                for forbidden in forbidden_cors:
                    if forbidden in origin:
                        raise ValueError(f"CORS origin '{origin}' is not allowed in production.")
        
        # Redis & Celery consistency
        if self.CELERY_TASK_TIMEOUT_SECONDS > 0:
            if not self.REDIS_HOST:
                raise ValueError("Celery requires REDIS_HOST to be configured as a broker.")
            
        return self

    @model_validator(mode="after")
    def detect_suspicious_env_vars(self) -> "Settings":
        """Warns about environment variables that are likely typos of valid settings."""
        valid_keys = set(self.model_fields.keys())
        # We also consider alias choices
        for field_name, field in self.model_fields.items():
            if field.validation_alias and isinstance(field.validation_alias, AliasChoices):
                for alias in field.validation_alias.choices:
                    if isinstance(alias, str):
                        valid_keys.add(alias.upper())
        
        # We only check keys that are in os.environ but not in valid_keys
        # and are close to a valid key.
        for env_key in os.environ.keys():
            env_key_upper = env_key.upper()
            if env_key_upper not in valid_keys:
                matches = difflib.get_close_matches(env_key_upper, [k.upper() for k in valid_keys], n=1, cutoff=0.8)
                if matches:
                    logger.warning(
                        f"Suspicious environment variable detected: '{env_key}'. "
                        f"Did you mean '{matches[0]}'?"
                    )
        return self

    def get_startup_report(self) -> dict[str, str]:
        """Returns a sanitized, concise dictionary of current configurations."""
        return {
            "Configuration Version": "1",
            "Application Environment": self.APP_ENV,
            "Configuration Loaded": "Successfully",
            "Debug Mode": str(self.APP_DEBUG),
            "Database": "Configured",
            "Redis": "Configured" if self.REDIS_HOST else "Disabled",
            "Celery": "Configured",
            "Docs": "Enabled" if self.ENABLE_DOCS else "Disabled",
            "Rate Limiting": "Enabled",
            "Storage": "Configured",
            "LLM": "Configured"
        }


    @model_validator(mode="after")
    def validate_insightforge_path(self) -> "Settings":
        if self.INSIGHTFORGE_PATH:
            path = Path(self.INSIGHTFORGE_PATH)
            if not path.exists():
                import warnings
                warnings.warn(
                    f"\n[CourseForge] INSIGHTFORGE_PATH does not exist: {path}\n"
                    "External InsightForge-AI directory not found. "
                    "Using bundled internal package.",
                    UserWarning,
                    stacklevel=2,
                )
        return self

    @model_validator(mode="after")
    def ensure_insightforge_on_sys_path(self) -> "Settings":
        """
        Add InsightForge-AI to sys.path so its modules can be imported
        by the InsightForge adapter without modification if configured.
        Only adds the path if it actually exists to avoid polluting sys.path.
        """
        if self.INSIGHTFORGE_PATH:
            path = Path(self.INSIGHTFORGE_PATH)
            if path.exists():
                insight_path = str(path.resolve())
                if insight_path not in sys.path:
                    sys.path.insert(0, insight_path)
        return self


# ─────────────────────────────────────────────
# Singleton instance
# ─────────────────────────────────────────────
# Imported throughout the application as:
#   from core.config import settings
settings = Settings()  # type: ignore[call-arg]
