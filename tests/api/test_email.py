"""
Unit tests for email utility functions in app.utils.email.
"""
import pytest
from unittest.mock import patch
from app.utils import email

def test_send_verification_email_success():
    """Test that send_verification_email returns True on success."""
    with patch('resend.Emails.send') as mock_send:
        mock_send.return_value = {"id": "mock_id"}
        result = email.send_verification_email('test@example.com', 'token')
        assert result is True
        mock_send.assert_called_once()

def test_send_verification_email_failure():
    """Test that send_verification_email returns False on exception."""
    with patch('resend.Emails.send', side_effect=Exception("fail")):
        result = email.send_verification_email('test@example.com', 'token')
        assert result is False

def test_send_password_reset_email_success():
    """Test that send_password_reset_email returns True on success."""
    with patch('resend.Emails.send') as mock_send:
        mock_send.return_value = {"id": "mock_id"}
        result = email.send_password_reset_email('test@example.com', 'token')
        assert result is True
        mock_send.assert_called_once()

def test_send_password_reset_email_failure():
    """Test that send_password_reset_email returns False on exception."""
    with patch('resend.Emails.send', side_effect=Exception("fail")):
        result = email.send_password_reset_email('test@example.com', 'token')
        assert result is False 