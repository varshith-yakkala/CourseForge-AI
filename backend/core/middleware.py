"""
CourseForge AI — CORS and Request Logging Middleware

Registers:
    1. CORS middleware — allows the React frontend to call the API.
    2. Request logging middleware — logs every request with method, path, status, duration.

Both are registered in main.py via register_middleware(app).
"""

from __future__ import annotations

import logging
import time

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import settings

logger = logging.getLogger(__name__)


def register_middleware(app: FastAPI) -> None:
    """
    Register all middleware on the FastAPI application instance.
    Order matters: middleware is applied bottom-up (last registered = outermost).
    """
    _register_cors(app)
    _register_request_logger(app)


def _register_cors(app: FastAPI) -> None:
    """Configure CORS to allow the React frontend origin."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Process-Time"],
    )


def _register_request_logger(app: FastAPI) -> None:
    """Log every incoming request with timing information."""
    app.add_middleware(_RequestLoggingMiddleware)


class _RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs every HTTP request.

    Logs:
        - Method + path + query string
        - Response status code
        - Total processing time in milliseconds
        - Client IP address
    """

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        start_time = time.perf_counter()

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Add processing time header for debugging
        response.headers["X-Process-Time"] = f"{duration_ms}ms"

        log_level = logging.WARNING if response.status_code >= 500 else logging.INFO

        logger.log(
            log_level,
            "HTTP request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query": str(request.url.query) or None,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "client_ip": _get_client_ip(request),
            },
        )

        return response


def _get_client_ip(request: Request) -> str:
    """Extract client IP, respecting X-Forwarded-For (for Nginx proxy)."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"
