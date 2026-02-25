
from typing import Dict, Any, Optional, List

from app.models.schemas import PredictionRequest, PredictionResponse
from app.models.exceptions import ValidationError
from app.repositories.prediction_repository import PredictionRepository
from app.services.ml_model_service import MLModelService
from app.utils.feature_processor import FeatureProcessor
from app.utils.logging import get_logger
from app.utils.request_helpers import DEMO_USER_ID
from app.config import get_config
from app.utils.mock_data import generate_mock_predictions, generate_mock_trends

logger = get_logger(__name__)


class PredictionService:
    """
    Service for financial predictions.
    
    Handles:
    - Feature processing
    - Model predictions
    - Result persistence
    
    Uses singleton pattern to avoid repeated initialization.
    """
    
    _instance: 'PredictionService' = None
    _initialized: bool = False
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern to avoid repeated initialization."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the prediction service."""
        if self._initialized:
            return
            
        config = get_config()
        
        self.repository = PredictionRepository(
            enable_fallback=config.ENABLE_JSON_FALLBACK
        )
        self.model_service = MLModelService(model_dir=config.MODEL_DIR)
        self.feature_processor = FeatureProcessor(config.FEATURE_INFO_FILE)
        
        PredictionService._initialized = True
    
    def predict(
        self, 
        request: PredictionRequest,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make a financial prediction.
        
        Args:
            request: Validated prediction request
            user_id: Optional user ID for tracking
        
        Returns:
            Prediction results from all models
        """
        # Convert Pydantic model to dict
        input_data = request.model_dump()
        
        logger.info(
            f"Processing prediction request",
            extra={'extra_data': {'income': input_data['Income'], 'age': input_data['Age']}}
        )
        
        # Process features
        try:
            features = self.feature_processor.process(input_data)
        except KeyError as e:
            raise ValidationError(f"Missing required field: {e}", field=str(e))
        
        # Get predictions
        predictions = self.model_service.predict(features)
        
        # Save to database (async)
        if user_id != DEMO_USER_ID:
            self._save_prediction(input_data, predictions, user_id)
        
        logger.info(
            f"Prediction completed",
            extra={'extra_data': {
                'can_achieve': predictions['savings_model']['can_achieve_savings'],
                'confidence': predictions['savings_model']['confidence']
            }}
        )
        
        return predictions
    
    def _save_prediction(
        self,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        user_id: Optional[str]
    ) -> None:
        """Save prediction to database."""
        try:
            self.repository.create(input_data, output_data, user_id)
        except Exception as e:
            # Log but don't fail the prediction
            logger.warning(f"Failed to save prediction: {e}")
    


    def get_predictions(
        self,
        user_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get historical predictions.
        
        Args:
            user_id: Filter by user ID
            limit: Maximum records to return
            offset: Pagination offset
        
        Returns:
            Dictionary with predictions and metadata
        """
        if user_id == DEMO_USER_ID:
            mock_data = generate_mock_predictions(max(limit, 10))
            paginated_data = mock_data[offset : offset + limit]
            return {
                "total_predictions": len(mock_data),
                "predictions": paginated_data
            }

        predictions = self.repository.get_all(user_id, limit, offset)
        
        return {
            "total_predictions": len(predictions),
            "predictions": predictions
        }
    
    def get_latest_prediction(self, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get the most recent prediction."""
        if user_id == DEMO_USER_ID:
            mock_data = generate_mock_predictions(1)
            return mock_data[0] if mock_data else None
            
        return self.repository.get_latest(user_id)

    def get_monthly_trends(
        self,
        user_id: Optional[str] = None,
        months: int = 6
    ) -> List[Dict[str, Any]]:
        """Get monthly financial trends."""
        if user_id == DEMO_USER_ID:
            return generate_mock_trends(months)
            
        return self.repository.get_monthly_trends(user_id=user_id, months=months)
