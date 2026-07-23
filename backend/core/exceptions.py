"""
CourseForge AI — Application Exceptions

Defines a hierarchy of typed exceptions used throughout the application.
FastAPI exception handlers (registered in main.py) catch these and return
consistent JSON error responses.

Error Response Format:
    {
        "detail": "Human-readable message",
        "code": "MACHINE_READABLE_CODE",
        "field": "optional_field_name"  // For validation errors
    }
"""

from __future__ import annotations

from typing import Any


class CourseForgeError(Exception):
    """
    Base exception for all CourseForge application errors.
    All custom exceptions must inherit from this class.
    """

    status_code: int = 500
    code: str = "INTERNAL_ERROR"

    def __init__(
        self,
        detail: str = "An internal error occurred.",
        *,
        field: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        self.detail = detail
        self.field = field
        self.context = context or {}
        super().__init__(detail)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "detail": self.detail,
            "code": self.code,
        }
        if self.field:
            payload["field"] = self.field
        return payload


# ─────────────────────────────────────────────
# 400 Bad Request
# ─────────────────────────────────────────────

class ValidationError(CourseForgeError):
    """Raised when request data fails business-level validation."""
    status_code = 400
    code = "VALIDATION_ERROR"


class InvalidFileTypeError(CourseForgeError):
    """Raised when an uploaded file has an unsupported extension."""
    status_code = 400
    code = "INVALID_FILE_TYPE"


class FileTooLargeError(CourseForgeError):
    """Raised when an uploaded file exceeds the size limit."""
    status_code = 400
    code = "FILE_TOO_LARGE"


class InvalidCredentialsError(CourseForgeError):
    """Raised when login credentials are incorrect."""
    status_code = 401
    code = "INVALID_CREDENTIALS"

class UnauthorizedError(CourseForgeError):
    """Raised for general authentication failures."""
    status_code = 401
    code = "UNAUTHORIZED"


class TokenExpiredError(CourseForgeError):
    """Raised when a JWT token has expired."""
    status_code = 401
    code = "TOKEN_EXPIRED"


class TokenInvalidError(CourseForgeError):
    """Raised when a JWT token is malformed or invalid."""
    status_code = 401
    code = "TOKEN_INVALID"


# ─────────────────────────────────────────────
# 403 Forbidden
# ─────────────────────────────────────────────

class PermissionDeniedError(CourseForgeError):
    """Raised when a user lacks permission to perform an action."""
    status_code = 403
    code = "PERMISSION_DENIED"


class MaxAttemptsExceededError(CourseForgeError):
    """Raised when a user has exhausted their quiz attempts."""
    status_code = 403
    code = "MAX_ATTEMPTS_EXCEEDED"


# ─────────────────────────────────────────────
# 404 Not Found
# ─────────────────────────────────────────────

class NotFoundError(CourseForgeError):
    """Raised when a requested resource does not exist."""
    status_code = 404
    code = "NOT_FOUND"


class CourseNotFoundError(NotFoundError):
    code = "COURSE_NOT_FOUND"


class LessonNotFoundError(NotFoundError):
    code = "LESSON_NOT_FOUND"


class QuizNotFoundError(NotFoundError):
    code = "QUIZ_NOT_FOUND"


class AttemptNotFoundError(NotFoundError):
    code = "ATTEMPT_NOT_FOUND"


class FlashcardNotFoundError(NotFoundError):
    code = "FLASHCARD_NOT_FOUND"


class ChatSessionNotFoundError(NotFoundError):
    code = "CHAT_SESSION_NOT_FOUND"


# ─────────────────────────────────────────────
# 409 Conflict
# ─────────────────────────────────────────────

class ConflictError(CourseForgeError):
    """Raised when an operation conflicts with existing data."""
    status_code = 409
    code = "CONFLICT"


class EmailAlreadyExistsError(ConflictError):
    code = "EMAIL_EXISTS"


class AlreadyEnrolledError(ConflictError):
    code = "ALREADY_ENROLLED"


# ─────────────────────────────────────────────
# 422 Unprocessable
# ─────────────────────────────────────────────

class CourseNotReadyError(CourseForgeError):
    """Raised when an action requires a course to be in 'ready' status."""
    status_code = 422
    code = "COURSE_NOT_READY"


# ─────────────────────────────────────────────
# 429 Rate Limited
# ─────────────────────────────────────────────

class RateLimitError(CourseForgeError):
    """Raised when a user exceeds a rate limit."""
    status_code = 429
    code = "RATE_LIMIT_EXCEEDED"


# ─────────────────────────────────────────────
# 500 Internal
# ─────────────────────────────────────────────

class AIGenerationError(CourseForgeError):
    """Raised when the AI pipeline fails to generate valid output."""
    status_code = 500
    code = "AI_GENERATION_FAILED"


class InsightForgeError(CourseForgeError):
    """Raised when the InsightForge adapter encounters an error."""
    status_code = 500
    code = "INSIGHTFORGE_ERROR"


class ExportError(CourseForgeError):
    """Raised when a course export fails."""
    status_code = 500
    code = "EXPORT_FAILED"
