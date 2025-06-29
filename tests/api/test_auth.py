"""
Unit tests for authentication utility functions in app.core.security.
"""
from unittest.mock import patch
from app.core import security
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import settings
import time
import pytest

def test_verify_password():
    """Test password verification logic."""
    with patch.object(security.pwd_context, 'verify', return_value=True) as mock_verify:
        assert security.verify_password('plain', 'hashed') is True
        mock_verify.assert_called_once_with('plain', 'hashed')


def test_get_password_hash():
    """Test password hashing logic."""
    with patch.object(security.pwd_context, 'hash', return_value='hashed') as mock_hash:
        assert security.get_password_hash('plain') == 'hashed'
        mock_hash.assert_called_once_with('plain')


def test_create_access_token():
    """Test JWT access token creation logic."""
    with patch('app.core.security.jwt.encode', return_value='token') as mock_encode:
        subject = 'user_id'
        token = security.create_access_token(subject)
        assert token == 'token'
        assert mock_encode.called


def test_token_expiration():
    """Test that token expiration is set correctly."""
    # Token expires in 1 minute
    expires = timedelta(minutes=1)
    token = security.create_access_token("testuser", expires_delta=expires)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    
    # Check that 'exp' is roughly 1 minute from now
    expected_exp = datetime.now(timezone.utc) + expires
    assert payload["exp"] == pytest.approx(expected_exp.timestamp(), abs=1)

    # Token expired 1 minute ago
    expires = timedelta(minutes=-1)
    token = security.create_access_token("testuser", expires_delta=expires)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM], options={"verify_exp": False})
    
    # Check that 'exp' is roughly 1 minute in the past
    expected_exp = datetime.now(timezone.utc) + expires
    assert payload["exp"] == pytest.approx(expected_exp.timestamp(), abs=1) 