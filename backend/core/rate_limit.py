"""
CourseForge AI - Rate Limiting

Provides a shared SlowAPI Limiter instance and key functions used across
route decorators throughout the application.

Key decisions:
  - IP-based limiting for public auth endpoints (register, login)
  - User-ID-based limiting for authenticated AI/upload endpoints
  - In-memory backend (fine for single-process; swap for Redis backend at scale)
  - Works correctly behind Render/Vercel proxy via X-Forwarded-For

Usage in routes:
    from core.rate_limit import limiter
    from slowapi.util import get_remote_address

    @router.post("/register")
    @limiter.limit("5/minute")
    async def register(request: Request, ...):
        ...
"""

from __future__ import annotations

import logging
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)


def _get_user_or_ip(request: Request) -> str:
    """
    Rate-limit key function for authenticated endpoints.

    Returns the authenticated user's ID (from JWT state if available),
    falling back to the client IP address for unauthenticated requests.
    This prevents a single malicious user from bypassing limits by
    rotating IPs, while also protecting unauthenticated endpoints.
    """
    # SlowAPI calls this before route execution, so we read the
    # Authorization header directly rather than using the Depends system.
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        try:
            from jose import jwt
            from core.config import settings
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=["HS256"],
                options={"verify_exp": False},  # Only need the sub for keying
            )
            user_id = payload.get("sub")
            if user_id:
                return f"user:{user_id}"
        except Exception:
            pass  # Fall through to IP-based key
    return get_remote_address(request)


# ─────────────────────────────────────────────
# Global limiter singleton
# ─────────────────────────────────────────────
# key_func=get_remote_address → IP-based default.
# Individual routes override with _get_user_or_ip where needed.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],      # No blanket limit; apply explicitly per route
    headers_enabled=True,   # Emit X-RateLimit-* and Retry-After headers
)
