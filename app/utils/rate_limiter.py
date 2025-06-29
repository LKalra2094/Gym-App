from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import time
import redis
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Redis client
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

class RateLimiter:
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        requests_per_day: int = 10000
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day

    async def check_rate_limit(self, request: Request) -> None:
        client_ip = request.client.host
        current_time = int(time.time())
        
        # Create keys for different time windows
        minute_key = f"rate_limit:{client_ip}:minute:{current_time // 60}"
        hour_key = f"rate_limit:{client_ip}:hour:{current_time // 3600}"
        day_key = f"rate_limit:{client_ip}:day:{current_time // 86400}"

        # Check and increment counters
        minute_count = redis_client.incr(minute_key)
        hour_count = redis_client.incr(hour_key)
        day_count = redis_client.incr(day_key)

        # Set expiration for keys
        redis_client.expire(minute_key, 60)
        redis_client.expire(hour_key, 3600)
        redis_client.expire(day_key, 86400)

        # Check limits
        if minute_count > self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail="Too many requests per minute"
            )
        if hour_count > self.requests_per_hour:
            raise HTTPException(
                status_code=429,
                detail="Too many requests per hour"
            )
        if day_count > self.requests_per_day:
            raise HTTPException(
                status_code=429,
                detail="Too many requests per day"
            )

# Create rate limiter instance
rate_limiter = RateLimiter()

# Rate limit middleware
async def rate_limit_middleware(request: Request, call_next):
    try:
        await rate_limiter.check_rate_limit(request)
        response = await call_next(request)
        return response
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail}
        ) 