"""
Flask extensions initialization.

Extensions:
- Flask-Limiter: Rate limiting
- Flask-Caching: Response caching
"""
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize extensions without app (will be configured in create_app)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per minute"],
    storage_uri="memory://",
)


def init_extensions(app: Flask) -> None:
    """Initialize all Flask extensions with the app instance."""
    
    # Configure rate limiter
    if app.config.get('RATELIMIT_ENABLED', True):
        limiter.init_app(app)
        app.logger.info("Rate limiting enabled")
    else:
        app.logger.info("Rate limiting disabled")
