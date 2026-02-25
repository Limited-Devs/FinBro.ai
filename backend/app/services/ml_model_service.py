
import os
import json
import pickle
import warnings
from typing import Dict, Any, Optional
import numpy as np

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

try:
    import tensorflow as tf
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False

from app.models.exceptions import MLModelError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class MLModelService:
    _instance: Optional['MLModelService'] = None
    _models: Optional[Dict[str, Any]] = None
    _initialized: bool = False
    _model_type: str = 'none'
    _feature_engineer = None
    
    # Legacy TensorFlow model names
    TF_MODEL_NAMES = ['savings', 'amount', 'multi_task']
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, model_dir: str = None):
        if self._initialized:
            return

        self._models = {}
        
        self.model_dir = model_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'model'
        )
        
        # Suppress warnings
        warnings.filterwarnings('ignore', category=UserWarning)
        if HAS_TENSORFLOW:
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
        
        self._load_models()
        self._initialized = True
    
    def _load_models(self) -> None:
        """Load ML models - prefer XGBoost, fallback to TensorFlow."""
        # Try XGBoost first (production model)
        if HAS_XGBOOST and self._try_load_xgboost():
            self._model_type = 'xgboost'
            logger.info("Loaded XGBoost models successfully")
            return
        
        # Fallback to TensorFlow
        if HAS_TENSORFLOW and self._try_load_tensorflow():
            self._model_type = 'tensorflow'
            logger.info("Loaded TensorFlow models successfully")
            return
        
        logger.warning("No ML models could be loaded!")
        self._model_type = 'none'
    
    def _try_load_xgboost(self) -> bool:
        """Try to load XGBoost models."""
        trained_model_dir = os.path.join(self.model_dir, 'trained_model')
        
        classifier_path = os.path.join(trained_model_dir, 'xgb_classifier.json')
        regressor_path = os.path.join(trained_model_dir, 'xgb_regressor.json')
        risk_path = os.path.join(trained_model_dir, 'xgb_risk_classifier.json')
        feature_engineer_path = os.path.join(trained_model_dir, 'feature_engineer.pkl')
        
        if not all(os.path.exists(p) for p in [classifier_path, regressor_path, risk_path]):
            logger.info("XGBoost model files not found")
            return False
        
        try:
            # Load models
            self._models['classifier'] = xgb.XGBClassifier()
            self._models['classifier'].load_model(classifier_path)
            
            self._models['regressor'] = xgb.XGBRegressor()
            self._models['regressor'].load_model(regressor_path)
            
            self._models['risk_classifier'] = xgb.XGBClassifier()
            self._models['risk_classifier'].load_model(risk_path)
            
            # Load feature engineer if available
            if os.path.exists(feature_engineer_path):
                with open(feature_engineer_path, 'rb') as f:
                    self._feature_engineer = pickle.load(f)
                logger.info("Loaded feature engineer")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load XGBoost models: {e}")
            self._models.clear()
            return False
    
    def _try_load_tensorflow(self) -> bool:
        """Try to load TensorFlow models."""
        import tensorflow as tf
        
        for name in self.TF_MODEL_NAMES:
            model_path = os.path.join(
                self.model_dir, 
                f'trained_model/best_{name}_model.keras'
            )
            
            try:
                if os.path.exists(model_path):
                    self._models[name] = tf.keras.models.load_model(model_path, compile=False)
                    logger.info(f"Loaded TensorFlow model: {name}")
            except Exception as e:
                logger.error(f"Failed to load TensorFlow model {name}: {e}")
        
        return len(self._models) > 0
    
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
            if self._model_type == 'xgboost':
                return self._predict_xgboost(features)
            elif self._model_type == 'tensorflow':
                return self._predict_tensorflow(features)
            else:
                raise MLModelError("No models available")
        
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise MLModelError(f"Prediction failed: {str(e)}")
    
    def _predict_xgboost(self, features: np.ndarray) -> Dict[str, Any]:
        """Run predictions using XGBoost models."""
        classifier = self._models['classifier']
        regressor = self._models['regressor']
        risk_classifier = self._models['risk_classifier']
        
        # Get predictions
        can_achieve = classifier.predict(features)[0]
        confidence = classifier.predict_proba(features)[0, 1]
        savings_amount = regressor.predict(features)[0]
        financial_risk = risk_classifier.predict(features)[0]
        risk_score = risk_classifier.predict_proba(features)[0, 1]
        
        return {
            "savings_model": {
                "can_achieve_savings": bool(can_achieve),
                "confidence": float(confidence)
            },
            "amount_model": {
                "recommended_savings": float(savings_amount)
            },
            "multi_task_model": {
                "can_achieve_savings": bool(can_achieve),
                "savings_confidence": float(confidence),
                "recommended_savings_amount": float(savings_amount),
                "financial_risk": bool(financial_risk),
                "risk_score": float(risk_score)
            }
        }
    
    def _predict_tensorflow(self, features: np.ndarray) -> Dict[str, Any]:
        """Run predictions using TensorFlow models."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            predictions = {}
            for name, model in self._models.items():
                predictions[name] = model.predict(features, verbose=0)
            
            return self._format_tensorflow_predictions(predictions)
    
    def _format_tensorflow_predictions(self, predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Format TensorFlow predictions into structured response."""
        result = {}
        
        if 'savings' in predictions:
            result["savings_model"] = {
                "can_achieve_savings": bool(predictions['savings'][0][0] > 0.5),
                "confidence": float(predictions['savings'][0][0])
            }
        
        if 'amount' in predictions:
            result["amount_model"] = {
                "recommended_savings": float(predictions['amount'][0][0])
            }
        
        if 'multi_task' in predictions:
            result["multi_task_model"] = {
                "can_achieve_savings": bool(predictions['multi_task'][0][0][0] > 0.5),
                "savings_confidence": float(predictions['multi_task'][0][0][0]),
                "recommended_savings_amount": float(predictions['multi_task'][1][0][0]),
                "financial_risk": bool(predictions['multi_task'][2][0][0] > 0.5),
                "risk_score": float(predictions['multi_task'][2][0][0])
            }
        
        return result
    
    def check_health(self) -> Dict[str, Any]:
        """
        Check health of ML models.
        
        Returns:
            Health status for each model
        """
        status = {}
        
        if self._model_type == 'xgboost':
            xgb_models = ['classifier', 'regressor', 'risk_classifier']
            for name in xgb_models:
                status[name] = "healthy" if name in self._models else "unhealthy"
        elif self._model_type == 'tensorflow':
            for name in self.TF_MODEL_NAMES:
                status[name] = "healthy" if name in self._models else "unhealthy"
        
        all_healthy = all(s == "healthy" for s in status.values()) if status else False
        
        return {
            "status": "healthy" if all_healthy else "unhealthy",
            "model_type": self._model_type,
            "models": status,
            "model_count": len(self._models)
        }
    
    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (useful for testing)."""
        cls._instance = None
        cls._models = {}
        cls._initialized = False
        cls._model_type = 'none'
        cls._feature_engineer = None
