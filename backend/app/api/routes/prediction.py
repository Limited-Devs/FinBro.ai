"""
Prediction API routes.

Endpoints:
- POST /api/predict - Make a financial prediction
- GET /api/data - Get historical predictions
"""
from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError as PydanticValidationError

from app.extensions import limiter
from app.models.schemas import PredictionRequest
from app.services.prediction_service import PredictionService
from app.utils.logging import get_logger

logger = get_logger(__name__)

prediction_bp = Blueprint('prediction', __name__)

# Lazy initialization of service
_prediction_service = None


def get_prediction_service() -> PredictionService:
    """Get or create the prediction service."""
    global _prediction_service
    if _prediction_service is None:
        _prediction_service = PredictionService()
    return _prediction_service


@prediction_bp.route('/')
def home():
    """API root endpoint."""
    service = get_prediction_service()
    return jsonify({
        "message": "FinBro.ai API",
        "version": "2.0.0",
        "features": service.feature_processor.total_features,
        "status": "running"
    })


@prediction_bp.route('/predict', methods=['POST'])
@limiter.limit(lambda: current_app.config.get('PREDICT_RATE_LIMIT', '10 per minute'))
def predict():
    """
    Make a financial prediction.
    
    Expects JSON body with all required financial parameters.
    Returns prediction results from all ML models.
    """
    # Get JSON data
    data = request.get_json()
    if not data:
        return jsonify({
            "error": True,
            "error_code": "INVALID_REQUEST",
            "message": "Request body must be valid JSON"
        }), 400
    
    # Validate with Pydantic
    try:
        prediction_request = PredictionRequest(**data)
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
    
    # Get prediction
    service = get_prediction_service()
    result = service.predict(prediction_request)
    
    return jsonify(result)


@prediction_bp.route('/data', methods=['GET'])
def get_data():
    """
    Get historical prediction data.
    
    Query params:
    - limit: Max records (default 100)
    - offset: Pagination offset (default 0)
    """
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Validate pagination params
    limit = min(max(1, limit), 1000)  # 1-1000
    offset = max(0, offset)
    
    service = get_prediction_service()
    result = service.get_predictions(limit=limit, offset=offset)
    
    return jsonify(result)


@prediction_bp.route('/data/trends', methods=['GET'])
def get_trends():
    """
    Get monthly aggregated financial trends for charts.
    
    Query params:
    - months: Number of months of history (default 6, max 12)
    """
    months = request.args.get('months', 6, type=int)
    months = min(max(1, months), 12)  # 1-12
    
    service = get_prediction_service()
    monthly_data = service.repository.get_monthly_trends(months=months)
    
    return jsonify({
        "monthly_data": monthly_data,
        "total_months": len(monthly_data)
    })

