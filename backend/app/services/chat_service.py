"""
Chat service for AI-powered financial advice.

Integrates with Google Gemini API for natural language responses.
"""
import os
from typing import Optional, Dict, Any

from google import genai

from app.models.schemas import ChatRequest
from app.models.exceptions import ExternalServiceError, NotFoundError
from app.repositories.prediction_repository import PredictionRepository
from app.utils.logging import get_logger
from app.utils.request_helpers import DEMO_USER_ID
from app.utils.mock_data import generate_mock_predictions
from app.config import get_config

logger = get_logger(__name__)


class ChatService:
    """
    Service for AI chat functionality.
    
    Provides context-aware financial advice using Gemini.
    """
    
    def __init__(self):
        """Initialize the chat service."""
        config = get_config()
        
        self.api_key = config.GEMINI_API_KEY
        self.model_name = config.GEMINI_MODEL
        self.max_tokens = config.GEMINI_MAX_TOKENS
        self.temperature = config.GEMINI_TEMPERATURE
        
        if not self.api_key:
            raise ExternalServiceError(
                "Gemini API key not configured",
                service_name="gemini"
            )
        
        self.client = genai.Client(api_key=self.api_key)
        self.repository = PredictionRepository(
            enable_fallback=config.ENABLE_JSON_FALLBACK
        )
    
    def chat(self, request: ChatRequest, user_id: Optional[str] = None) -> str:
        """
        Process a chat message and return AI response.
        
        Args:
            request: Chat request with user message
            user_id: Optional user ID for context
        
        Returns:
            AI-generated response string
        """
        message = request.message
        
        logger.info(
            f"Processing chat request",
            extra={'extra_data': {'message_length': len(message)}}
        )
        
        # Get latest prediction for context
        latest = self._get_user_context(user_id)
        
        if not latest:
            return (
                "I don't have any saved financial data yet. "
                "Please make a savings prediction first!"
            )
        
        # Build prompt with financial context
        prompt = self._build_prompt(message, latest)
        
        # Get response from Gemini
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )

            # Ensure the AI returned a non-empty response; treat empty as an error.
            text = getattr(response, "text", None)
            if text is None or not str(text).strip():
                logger.error(
                    "Gemini API returned an empty response",
                    extra={"extra_data": {"prompt_length": len(prompt)}},
                )
                raise ExternalServiceError(
                    "Received empty response from Gemini",
                    service_name="gemini",
                    details={"reason": "empty_response"},
                )

            ai_response = str(text)

            logger.info(
                f"Chat response generated",
                extra={'extra_data': {'response_length': len(ai_response)}}
            )

            return ai_response
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise ExternalServiceError(
                "Failed to generate AI response",
                service_name="gemini",
                details={"error": str(e)}
            )
    
    def _get_user_context(self, user_id: Optional[str]) -> Optional[Dict[str, Any]]:
        """Get latest prediction for user context."""
        if user_id == DEMO_USER_ID:
            mock_data = generate_mock_predictions(1)
            if mock_data:
                return {
                    "input": mock_data[0].get("input_data", {}),
                    "output": mock_data[0].get("output_data", {})
                }
            return None
        
        try:
            latest = self.repository.get_latest(user_id)
            
            if latest:
                # Normalize the data structure
                if "input_data" in latest:
                    return {
                        "input": latest["input_data"],
                        "output": latest["output_data"]
                    }
                return latest
            
            return None
        
        except Exception as e:
            logger.warning(f"Failed to get user context: {e}")
            return None
    
    def _build_prompt(self, user_message: str, context: Dict[str, Any]) -> str:
        """Build the full prompt with financial context."""
        input_data = context.get("input", {})
        output_data = context.get("output", {})
        
        savings_model = output_data.get("savings_model", {})
        amount_model = output_data.get("amount_model", {})
        multi_task = output_data.get("multi_task_model", {})
        
        can_achieve = savings_model.get('can_achieve_savings', False)
        confidence = savings_model.get('confidence', 0) * 100
        recommended = amount_model.get('recommended_savings', 0)
        has_risk = multi_task.get('financial_risk', False)
        
        return f"""
You are a Personal Finance Advisor chatbot.
The user recently submitted this financial profile:

Income: ₹{input_data.get("Income", "N/A")}
Age: {input_data.get("Age", "N/A")}
Occupation: {input_data.get("Occupation", "N/A")}
City Tier: {input_data.get("City_Tier", "N/A")}
Dependents: {input_data.get("Dependents", "N/A")}

Monthly Expenses:
Rent: ₹{input_data.get("Rent", "N/A")}
Groceries: ₹{input_data.get("Groceries", "N/A")}
Transport: ₹{input_data.get("Transport", "N/A")}
Eating Out: ₹{input_data.get("Eating_Out", "N/A")}
Utilities: ₹{input_data.get("Utilities", "N/A")}
Healthcare: ₹{input_data.get("Healthcare", "N/A")}
Education: ₹{input_data.get("Education", "N/A")}
Miscellaneous: ₹{input_data.get("Miscellaneous", "N/A")}

Savings Goals:
Desired Savings %: {input_data.get("Desired_Savings_Percentage", "N/A")}%
Disposable Income: ₹{input_data.get("Disposable_Income", "N/A")}

Prediction Results:
Can Achieve Savings: {'✅ Yes' if can_achieve else '❌ No'}
Confidence: {confidence:.2f}%
Recommended Monthly Savings: ₹{recommended:,.2f}
Financial Risk: {'⚠️ Yes' if has_risk else '✅ No'}

Now the user is asking:
"{user_message}"

Instructions:
- For greetings/casual talk: Respond naturally and friendly
- For finance questions: Use their data to give personalized advice
- For general questions: Answer normally without forcing financial data
- Keep all responses under 100 words and conversational
- Always give response in plain text, do not use any ** or formatting
"""
