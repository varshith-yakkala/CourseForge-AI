"""
CourseForge AI — Backend Application Configuration

Loads all settings from environment variables using Pydantic Settings.
This is the single source of truth for all configuration values.
All application code imports settings from this module — never from os.environ directly.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

from pydantic import AnyUrl, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    APP_PORT: int = 8001
    APP_SECRET_KEY: str
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
    CELERY_TASK_TIMEOUT_SECONDS: int = 600
    CELERY_MAX_RETRIES: int = 3

    # ─────────────────────────────────────────────
    # JWT AUTHENTICATION
    # ─────────────────────────────────────────────
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ─────────────────────────────────────────────
    # INSIGHTFORGE INTEGRATION
    # ─────────────────────────────────────────────
    INSIGHTFORGE_PATH: str = "./insightforge-ai"

    # ─────────────────────────────────────────────
    # AI — GROQ
    # ─────────────────────────────────────────────
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_MAX_TOKENS: int = 2048
    GROQ_TEMPERATURE: float = 0.2
    GROQ_REQUEST_TIMEOUT_SECONDS: int = 60

    # ─────────────────────────────────────────────
    # AI — EMBEDDING
    # ─────────────────────────────────────────────
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # ─────────────────────────────────────────────
    # FILE STORAGE
    # ─────────────────────────────────────────────
    UPLOAD_DIR: str = "./uploads"
    EXPORT_DIR: str = "./exports"
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_UPLOAD_EXTENSIONS: str = ".pdf,.txt,.md"

    # ─────────────────────────────────────────────
    # CORS
    # ─────────────────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
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
    RATE_LIMIT_CHAT_MESSAGES_PER_HOUR: int = 60
    RATE_LIMIT_UPLOAD_PER_DAY: int = 10

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

    @property
    def database_url(self) -> str:
        """Async PostgreSQL URL for SQLAlchemy with asyncpg driver."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def database_url_sync(self) -> str:
        """Sync PostgreSQL URL for Alembic migrations."""
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
        """Parse CORS_ORIGINS into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def insightforge_path(self) -> Path:
        """Resolved absolute path to InsightForge-AI project."""
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

    @field_validator("APP_SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError(
                "APP_SECRET_KEY must be at least 32 characters long. "
                "Generate with: python -c \"import secrets; print(secrets.token_hex(64))\""
            )
        return v

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError(
                "JWT_SECRET_KEY must be at least 32 characters long. "
                "Generate with: python -c \"import secrets; print(secrets.token_hex(64))\""
            )
        return v

    @model_validator(mode="after")
    def validate_insightforge_path(self) -> "Settings":
        path = Path(self.INSIGHTFORGE_PATH)
        if not path.exists():
            import warnings
            if self.APP_ENV == "production":
                raise ValueError(
                    f"INSIGHTFORGE_PATH does not exist: {path}\n"
                    "Ensure InsightForge-AI is cloned at the configured path."
                )
            else:
                warnings.warn(
                    f"\n[CourseForge] INSIGHTFORGE_PATH does not exist: {path}\n"
                    "InsightForge-AI features (search, generation) will be unavailable.\n"
                    "Set INSIGHTFORGE_PATH in backend/.env to enable AI features.",
                    UserWarning,
                    stacklevel=2,
                )
        return self

    @model_validator(mode="after")
    def ensure_insightforge_on_sys_path(self) -> "Settings":
        """
        Add InsightForge-AI to sys.path so its modules can be imported
        by the InsightForge adapter without modification.
        Only adds the path if it actually exists to avoid polluting sys.path.
        """
        insight_path = str(Path(self.INSIGHTFORGE_PATH).resolve())
        if Path(self.INSIGHTFORGE_PATH).exists() and insight_path not in sys.path:
            sys.path.insert(0, insight_path)
        return self


# ─────────────────────────────────────────────
# Singleton instance
# ─────────────────────────────────────────────
# Imported throughout the application as:
#   from core.config import settings
settings = Settings()  # type: ignore[call-arg]
