"""
Health check API route.

Endpoints:
- GET /api/health - Check application health
"""
import time
from flask import Blueprint, jsonify, current_app

from app.services.ml_model_service import MLModelService
from app.repositories.prediction_repository import PredictionRepository
from app.utils.logging import get_logger

logger = get_logger(__name__)

health_bp = Blueprint('health', __name__)

# Track app start time
_start_time = time.time()


@health_bp.route('/health')
def health():
    """
    Comprehensive health check endpoint.
    
    Returns status of:
    - Overall application
    - ML models
    - Database connection
    """
    components = {}
    overall_status = "healthy"
    
    # Check ML models
    try:
        model_service = MLModelService()
        ml_health = model_service.check_health()
        components["ml_models"] = {
            "status": ml_health["status"],
            "message": f"{ml_health['model_count']} models loaded"
        }
        if ml_health["status"] != "healthy":
            overall_status = "degraded"
    except Exception as e:
        components["ml_models"] = {
            "status": "unhealthy",
            "message": str(e)
        }
        overall_status = "unhealthy"
    
    # Check database
    try:
        repo = PredictionRepository()
        db_health = repo.check_health()
        
        if db_health["supabase"] == "healthy":
            components["database"] = {
                "status": "healthy",
                "message": "Supabase connected"
            }
        elif db_health["json_fallback"] == "healthy":
            components["database"] = {
                "status": "degraded",
                "message": "Using JSON fallback"
            }
            if overall_status == "healthy":
                overall_status = "degraded"
        else:
            components["database"] = {
                "status": "unhealthy",
                "message": "No storage available"
            }
            overall_status = "unhealthy"
    except Exception as e:
        components["database"] = {
            "status": "unhealthy",
            "message": str(e)
        }
        overall_status = "unhealthy"
    
    # Calculate uptime
    uptime = time.time() - _start_time
    
    return jsonify({
        "status": overall_status,
        "version": "2.0.0",
        "environment": current_app.config.get('ENV', 'development'),
        "components": components,
        "uptime_seconds": round(uptime, 2)
    })
