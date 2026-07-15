"""
Request logging middleware.

Responsibilities
----------------
- Log every HTTP request
- Measure request duration
- Generate/forward X-Request-ID
- Log unhandled exceptions
"""

from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.logging import get_logger


logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs every incoming request.
    """

    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:

        # -----------------------------------------------------
        # Request ID
        # -----------------------------------------------------

        request_id = request.headers.get(
            "X-Request-ID",
            str(uuid.uuid4()),
        )

        request.state.request_id = request_id

        start_time = time.perf_counter()

        try:

            response = await call_next(request)

            duration = (
                time.perf_counter() - start_time
            ) * 1000

            response.headers["X-Request-ID"] = request_id

            logger.info(
                "[%s] %s %s -> %s (%.2f ms)",
                request_id,
                request.method,
                request.url.path,
                response.status_code,
                duration,
            )

            return response

        except Exception:

            duration = (
                time.perf_counter() - start_time
            ) * 1000

            logger.exception(
                "[%s] FAILED %s %s (%.2f ms)",
                request_id,
                request.method,
                request.url.path,
                duration,
            )

            raise