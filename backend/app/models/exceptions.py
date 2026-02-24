"""
Custom exception hierarchy for FinBro.ai.

All exceptions inherit from FinBroException for consistent error handling.
Each exception type maps to appropriate HTTP status codes.
"""
from typing import Optional, Dict, Any
from enum import Enum


class ErrorCode(str, Enum):
    INVALID_REQUEST = "INVALID_REQUEST"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    ML_MODEL_ERROR = "ML_MODEL_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    NOT_FOUND = "NOT_FOUND"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    CALCULATION_ERROR = "CALCULATION_ERROR"
    AUTH_REQUIRED = "AUTH_REQUIRED"


class FinBroException(Exception):
    """
    Base exception for all FinBro.ai application errors.
    
    Attributes:
        message: Human-readable error message
        error_code: Machine-readable error code
        status_code: HTTP status code
        details: Additional error details
    """
    
    def __init__(
        self,
        message: str = "An unexpected error occurred",
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response."""
        return {
            "error": True,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }


class ValidationError(FinBroException):
    """Raised when input validation fails."""
    
    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[Dict[str, Any]] = None,
        field: Optional[str] = None
    ):
        if field:
            details = details or {}
            details["field"] = field
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=details
        )


class DatabaseError(FinBroException):
    """Raised when database operations fail."""
    
    def __init__(
        self,
        message: str = "Database operation failed",
        details: Optional[Dict[str, Any]] = None,
        operation: Optional[str] = None
    ):
        if operation:
            details = details or {}
            details["operation"] = operation
        
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=503,
            details=details
        )


class MLModelError(FinBroException):
    """Raised when ML model operations fail."""
    
    def __init__(
        self,
        message: str = "ML model error",
        details: Optional[Dict[str, Any]] = None,
        model_name: Optional[str] = None
    ):
        if model_name:
            details = details or {}
            details["model"] = model_name
        
        super().__init__(
            message=message,
            error_code="ML_MODEL_ERROR",
            status_code=500,
            details=details
        )


class RateLimitExceeded(FinBroException):
    """Raised when rate limit is exceeded."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded. Please try again later.",
        retry_after: Optional[int] = None
    ):
        details = {}
        if retry_after:
            details["retry_after_seconds"] = retry_after
        
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details=details
        )


class ExternalServiceError(FinBroException):
    """Raised when external service (e.g., Gemini API) fails."""
    
    def __init__(
        self,
        message: str = "External service unavailable",
        service_name: str = "unknown",
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details["service"] = service_name
        
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=502,
            details=details
        )


class NotFoundError(FinBroException):
    """Raised when a requested resource is not found."""
    
    def __init__(
        self,
        message: str = "Resource not found",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None
    ):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id
        
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=404,
            details=details
        )
