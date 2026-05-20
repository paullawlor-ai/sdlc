"""Rate limiting configuration."""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings

# Create rate limiter using client IP
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_PERIOD}seconds"],
)

