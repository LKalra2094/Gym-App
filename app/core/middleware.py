import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from .config import settings

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID to each request."""
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to responses."""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        for header, value in settings.SECURITY_HEADERS.items():
            response.headers[header] = value
        return response

class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware to track request timing."""
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response 