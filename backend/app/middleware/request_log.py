"""HTTP request logging: surfaces Gemini usage per request to catch storms."""
from __future__ import annotations

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from ..services.gemini import reset_request_gemini_stats, snapshot_request_gemini_stats

# Do not use uvicorn.access: its formatter expects exactly 5 record args.
logger = logging.getLogger("astra.request")


class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        reset_request_gemini_stats()
        started = time.perf_counter()
        response: Response | None = None
        error: str | None = None
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            error = str(exc)
            raise
        finally:
            elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
            gemini = snapshot_request_gemini_stats()
            path = request.url.path
            status = response.status_code if response is not None else 500
            gemini_flag = "yes" if gemini["called"] else "no"
            gemini_detail = ""
            if gemini["called"]:
                gemini_detail = (
                    f" | gemini_ops={gemini['count']}"
                    f" | gemini_ok={gemini['success']}"
                    f" | gemini_fail={gemini['failure']}"
                    f" | gemini_ms={gemini['total_ms']}"
                )
            err_suffix = f" | error={error}" if error else ""
            line = (
                f"{request.method} {path} → {status} in {elapsed_ms}ms"
                f" | ai={gemini_flag}{gemini_detail}{err_suffix}"
            )
            logger.info(line)
