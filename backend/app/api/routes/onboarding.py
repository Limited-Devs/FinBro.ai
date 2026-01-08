"""
Onboarding API routes.

Endpoints:
- GET /api/user/status - Get user onboarding status
- POST /api/onboarding - Complete onboarding with financial profile
"""
from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError as PydanticValidationError
import os
from supabase import create_client, Client
from dotenv import load_dotenv

from app.extensions import limiter
from app.models.schemas import PredictionRequest
from app.services.prediction_service import PredictionService
from app.utils.logging import get_logger

load_dotenv()

logger = get_logger(__name__)

onboarding_bp = Blueprint('onboarding', __name__)

# Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

def get_supabase_client() -> Client:
    """Get Supabase client."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Missing Supabase configuration")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Lazy initialization of prediction service
_prediction_service = None

def get_prediction_service() -> PredictionService:
    """Get or create the prediction service."""
    global _prediction_service
    if _prediction_service is None:
        _prediction_service = PredictionService()
    return _prediction_service


@onboarding_bp.route('/user/status', methods=['GET'])
def get_user_status():
    """
    Get user onboarding status.
    
    Returns:
        { onboarding_completed: boolean }
    """
    user_id = request.headers.get('X-User-ID')
    is_demo = request.headers.get('X-Demo-Mode', 'false').lower() == 'true'
    
    # Demo users are always "onboarded"
    if is_demo or user_id == 'demo':
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
        
        # Check user_profiles table
        result = supabase.table("user_profiles")\
            .select("onboarding_completed")\
            .eq("user_id", user_id)\
            .execute()
        
        if result.data and len(result.data) > 0:
            return jsonify({
                "onboarding_completed": result.data[0].get("onboarding_completed", False),
                "is_demo": False
            })
        
        # No profile found - user hasn't completed onboarding
        # Try to create a profile entry for them
        try:
            supabase.table("user_profiles").insert({
                "user_id": user_id,
                "onboarding_completed": False
            }).execute()
        except Exception as insert_err:
            logger.warning(f"Could not create user profile: {insert_err}")
        
        return jsonify({
            "onboarding_completed": False,
            "is_demo": False
        })
        
    except Exception as e:
        logger.error(f"Error checking user status: {e}")
        # On error, assume not onboarded to be safe
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
    user_id = request.headers.get('X-User-ID')
    is_demo = request.headers.get('X-Demo-Mode', 'false').lower() == 'true'
    
    if is_demo or user_id == 'demo':
        return jsonify({
            "error": True,
            "message": "Demo users cannot complete onboarding"
        }), 400
    
    if not user_id:
        return jsonify({
            "error": True,
            "message": "User ID required"
        }), 401
    
    # Get JSON data
    data = request.get_json()
    if not data:
        return jsonify({
            "error": True,
            "error_code": "INVALID_REQUEST",
            "message": "Request body must be valid JSON"
        }), 400
    
    # Map occupation from frontend format to backend format
    occupation_mapping = {
        'Employed': 'Salaried',
        'Self_Employed': 'Self_Employed',
        'Student': 'Student',
        'Retired': 'Retired',
        # Also accept backend format directly
        'Salaried': 'Salaried'
    }
    if 'Occupation' in data:
        data['Occupation'] = occupation_mapping.get(data['Occupation'], data['Occupation'])
    
    # Calculate derived fields that the onboarding form doesn't provide
    try:
        income = float(data.get('Income', 0))
        
        # Calculate total expenses
        expense_fields = ['Rent', 'Loan_Repayment', 'Insurance', 'Groceries', 
                         'Transport', 'Eating_Out', 'Entertainment', 'Utilities',
                         'Healthcare', 'Education', 'Miscellaneous']
        total_expenses = sum(float(data.get(field, 0)) for field in expense_fields)
        
        # Calculate disposable income
        data['Disposable_Income'] = max(0, income - total_expenses)
        
        # Calculate potential savings (10% of each variable expense as potential savings)
        variable_expense_fields = ['Groceries', 'Transport', 'Eating_Out', 'Entertainment',
                                   'Utilities', 'Healthcare', 'Education', 'Miscellaneous']
        for field in variable_expense_fields:
            savings_field = f'Potential_Savings_{field}'
            if savings_field not in data:
                # Estimate 10% potential savings for each variable expense
                data[savings_field] = float(data.get(field, 0)) * 0.1
                
    except (ValueError, TypeError) as e:
        logger.error(f"Error calculating derived fields: {e}")
        return jsonify({
            "error": True,
            "error_code": "CALCULATION_ERROR",
            "message": f"Error calculating financial metrics: {str(e)}"
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
        
        logger.warning(f"Onboarding validation failed for user {user_id}: {errors}")
        return jsonify({
            "error": True,
            "error_code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": {"validation_errors": errors}
        }), 400
    
    try:
        # Get prediction from ML models
        service = get_prediction_service()
        prediction_result = service.predict(prediction_request, user_id=user_id)
        
        # Mark user as onboarded
        supabase = get_supabase_client()
        
        # Update or insert user profile
        try:
            # Try update first
            update_result = supabase.table("user_profiles")\
                .update({"onboarding_completed": True})\
                .eq("user_id", user_id)\
                .execute()
            
            # If no rows updated, insert
            if not update_result.data or len(update_result.data) == 0:
                supabase.table("user_profiles").insert({
                    "user_id": user_id,
                    "onboarding_completed": True
                }).execute()
                
        except Exception as profile_err:
            logger.warning(f"Could not update user profile: {profile_err}")
            # Continue anyway - prediction was saved
        
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
