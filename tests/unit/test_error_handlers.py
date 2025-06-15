"""
Unit tests for error handler utilities in app.utils.error_handlers.
"""
import pytest
from app.utils.error_handlers import ErrorResponse, SuccessResponse, http_exception_handler, validation_exception_handler, database_exception_handler, general_exception_handler
from fastapi import HTTPException, Request
from unittest.mock import MagicMock
import asyncio


def test_error_response_model():
    """Test ErrorResponse model fields."""
    err = ErrorResponse(status_code=400, detail="Bad Request", error_type="http_error")
    assert err.status_code == 400
    assert err.detail == "Bad Request"
    assert err.error_type == "http_error"


def test_success_response_model():
    """Test SuccessResponse model fields."""
    resp = SuccessResponse(message="OK", data={"foo": "bar"})
    assert resp.status_code == 200
    assert resp.message == "OK"
    assert resp.data == {"foo": "bar"}

@pytest.mark.asyncio
def test_http_exception_handler():
    """Test http_exception_handler returns correct JSONResponse."""
    req = MagicMock(Request)
    exc = HTTPException(status_code=404, detail="Not found")
    response = asyncio.run(http_exception_handler(req, exc))
    assert response.status_code == 404
    assert response.body

@pytest.mark.asyncio
def test_validation_exception_handler():
    """Test validation_exception_handler returns correct JSONResponse."""
    req = MagicMock(Request)
    exc = Exception("Validation failed")
    response = asyncio.run(validation_exception_handler(req, exc))
    assert response.status_code == 422
    assert response.body

@pytest.mark.asyncio
def test_database_exception_handler():
    """Test database_exception_handler returns correct JSONResponse."""
    req = MagicMock(Request)
    exc = Exception("DB error")
    response = asyncio.run(database_exception_handler(req, exc))
    assert response.status_code == 500
    assert response.body

@pytest.mark.asyncio
def test_general_exception_handler():
    """Test general_exception_handler returns correct JSONResponse."""
    req = MagicMock(Request)
    exc = Exception("General error")
    response = asyncio.run(general_exception_handler(req, exc))
    assert response.status_code == 500
    assert response.body 