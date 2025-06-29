# app/core/middleware.py

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from .config import settings


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add a unique request ID to each request and response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware to track request timing using a high-resolution clock."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start
        # four decimal places of precision
        response.headers["X-Process-Time"] = f"{elapsed:.4f}"
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to inject security headers into every response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        for header, value in settings.SECURITY_HEADERS.items():
            response.headers[header] = value
        return response
