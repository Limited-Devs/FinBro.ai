
from flask import Flask, jsonify, current_app, g
from werkzeug.exceptions import HTTPException
from pydantic import ValidationError as PydanticValidationError

from app.models.exceptions import FinBroException


def register_error_handlers(app: Flask) -> None:
    """Register all error handlers with the Flask app."""
    
    @app.errorhandler(FinBroException)
    def handle_finbro_exception(error: FinBroException):
        """Handle custom FinBro exceptions."""
        current_app.logger.warning(
            f"FinBro exception: {error.error_code} - {error.message}",
            extra={'extra_data': {'error_code': error.error_code, 'details': error.details}}
        )
        
        response = error.to_dict()
        response['request_id'] = getattr(g, 'request_id', None)
        
        return jsonify(response), error.status_code
    
    @app.errorhandler(PydanticValidationError)
    def handle_pydantic_validation_error(error: PydanticValidationError):
        """Handle Pydantic validation errors."""
        current_app.logger.warning(
            f"Validation error: {error.error_count()} errors"
        )
        
        # Format validation errors nicely
        errors = []
        for err in error.errors():
            field = '.'.join(str(loc) for loc in err['loc'])
            errors.append({
                'field': field,
                'message': err['msg'],
                'type': err['type']
            })
        
        response = {
            'error': True,
            'error_code': 'VALIDATION_ERROR',
            'message': 'Request validation failed',
            'details': {'validation_errors': errors},
            'request_id': getattr(g, 'request_id', None)
        }
        
        return jsonify(response), 400
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        """Handle standard HTTP exceptions."""
        current_app.logger.warning(
            f"HTTP exception: {error.code} - {error.description}"
        )
        
        response = {
            'error': True,
            'error_code': f'HTTP_{error.code}',
            'message': error.description,
            'request_id': getattr(g, 'request_id', None)
        }
        
        return jsonify(response), error.code
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error: Exception):
        """Handle unexpected exceptions."""
        current_app.logger.exception(
            f"Unexpected error: {str(error)}"
        )
        
        # Don't expose internal errors in production
        message = str(error) if app.debug else "An internal error occurred"
        
        response = {
            'error': True,
            'error_code': 'INTERNAL_ERROR',
            'message': message,
            'request_id': getattr(g, 'request_id', None)
        }
        
        return jsonify(response), 500
