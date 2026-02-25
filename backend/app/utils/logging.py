
import logging
import sys
import json
from typing import Optional
from datetime import datetime
from flask import Flask, g, has_request_context, request
import uuid


class RequestIdFilter(logging.Filter):
    """Filter that adds request_id to log records."""
    
    def filter(self, record):
        if has_request_context():
            record.request_id = getattr(g, 'request_id', 'no-request')
            record.path = request.path
            record.method = request.method
        else:
            record.request_id = 'no-request'
            record.path = '-'
            record.method = '-'
        return True


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'request_id': getattr(record, 'request_id', 'no-request'),
        }
        
        # Add request context if available
        if hasattr(record, 'path') and record.path != '-':
            log_data['path'] = record.path
            log_data['method'] = record.method
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add any extra fields
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """Human-readable text formatter for development."""
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s | %(levelname)-8s | %(request_id)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


def setup_logging(app: Flask) -> None:
    """Configure logging for the Flask application."""
    
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())
    log_format = app.config.get('LOG_FORMAT', 'json')
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    # Choose formatter
    if log_format == 'json':
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(TextFormatter())
    
    # Add request ID filter
    handler.addFilter(RequestIdFilter())
    
    # Configure app logger
    app.logger.handlers = []
    app.logger.addHandler(handler)
    app.logger.setLevel(log_level)
    
    # Configure root logger for other libraries
    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.WARNING)  # Suppress noisy libraries
    
    # Suppress TensorFlow logs
    logging.getLogger('tensorflow').setLevel(logging.ERROR)
    logging.getLogger('absl').setLevel(logging.ERROR)
    
    app.logger.info(
        f"Logging configured",
        extra={'extra_data': {'level': app.config.get('LOG_LEVEL'), 'format': log_format}}
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    logger = logging.getLogger(name)
    return logger


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())[:8]
