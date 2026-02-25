"""
Prediction API routes.

Endpoints:
- POST /api/predict - Make a financial prediction
- GET /api/data - Get historical predictions
"""
from flask import Blueprint, request, jsonify, current_app

from app.extensions import limiter
from app.models.schemas import PredictionRequest
from app.services.prediction_service import PredictionService
from app.utils.logging import get_logger
from app.utils.request_helpers import get_user_context

logger = get_logger(__name__)

prediction_bp = Blueprint('prediction', __name__)


@prediction_bp.route('/')
def home():
    service = PredictionService()
    return jsonify({
        "message": "FinBro.ai API",
        "version": "2.0.0",
        "features": service.feature_processor.total_features,
        "status": "running"
    })


@prediction_bp.route('/predict', methods=['POST'])
@limiter.limit(lambda: current_app.config.get('PREDICT_RATE_LIMIT', '10 per minute'))
def predict():
    data = request.get_json()
    if not data:
        return jsonify({
            "error": True,
            "error_code": "INVALID_REQUEST",
            "message": "Request body must be valid JSON"
        }), 400

    prediction_request = PredictionRequest(**data)
    user_id, _ = get_user_context(request)

    result = PredictionService().predict(prediction_request, user_id=user_id)
    return jsonify(result)


@prediction_bp.route('/data', methods=['GET'])
def get_data():
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)

    limit = min(max(1, limit), 1000)
    offset = max(0, offset)

    user_id, _ = get_user_context(request)
    result = PredictionService().get_predictions(user_id=user_id, limit=limit, offset=offset)
    return jsonify(result)


@prediction_bp.route('/data/trends', methods=['GET'])
def get_trends():
    months = request.args.get('months', 6, type=int)
    months = min(max(1, months), 12)

    user_id, _ = get_user_context(request)
    monthly_data = PredictionService().get_monthly_trends(user_id=user_id, months=months)
    return jsonify({
        "monthly_data": monthly_data,
        "total_months": len(monthly_data)
    })
