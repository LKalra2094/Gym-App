from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Any, Optional
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    """Standard error response model"""
    status_code: int
    detail: str
    error_type: str

class SuccessResponse(BaseModel):
    """Standard success response model"""
    status_code: int = 200
    message: str
    data: Any | None = None

def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            status_code=exc.status_code,
            detail=exc.detail,
            error_type="http_error"
        ).model_dump()
    )

def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle validation exceptions"""
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            status_code=422,
            detail=str(exc),
            error_type="validation_error"
        ).model_dump()
    )

def database_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle database exceptions"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            status_code=500,
            detail="Database error occurred",
            error_type="database_error"
        ).model_dump()
    )

def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            status_code=500,
            detail="Internal server error",
            error_type="server_error"
        ).model_dump()
    ) 