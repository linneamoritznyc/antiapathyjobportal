"""
Rate limiting using slowapi
Protects API endpoints from abuse
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import get_settings

settings = get_settings()

# Create limiter instance using client IP as key
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_requests}/{settings.rate_limit_window}seconds"]
)


def setup_rate_limiting(app):
    """
    Configure rate limiting on FastAPI app

    Args:
        app: FastAPI application instance
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
