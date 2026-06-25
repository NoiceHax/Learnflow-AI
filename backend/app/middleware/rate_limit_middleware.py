"""Global per-IP rate limiting middleware.

Applies a broad request-per-minute cap across all ``/api/`` routes to prevent
a single IP from overwhelming the server — whether authenticated or not.
Health and static endpoints are exempted.
"""
from __future__ import annotations

import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from ..config import settings
from ..services.rate_limiter import GlobalIPLimiter

logger = logging.getLogger("astra.ratelimit")

# Module-level singleton — shared across the app lifetime.
_global_ip_limiter = GlobalIPLimiter(
    max_requests=settings.rate_limit_global_minute,
    window_seconds=60.0,
)

# Paths that bypass the global limiter (health checks, docs, root).
_EXEMPT_PREFIXES = ("/api/health", "/docs", "/openapi.json", "/redoc")


def get_global_ip_limiter() -> GlobalIPLimiter:
    """Expose the singleton so tests can call ``.clear()``."""
    return _global_ip_limiter


def _client_ip(request: Request) -> str:
    """Best-effort client IP: respect X-Forwarded-For behind a reverse proxy."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    client = request.client
    return client.host if client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path

        # Skip non-API and exempt paths
        if not path.startswith("/api/") or any(path.startswith(p) for p in _EXEMPT_PREFIXES):
            return await call_next(request)

        # Skip OPTIONS (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        ip = _client_ip(request)
        blocked, retry_after = _global_ip_limiter.is_blocked(ip)

        if blocked:
            logger.warning("Global IP rate limit exceeded: ip=%s path=%s", ip, path)
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please slow down and try again shortly.",
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(settings.rate_limit_global_minute),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        return response
