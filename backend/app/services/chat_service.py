from typing import Optional, Dict, Any

from google import genai

from app.models.schemas import ChatRequest
from app.models.exceptions import ExternalServiceError
from app.repositories.prediction_repository import PredictionRepository
from app.utils.logging import get_logger
from app.utils.request_helpers import DEMO_USER_ID, to_float
from app.utils.mock_data import generate_mock_predictions
from app.config import get_config

logger = get_logger(__name__)


class ChatService:
    NO_CONTEXT_RESPONSE = (
        "I don't have any saved financial data yet. "
        "Please make a savings prediction first!"
    )

    PROMPT_INSTRUCTIONS = """Instructions:
- For greetings/casual talk: Respond naturally and friendly
- For finance questions: Use their data to give personalized advice
- For general questions: Answer normally without forcing financial data
- Keep all responses under 100 words and conversational
- Always give response in plain text, do not use any ** or formatting"""
    
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
        
        latest = self._get_user_context(user_id)
        if not latest:
            return self.NO_CONTEXT_RESPONSE

        prompt = self._build_prompt(message, latest)
        return self._generate_ai_response(prompt)
    
    def _get_user_context(self, user_id: Optional[str]) -> Optional[Dict[str, Any]]:
        """Get latest prediction for user context."""
        if user_id == DEMO_USER_ID:
            return self._get_demo_context()
        
        try:
            latest = self.repository.get_latest(user_id)
            return self._normalize_context(latest) if latest else None
        
        except Exception as e:
            logger.warning(f"Failed to get user context: {e}")
            return None

    def _get_demo_context(self) -> Optional[Dict[str, Any]]:
        """Get mock prediction context for demo users."""
        mock_data = generate_mock_predictions(1)
        if not mock_data:
            return None

        return {
            "input": mock_data[0].get("input_data", {}),
            "output": mock_data[0].get("output_data", {})
        }

    def _normalize_context(self, raw_context: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize repository data into a consistent input/output structure."""
        if "input_data" in raw_context:
            return {
                "input": raw_context.get("input_data", {}),
                "output": raw_context.get("output_data", {})
            }

        return {
            "input": raw_context.get("input", {}),
            "output": raw_context.get("output", {})
        }
    
    def _build_prompt(self, user_message: str, context: Dict[str, Any]) -> str:
        """Build the full prompt with financial context."""
        input_data = context.get("input", {})
        output_data = context.get("output", {})

        return f"""
You are a Personal Finance Advisor chatbot.
The user recently submitted this financial profile:

{self._build_profile_section(input_data)}

Monthly Expenses:
{self._build_expense_section(input_data)}

Savings Goals:
{self._build_savings_section(input_data)}

Prediction Results:
{self._build_prediction_section(output_data)}

Now the user is asking:
"{user_message}"

{self.PROMPT_INSTRUCTIONS}
"""

    def _build_profile_section(self, input_data: Dict[str, Any]) -> str:
        """Format profile attributes for the LLM prompt."""
        return (
            f"Income: ₹{input_data.get('Income', 'N/A')}\n"
            f"Age: {input_data.get('Age', 'N/A')}\n"
            f"Occupation: {input_data.get('Occupation', 'N/A')}\n"
            f"City Tier: {input_data.get('City_Tier', 'N/A')}\n"
            f"Dependents: {input_data.get('Dependents', 'N/A')}"
        )

    def _build_expense_section(self, input_data: Dict[str, Any]) -> str:
        """Format monthly expense lines for the LLM prompt."""
        return (
            f"Rent: ₹{input_data.get('Rent', 'N/A')}\n"
            f"Groceries: ₹{input_data.get('Groceries', 'N/A')}\n"
            f"Transport: ₹{input_data.get('Transport', 'N/A')}\n"
            f"Eating Out: ₹{input_data.get('Eating_Out', 'N/A')}\n"
            f"Utilities: ₹{input_data.get('Utilities', 'N/A')}\n"
            f"Healthcare: ₹{input_data.get('Healthcare', 'N/A')}\n"
            f"Education: ₹{input_data.get('Education', 'N/A')}\n"
            f"Miscellaneous: ₹{input_data.get('Miscellaneous', 'N/A')}"
        )

    def _build_savings_section(self, input_data: Dict[str, Any]) -> str:
        """Format savings goal lines for the LLM prompt."""
        return (
            f"Desired Savings %: {input_data.get('Desired_Savings_Percentage', 'N/A')}%\n"
            f"Disposable Income: ₹{input_data.get('Disposable_Income', 'N/A')}"
        )

    def _build_prediction_section(self, output_data: Dict[str, Any]) -> str:
        """Format model outputs for the LLM prompt."""
        savings_model = output_data.get("savings_model", {})
        amount_model = output_data.get("amount_model", {})
        multi_task = output_data.get("multi_task_model", {})

        can_achieve = "✅ Yes" if savings_model.get("can_achieve_savings") else "❌ No"
        confidence = to_float(savings_model.get("confidence")) * 100
        recommended = to_float(amount_model.get("recommended_savings"))
        has_risk = "⚠️ Yes" if multi_task.get("financial_risk") else "✅ No"

        return (
            f"Can Achieve Savings: {can_achieve}\n"
            f"Confidence: {confidence:.2f}%\n"
            f"Recommended Monthly Savings: ₹{recommended:,.2f}\n"
            f"Financial Risk: {has_risk}"
        )

    def _generate_ai_response(self, prompt: str) -> str:
        """Generate and validate AI response from Gemini."""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            ai_response = self._extract_response_text(response, prompt)

            logger.info(
                f"Chat response generated",
                extra={"extra_data": {"response_length": len(ai_response)}}
            )

            return ai_response
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise ExternalServiceError(
                "Failed to generate AI response",
                service_name="gemini",
                details={"error": str(e)}
            )

    def _extract_response_text(self, response: Any, prompt: str) -> str:
        """Extract non-empty text from Gemini response."""
        text = getattr(response, "text", None)
        if text is None or not str(text).strip():
            logger.error(
                "Gemini API returned an empty response",
                extra={"extra_data": {"prompt_length": len(prompt)}}
            )
            raise ExternalServiceError(
                "Received empty response from Gemini",
                service_name="gemini",
                details={"reason": "empty_response"}
            )

        return str(text)

