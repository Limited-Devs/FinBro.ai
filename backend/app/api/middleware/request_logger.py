"""
Request logging middleware.

Logs all incoming requests and outgoing responses
with timing information and correlation IDs.
"""
import time
from flask import Flask, request, g
from app.utils.logging import generate_request_id


def register_request_logging(app: Flask) -> None:
    """Register request/response logging middleware."""
    
    @app.before_request
    def before_request():
        """Log incoming request and set up correlation ID."""
        # Generate unique request ID
        g.request_id = request.headers.get('X-Request-ID', generate_request_id())
        g.start_time = time.time()
        
        # Skip logging for static files and health checks
        if request.path.startswith('/assets/') or request.path == '/api/health':
            return
        
        app.logger.info(
            f"Request started: {request.method} {request.path}",
            extra={'extra_data': {
                'method': request.method,
                'path': request.path,
                'remote_addr': request.remote_addr,
                'user_agent': request.user_agent.string[:100] if request.user_agent.string else None
            }}
        )
    
    @app.after_request
    def after_request(response):
        """Log outgoing response with timing."""
        # Add request ID to response headers
        response.headers['X-Request-ID'] = getattr(g, 'request_id', 'unknown')
        
        # Skip logging for static files and health checks
        if request.path.startswith('/assets/') or request.path == '/api/health':
            return response
        
        # Calculate request duration
        duration_ms = 0
        if hasattr(g, 'start_time'):
            duration_ms = (time.time() - g.start_time) * 1000
        
        log_level = 'info'
        if response.status_code >= 500:
            log_level = 'error'
        elif response.status_code >= 400:
            log_level = 'warning'
        
        log_method = getattr(app.logger, log_level)
        log_method(
            f"Request completed: {response.status_code} in {duration_ms:.2f}ms",
            extra={'extra_data': {
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration_ms': round(duration_ms, 2)
            }}
        )
        
        return response
