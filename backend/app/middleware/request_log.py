"""HTTP request logging: surfaces LLM usage per request to catch storms."""
from __future__ import annotations

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from ..services.llm import reset_request_llm_stats, snapshot_request_llm_stats

logger = logging.getLogger("astra.access")


class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        reset_request_llm_stats()
        started = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            elapsed_ms = (time.perf_counter() - started) * 1000
            llm = snapshot_request_llm_stats()
            path = request.url.path
            method = request.method
            llm_flag = "yes" if llm["called"] else "no"
            llm_detail = ""
            if llm["called"]:
                llm_detail = (
                    f" | llm_ops={llm['count']}"
                    f" | llm_ok={llm['success']}"
                    f" | llm_fail={llm['failure']}"
                    f" | llm_ms={llm['total_ms']}"
                )
            err_suffix = "" if status_code < 400 else " | status=error"
            logger.info(
                f'{method} {path} {status_code} {elapsed_ms:.0f}ms'
                f" | ai={llm_flag}{llm_detail}{err_suffix}"
            )
