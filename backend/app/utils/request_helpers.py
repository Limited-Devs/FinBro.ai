"""
Request handling utilities for API routes.

Provides shared helpers for:
- Demo user detection and handling
- Validation error formatting
- Standardized error responses
"""
from typing import Optional, Dict, Any, List
from flask import Request
from pydantic import ValidationError as PydanticValidationError


DEMO_USER_ID = 'demo'


def get_user_context(request: Request) -> tuple[Optional[str], bool]:
    """
    Extract user context from request headers.
    
    Args:
        request: Flask request object
        
    Returns:
        Tuple of (user_id, is_demo)
    """
    user_id = request.headers.get('X-User-ID')
    is_demo = request.headers.get('X-Demo-Mode', 'false').lower() == 'true'
    
    if is_demo:
        user_id = DEMO_USER_ID
    
    return user_id, is_demo


def format_validation_error(error: PydanticValidationError) -> Dict[str, Any]:
    """
    Format Pydantic validation errors into standard API response format.
    
    Args:
        error: Pydantic ValidationError
        
    Returns:
        Dictionary suitable for JSON response
    """
    errors = []
    for err in error.errors():
        field = '.'.join(str(loc) for loc in err['loc'])
        errors.append({
            'field': field,
            'message': err['msg']
        })
    
    return {
        "error": True,
        "error_code": "VALIDATION_ERROR",
        "message": "Request validation failed",
        "details": {"validation_errors": errors}
    }


def create_error_response(
    error_code: str,
    message: str,
    status_code: int = 400,
    details: Optional[Dict[str, Any]] = None
) -> tuple[Dict[str, Any], int]:
    """
    Create a standardized error response.
    
    Args:
        error_code: Machine-readable error code
        message: Human-readable error message
        status_code: HTTP status code
        details: Additional error details
        
    Returns:
        Tuple of (response_dict, status_code)
    """
    response = {
        "error": True,
        "error_code": error_code,
        "message": message
    }
    
    if details:
        response["details"] = details
    
    return response, status_code
