"""Performance timing middleware."""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from app.core.constants import PROCESS_TIME_HEADER

class ProcessTimingMiddleware(BaseHTTPMiddleware):
    """Calculates request processing time and injects it into headers."""
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers[PROCESS_TIME_HEADER] = str(round(process_time, 4))
        return response