"""
Unit tests for rate limiting utility in app.utils.rate_limiter.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.utils.rate_limiter import RateLimiter
from fastapi import HTTPException

@pytest.mark.asyncio
def test_check_rate_limit_allows_within_limits():
    """Test that requests within limits do not raise an exception."""
    limiter = RateLimiter(requests_per_minute=2, requests_per_hour=5, requests_per_day=10)
    mock_request = MagicMock()
    mock_request.client.host = '127.0.0.1'
    with patch('app.utils.rate_limiter.redis_client') as mock_redis:
        mock_redis.incr.return_value = 1
        mock_redis.expire.return_value = None
        # Should not raise
        import asyncio
        asyncio.run(limiter.check_rate_limit(mock_request))

@pytest.mark.asyncio
@pytest.mark.parametrize('minute, hour, day', [(3, 1, 1), (1, 6, 1), (1, 1, 11)])
def test_check_rate_limit_raises(minute, hour, day):
    """Test that exceeding any limit raises HTTPException."""
    limiter = RateLimiter(requests_per_minute=2, requests_per_hour=5, requests_per_day=10)
    mock_request = MagicMock()
    mock_request.client.host = '127.0.0.1'
    with patch('app.utils.rate_limiter.redis_client') as mock_redis:
        mock_redis.incr.side_effect = [minute, hour, day]
        mock_redis.expire.return_value = None
        import asyncio
        with pytest.raises(HTTPException):
            asyncio.run(limiter.check_rate_limit(mock_request)) 