"""
Unit tests for authentication utility functions in app.utils.auth.
"""
import pytest
from unittest.mock import patch
from app.utils import auth

def test_verify_password():
    """Test password verification logic."""
    with patch.object(auth.pwd_context, 'verify', return_value=True) as mock_verify:
        assert auth.verify_password('plain', 'hashed') is True
        mock_verify.assert_called_once_with('plain', 'hashed')


def test_get_password_hash():
    """Test password hashing logic."""
    with patch.object(auth.pwd_context, 'hash', return_value='hashed') as mock_hash:
        assert auth.get_password_hash('plain') == 'hashed'
        mock_hash.assert_called_once_with('plain')


def test_create_access_token():
    """Test JWT access token creation logic."""
    with patch('app.utils.auth.jwt.encode', return_value='token') as mock_encode:
        data = {'sub': 'user_id'}
        token = auth.create_access_token(data)
        assert token == 'token'
        assert mock_encode.called 