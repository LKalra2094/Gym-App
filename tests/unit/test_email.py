"""
Unit tests for email utility functions in app.utils.email.
"""
import pytest
from unittest.mock import patch
import asyncio
from app.utils import email

@pytest.mark.asyncio
def test_send_verification_email_success():
    """Test that send_verification_email returns True on success."""
    with patch('app.utils.email.resend.emails.send', return_value=True):
        result = asyncio.run(email.send_verification_email('test@example.com', 'token'))
        assert result is True

@pytest.mark.asyncio
def test_send_verification_email_failure():
    """Test that send_verification_email returns False on exception."""
    with patch('app.utils.email.resend.emails.send', side_effect=Exception("fail")):
        result = asyncio.run(email.send_verification_email('test@example.com', 'token'))
        assert result is False

@pytest.mark.asyncio
def test_send_password_reset_email_success():
    """Test that send_password_reset_email returns True on success."""
    with patch('app.utils.email.resend.emails.send', return_value=True):
        result = asyncio.run(email.send_password_reset_email('test@example.com', 'token'))
        assert result is True

@pytest.mark.asyncio
def test_send_password_reset_email_failure():
    """Test that send_password_reset_email returns False on exception."""
    with patch('app.utils.email.resend.emails.send', side_effect=Exception("fail")):
        result = asyncio.run(email.send_password_reset_email('test@example.com', 'token'))
        assert result is False 