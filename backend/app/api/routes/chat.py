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
from app.utils.request_helpers import format_validation_error, get_user_context

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
        return jsonify(format_validation_error(e)), 400
    
    # Get user context
    user_id, _ = get_user_context(request)
    
    # Get chat response
    service = get_chat_service()
    response_text = service.chat(chat_request, user_id=user_id)
    
    return jsonify({"response": response_text})
