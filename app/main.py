# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from .core.config import settings
from .core.middleware import RequestIDMiddleware, SecurityHeadersMiddleware, TimingMiddleware
from .api.v1.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for tracking workout progress and exercise weights",
    version=settings.VERSION,
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# 1. CORS first—so preflight requests are handled immediately
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
)

# 2. GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 3. Custom middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(TimingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# 4. Versioned API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with basic welcome information.
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs_url": f"{settings.API_V1_STR}/docs",
        "version": settings.VERSION,
    }


@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
async def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}


# Explicitly export the ASGI app for Uvicorn / Vercel
__all__ = ["app"]
