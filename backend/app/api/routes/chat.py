"""
Chat API route.

Endpoints:
- POST /api/chat - Send a message to the AI assistant
"""
from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError as PydanticValidationError

from app.extensions import limiter
from app.models.schemas import ChatRequest
from app.services.chat_service import ChatService
from app.utils.logging import get_logger

logger = get_logger(__name__)

chat_bp = Blueprint('chat', __name__)

# Lazy initialization of service
_chat_service = None


def get_chat_service() -> ChatService:
    """Get or create the chat service."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service


@chat_bp.route('/', methods=['POST'])
@limiter.limit(lambda: current_app.config.get('CHAT_RATE_LIMIT', '30 per minute'))
def chat():
    """
    Send a message to the AI financial advisor.
    
    Expects JSON body with 'message' field.
    Returns AI-generated response.
    """
    data = request.get_json()
    if not data:
        return jsonify({
            "error": True,
            "error_code": "INVALID_REQUEST",
            "message": "Request body must be valid JSON"
        }), 400
    
    # Validate with Pydantic
    try:
        chat_request = ChatRequest(**data)
    except PydanticValidationError as e:
        errors = []
        for err in e.errors():
            field = '.'.join(str(loc) for loc in err['loc'])
            errors.append({
                'field': field,
                'message': err['msg']
            })
        
        return jsonify({
            "error": True,
            "error_code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": {"validation_errors": errors}
        }), 400
    
    # Get chat response
    service = get_chat_service()
    response_text = service.chat(chat_request)
    
    return jsonify({"response": response_text})
