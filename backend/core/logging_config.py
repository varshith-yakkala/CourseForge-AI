"""
CourseForge AI — Logging Configuration

Configures structured JSON logging (production) and human-readable text logging (development).
Uses the standard library logging module with optional structlog for JSON formatting.

All application modules should use:
    import logging
    logger = logging.getLogger(__name__)

This module is called once at application startup from main.py.
"""

from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Literal


def configure_logging(
    level: str = "INFO",
    format: Literal["json", "text"] = "json",
    log_file: Path | None = None,
) -> None:
    """
    Configure application-wide logging.

    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        format: Output format. 'json' for production, 'text' for development.
        log_file: Optional path to write logs to a file in addition to stdout.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    handlers: list[logging.Handler] = []

    # ─────────────────────────────────────────────
    # Console handler
    # ─────────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)

    if format == "json":
        console_handler.setFormatter(_JsonFormatter())
    else:
        console_handler.setFormatter(_TextFormatter())

    handlers.append(console_handler)

    # ─────────────────────────────────────────────
    # File handler (optional)
    # ─────────────────────────────────────────────
    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB per file
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(_JsonFormatter())  # Always JSON in file
        handlers.append(file_handler)

    # ─────────────────────────────────────────────
    # Root logger configuration
    # ─────────────────────────────────────────────
    logging.basicConfig(
        level=numeric_level,
        handlers=handlers,
        force=True,
    )

    # ─────────────────────────────────────────────
    # Silence noisy third-party loggers
    # ─────────────────────────────────────────────
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("faiss").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        "Logging configured",
        extra={"level": level, "format": format, "log_file": str(log_file)},
    )


class _TextFormatter(logging.Formatter):
    """Human-readable log formatter for development."""

    _LEVEL_COLORS = {
        "DEBUG": "\033[36m",    # Cyan
        "INFO": "\033[32m",     # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",    # Red
        "CRITICAL": "\033[35m", # Magenta
    }
    _RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self._LEVEL_COLORS.get(record.levelname, "")
        reset = self._RESET
        level = f"{color}{record.levelname:<8}{reset}"
        name = f"\033[90m{record.name}\033[0m"
        return f"{self.formatTime(record, '%H:%M:%S')} {level} {name} — {record.getMessage()}"


class _JsonFormatter(logging.Formatter):
    """
    JSON log formatter for production and file output.
    Outputs one JSON object per line (newline-delimited JSON).
    """

    def format(self, record: logging.LogRecord) -> str:
        import json
        import traceback

        payload: dict = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include extra fields attached via extra={...} in log calls
        for key, value in record.__dict__.items():
            if key not in (
                "args", "asctime", "created", "exc_info", "exc_text",
                "filename", "funcName", "id", "levelname", "levelno",
                "lineno", "module", "msecs", "message", "msg", "name",
                "pathname", "process", "processName", "relativeCreated",
                "stack_info", "thread", "threadName",
            ):
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)
