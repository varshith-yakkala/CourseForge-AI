"""
CourseForge AI — Middleware Suite (CORS, Security Headers, Request ID & Request Logging)

Registers:
    1. CORS middleware — allows the React frontend to call the API.
    2. Security Headers middleware — enforces CSP, X-Frame-Options, HSTS, X-Content-Type-Options.
    3. Request ID middleware — generates/propagates unique X-Request-ID for request tracing.
    4. Request logging middleware — logs every request with method, path, status, duration.
"""

from __future__ import annotations

import logging
import time
import uuid

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import settings

logger = logging.getLogger(__name__)


def register_middleware(app: FastAPI) -> None:
    """
    Register all middleware on the FastAPI application instance.

    In Starlette, middlewares execute in REVERSE order of registration (last added runs outermost).
    CORSMiddleware MUST be registered LAST so that it intercepts CORS preflight OPTIONS requests
    before any custom BaseHTTPMiddleware or router route matching.
    """
    app.add_middleware(_SecurityHeadersMiddleware)
    app.add_middleware(_RequestLoggingMiddleware)
    _register_cors(app)


def _register_cors(app: FastAPI) -> None:
    """Configure CORS to allow local dev, production, and Vercel preview origins."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_origin_regex=settings.CORS_ORIGIN_REGEX,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Process-Time"],
    )


class _SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Enforces production security headers on all responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://fastapi.tiangolo.com; "
            "font-src 'self' data: https://cdn.jsdelivr.net;"
        )
        if settings.APP_ENV == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


class _RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs every HTTP request and propagates X-Request-ID."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start_time = time.perf_counter()

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{duration_ms}ms"

        log_level = logging.WARNING if response.status_code >= 500 else logging.INFO

        logger.log(
            log_level,
            "HTTP request",
            extra={
                "request_id": request_id,
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
