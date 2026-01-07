"""
ML Model service for loading and running predictions.

Features:
- Singleton pattern for model loading
- Lazy initialization
- Model health checks
"""
import os
import warnings
from typing import Dict, Any, Optional
import numpy as np
import tensorflow as tf

from app.models.exceptions import MLModelError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class MLModelService:
    """
    Service for ML model operations.
    
    Uses singleton pattern to ensure models are loaded only once.
    """
    
    _instance: Optional['MLModelService'] = None
    _models: Dict[str, tf.keras.Model] = {}
    _initialized: bool = False
    
    MODEL_NAMES = ['savings', 'amount', 'multi_task']
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, model_dir: str = None):
        """
        Initialize the ML model service.
        
        Args:
            model_dir: Directory containing trained models
        """
        if self._initialized:
            return
        
        self.model_dir = model_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'model'
        )
        
        # Suppress TensorFlow warnings
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
        warnings.filterwarnings('ignore', category=UserWarning, module='keras')
        
        self._load_models()
        self._initialized = True
    
    def _load_models(self) -> None:
        """Load all ML models."""
        for name in self.MODEL_NAMES:
            model_path = os.path.join(
                self.model_dir, 
                f'trained_model/best_{name}_model.keras'
            )
            
            try:
                self._models[name] = tf.keras.models.load_model(model_path, compile=False)
                logger.info(f"Loaded model: {name}")
            except Exception as e:
                logger.error(f"Failed to load model {name}: {e}")
                raise MLModelError(
                    message=f"Failed to load ML model: {name}",
                    model_name=name
                )
    
    def predict(self, features: np.ndarray) -> Dict[str, Any]:
        """
        Run predictions on all models.
        
        Args:
            features: Feature array of shape (1, num_features)
        
        Returns:
            Dictionary with predictions from all models
        """
        if not self._models:
            raise MLModelError("Models not loaded")
        
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                predictions = {}
                for name, model in self._models.items():
                    predictions[name] = model.predict(features, verbose=0)
                
                return self._format_predictions(predictions)
        
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise MLModelError(f"Prediction failed: {str(e)}")
    
    def _format_predictions(self, predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Format raw predictions into structured response."""
        return {
            "savings_model": {
                "can_achieve_savings": bool(predictions['savings'][0][0] > 0.5),
                "confidence": float(predictions['savings'][0][0])
            },
            "amount_model": {
                "recommended_savings": float(predictions['amount'][0][0])
            },
            "multi_task_model": {
                "can_achieve_savings": bool(predictions['multi_task'][0][0][0] > 0.5),
                "savings_confidence": float(predictions['multi_task'][0][0][0]),
                "recommended_savings_amount": float(predictions['multi_task'][1][0][0]),
                "financial_risk": bool(predictions['multi_task'][2][0][0] > 0.5),
                "risk_score": float(predictions['multi_task'][2][0][0])
            }
        }
    
    def check_health(self) -> Dict[str, Any]:
        """
        Check health of ML models.
        
        Returns:
            Health status for each model
        """
        status = {}
        for name in self.MODEL_NAMES:
            status[name] = "healthy" if name in self._models else "unhealthy"
        
        return {
            "status": "healthy" if all(s == "healthy" for s in status.values()) else "unhealthy",
            "models": status,
            "model_count": len(self._models)
        }
    
    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (useful for testing)."""
        cls._instance = None
        cls._models = {}
        cls._initialized = False
