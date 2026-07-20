
from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.logging import get_logger

logger = get_logger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self,request: Request,call_next,) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER,str(uuid.uuid4()),)
        request.state.request_id = request_id
        start_time = time.perf_counter()
        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000

            response.headers[REQUEST_ID_HEADER] = request_id

            logger.info("[%s] %s %s -> %s (%.2f ms)",request_id,request.method,request.url.path,response.status_code,duration_ms,)
            return response
        except Exception:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.exception(
                "[%s] %s %s FAILED (%.2f ms)",
                request_id,
                request.method,
                request.url.path,
                duration_ms,
            )
            raise