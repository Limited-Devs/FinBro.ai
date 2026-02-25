from flask import Blueprint, request, jsonify, current_app
import os
from supabase import create_client, Client
from dotenv import load_dotenv

from app.extensions import limiter
from app.models.schemas import PredictionRequest
from app.services.prediction_service import PredictionService
from app.utils.logging import get_logger
from app.utils.financial_fields import (
    OCCUPATION_MAPPING,
    EXPENSE_FIELDS,
    VARIABLE_EXPENSE_FIELDS,
)
from app.utils.request_helpers import get_user_context, to_float

load_dotenv()

logger = get_logger(__name__)

onboarding_bp = Blueprint('onboarding', __name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Missing Supabase configuration")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def _normalize_occupation(data: dict) -> None:
    """Map occupation values from frontend labels to backend labels."""
    occupation = data.get('Occupation')
    if occupation is not None:
        data['Occupation'] = OCCUPATION_MAPPING.get(occupation, occupation)


def _add_derived_financial_fields(data: dict) -> None:
    income = to_float(data.get('Income', 0))
    total_expenses = sum(to_float(data.get(field, 0)) for field in EXPENSE_FIELDS)
    data['Disposable_Income'] = max(0, income - total_expenses)

    for field in VARIABLE_EXPENSE_FIELDS:
        savings_field = f'Potential_Savings_{field}'
        if savings_field not in data:
            data[savings_field] = to_float(data.get(field, 0)) * 0.1


def _mark_user_onboarded(supabase: Client, user_id: str) -> None:
    """Set onboarding_completed=true for a user, inserting profile if missing."""
    update_result = (
        supabase.table("user_profiles")
        .update({"onboarding_completed": True})
        .eq("user_id", user_id)
        .execute()
    )

    if not update_result.data:
        supabase.table("user_profiles").insert({
            "user_id": user_id,
            "onboarding_completed": True
        }).execute()


def _get_profile_status(supabase: Client, user_id: str) -> bool:
    """Fetch onboarding status; create default profile when missing."""
    result = (
        supabase.table("user_profiles")
        .select("onboarding_completed")
        .eq("user_id", user_id)
        .execute()
    )

    if result.data:
        return bool(result.data[0].get("onboarding_completed", False))

    try:
        supabase.table("user_profiles").insert({
            "user_id": user_id,
            "onboarding_completed": False
        }).execute()
    except Exception as insert_err:
        logger.warning(f"Could not create user profile: {insert_err}")

    return False


@onboarding_bp.route('/user/status', methods=['GET'])
def get_user_status():
    """
    Get user onboarding status.
    
    Returns:
        { onboarding_completed: boolean }
    """
    user_id, is_demo = get_user_context(request)
    
    # Demo users are always "onboarded"
    if is_demo:
        return jsonify({
            "onboarding_completed": True,
            "is_demo": True
        })
    
    if not user_id:
        return jsonify({
            "error": True,
            "message": "User ID required"
        }), 401
    
    try:
        supabase = get_supabase_client()
        onboarding_completed = _get_profile_status(supabase, user_id)
        return jsonify({
            "onboarding_completed": onboarding_completed,
            "is_demo": False
        })

    except Exception as e:
        logger.error(f"Error checking user status: {e}")
        return jsonify({
            "onboarding_completed": False,
            "is_demo": False,
            "error": str(e)
        })


@onboarding_bp.route('/onboarding', methods=['POST'])
@limiter.limit(lambda: current_app.config.get('PREDICT_RATE_LIMIT', '10 per minute'))
def complete_onboarding():
    """
    Complete user onboarding with financial profile.
    
    This endpoint:
    1. Validates the financial profile data
    2. Calculates derived fields (Disposable_Income, Potential_Savings)
    3. Processes it through ML models
    4. Saves the prediction to the database
    5. Marks the user as onboarded
    
    Returns prediction results.
    """
    user_id, is_demo = get_user_context(request)
    
    if is_demo:
        return jsonify({
            "error": True,
            "message": "Demo users cannot complete onboarding"
        }), 400
    
    if not user_id:
        return jsonify({
            "error": True,
            "message": "User ID required"
        }), 401
    
    data = request.get_json()
    if not data:
        return jsonify({
            "error": True,
            "error_code": "INVALID_REQUEST",
            "message": "Request body must be valid JSON"
        }), 400

    try:
        _normalize_occupation(data)
        _add_derived_financial_fields(data)
    except (ValueError, TypeError) as e:
        logger.error(f"Error calculating derived fields: {e}")
        return jsonify({
            "error": True,
            "error_code": "CALCULATION_ERROR",
            "message": f"Error calculating financial metrics: {str(e)}"
        }), 400
    
    prediction_request = PredictionRequest(**data)

    try:
        prediction_result = PredictionService().predict(prediction_request, user_id=user_id)

        supabase = get_supabase_client()
        try:
            _mark_user_onboarded(supabase, user_id)
        except Exception as profile_err:
            logger.warning(f"Could not update user profile: {profile_err}")

        logger.info(f"User {user_id} completed onboarding")

        return jsonify({
            "success": True,
            "onboarding_completed": True,
            "prediction": prediction_result
        })

    except Exception as e:
        logger.error(f"Error during onboarding: {e}")
        return jsonify({
            "error": True,
            "message": f"Failed to complete onboarding: {str(e)}"
        }), 500
