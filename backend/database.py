import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_ANON_KEY in environment variables")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class DatabaseService:
    """Service class for database operations"""
    
    @staticmethod
    def create_prediction(prediction_data):
        """Insert a new prediction record into the predictions table"""
        try:
            # Extract input and output data
            input_data = prediction_data["input"]
            output_data = prediction_data["output"]
            
            # Map input data to table columns
            data = {
                "timestamp": prediction_data["timestamp"],
                "user_id": None,  # Will be set when user auth is implemented
                
                # Basic financial info from input
                "income": float(input_data.get("Income", 0)),
                "age": int(input_data.get("Age", 0)),
                "dependents": int(input_data.get("Dependents", 0)),
                "occupation": input_data.get("Occupation"),
                "city_tier": input_data.get("City_Tier"),
                
                # Expenses from input
                "rent": float(input_data.get("Rent", 0)),
                "loan_repayment": float(input_data.get("Loan_Repayment", 0)),
                "insurance": float(input_data.get("Insurance", 0)),
                "groceries": float(input_data.get("Groceries", 0)),
                "transport": float(input_data.get("Transport", 0)),
                "eating_out": float(input_data.get("Eating_Out", 0)),
                "entertainment": float(input_data.get("Entertainment", 0)),
                "utilities": float(input_data.get("Utilities", 0)),
                "healthcare": float(input_data.get("Healthcare", 0)),
                "education": float(input_data.get("Education", 0)),
                "miscellaneous": float(input_data.get("Miscellaneous", 0)),
                
                # Calculated financial metrics from input
                "desired_savings_percentage": float(input_data.get("Desired_Savings_Percentage", 0)),
                "disposable_income": float(input_data.get("Disposable_Income", 0)),
                "savings_rate": float(input_data.get("Savings_Rate", 0)),
                "actual_savings_potential": float(input_data.get("Actual_Savings_Potential", 0)),
                "essential_expenses": float(input_data.get("Essential_Expenses", 0)),
                "essential_expense_ratio": float(input_data.get("Essential_Expense_Ratio", 0)),
                "non_essential_income": float(input_data.get("Non_Essential_Income", 0)),
                "expense_efficiency": float(input_data.get("Expense_Efficiency", 0)),
                "total_expenses": float(input_data.get("Total_Expenses", 0)),
                "debt_to_income_ratio": float(input_data.get("Debt_to_Income_Ratio", 0)),
                "financial_stress_score": float(input_data.get("Financial_Stress_Score", 0)),
                
                # Potential savings from input
                "potential_savings_groceries": float(input_data.get("Potential_Savings_Groceries", 0)),
                "potential_savings_transport": float(input_data.get("Potential_Savings_Transport", 0)),
                "potential_savings_eating_out": float(input_data.get("Potential_Savings_Eating_Out", 0)),
                "potential_savings_entertainment": float(input_data.get("Potential_Savings_Entertainment", 0)),
                "potential_savings_utilities": float(input_data.get("Potential_Savings_Utilities", 0)),
                "potential_savings_healthcare": float(input_data.get("Potential_Savings_Healthcare", 0)),
                "potential_savings_education": float(input_data.get("Potential_Savings_Education", 0)),
                "potential_savings_miscellaneous": float(input_data.get("Potential_Savings_Miscellaneous", 0)),
                
                # Categorical encodings from input
                "occupation_retired": int(input_data.get("Occupation_Retired", 0)),
                "occupation_self_employed": int(input_data.get("Occupation_Self_Employed", 0)),
                "occupation_student": int(input_data.get("Occupation_Student", 0)),
                "city_tier_tier_2": int(input_data.get("City_Tier_Tier_2", 0)),
                "city_tier_tier_3": int(input_data.get("City_Tier_Tier_3", 0)),
                "age_group_mid_career": int(input_data.get("Age_Group_Mid_Career", 0)),
                "age_group_pre_retirement": int(input_data.get("Age_Group_Pre_Retirement", 0)),
                "age_group_senior": int(input_data.get("Age_Group_Senior", 0)),
                "age_group_young_adult": int(input_data.get("Age_Group_Young_Adult", 0)),
                "income_bracket_low_income": int(input_data.get("Income_Bracket_Low_Income", 0)),
                "income_bracket_lower_mid": int(input_data.get("Income_Bracket_Lower_Mid", 0)),
                "income_bracket_middle": int(input_data.get("Income_Bracket_Middle", 0)),
                "income_bracket_upper_mid": int(input_data.get("Income_Bracket_Upper_Mid", 0)),
                "savings_difficulty_moderate": int(input_data.get("Savings_Difficulty_Moderate", 0)),
                "savings_difficulty_very_hard": int(input_data.get("Savings_Difficulty_Very_Hard", 0)),
                "savings_difficulty_nan": int(input_data.get("Savings_Difficulty_nan", 0)),
                
                # ML model predictions from output
                "savings_model_can_achieve": output_data.get("savings_model", {}).get("can_achieve_savings"),
                "savings_model_confidence": float(output_data.get("savings_model", {}).get("confidence", 0)),
                "amount_model_recommended_savings": float(output_data.get("amount_model", {}).get("recommended_savings", 0)),
                "multi_task_can_achieve": output_data.get("multi_task_model", {}).get("can_achieve_savings"),
                "multi_task_savings_confidence": float(output_data.get("multi_task_model", {}).get("savings_confidence", 0)),
                "multi_task_recommended_amount": float(output_data.get("multi_task_model", {}).get("recommended_savings_amount", 0)),
                "multi_task_financial_risk": output_data.get("multi_task_model", {}).get("financial_risk"),
                "multi_task_risk_score": float(output_data.get("multi_task_model", {}).get("risk_score", 0))
            }
            
            result = supabase.table("predictions").insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating prediction: {e}")
            return None
    
    @staticmethod
    def get_user_predictions(user_id=None):
        """Get all predictions for a user"""
        try:
            query = supabase.table("predictions").select("*").order("timestamp", desc=True)
            
            # If user_id is provided and not None, filter by it
            if user_id is not None:
                query = query.eq("user_id", user_id)
            
            result = query.execute()
            
            # Transform back to expected format
            formatted_predictions = []
            for pred in result.data:
                # Reconstruct input data from individual columns
                input_data = {
                    "Income": pred["income"],
                    "Age": pred["age"],
                    "Dependents": pred["dependents"],
                    "Occupation": pred["occupation"],
                    "City_Tier": pred["city_tier"],
                    "Rent": pred["rent"],
                    "Loan_Repayment": pred["loan_repayment"],
                    "Insurance": pred["insurance"],
                    "Groceries": pred["groceries"],
                    "Transport": pred["transport"],
                    "Eating_Out": pred["eating_out"],
                    "Entertainment": pred["entertainment"],
                    "Utilities": pred["utilities"],
                    "Healthcare": pred["healthcare"],
                    "Education": pred["education"],
                    "Miscellaneous": pred["miscellaneous"],
                    "Desired_Savings_Percentage": pred["desired_savings_percentage"],
                    "Disposable_Income": pred["disposable_income"],
                    "Potential_Savings_Groceries": pred["potential_savings_groceries"],
                    "Potential_Savings_Transport": pred["potential_savings_transport"],
                    "Potential_Savings_Eating_Out": pred["potential_savings_eating_out"],
                    "Potential_Savings_Entertainment": pred["potential_savings_entertainment"],
                    "Potential_Savings_Utilities": pred["potential_savings_utilities"],
                    "Potential_Savings_Healthcare": pred["potential_savings_healthcare"],
                    "Potential_Savings_Education": pred["potential_savings_education"],
                    "Potential_Savings_Miscellaneous": pred["potential_savings_miscellaneous"],
                    "Savings_Rate": pred["savings_rate"],
                    "Actual_Savings_Potential": pred["actual_savings_potential"],
                    "Essential_Expenses": pred["essential_expenses"],
                    "Essential_Expense_Ratio": pred["essential_expense_ratio"],
                    "Non_Essential_Income": pred["non_essential_income"],
                    "Expense_Efficiency": pred["expense_efficiency"],
                    "Total_Expenses": pred["total_expenses"],
                    "Debt_to_Income_Ratio": pred["debt_to_income_ratio"],
                    "Financial_Stress_Score": pred["financial_stress_score"],
                    "Occupation_Retired": pred["occupation_retired"],
                    "Occupation_Self_Employed": pred["occupation_self_employed"],
                    "Occupation_Student": pred["occupation_student"],
                    "City_Tier_Tier_2": pred["city_tier_tier_2"],
                    "City_Tier_Tier_3": pred["city_tier_tier_3"],
                    "Age_Group_Mid_Career": pred["age_group_mid_career"],
                    "Age_Group_Pre_Retirement": pred["age_group_pre_retirement"],
                    "Age_Group_Senior": pred["age_group_senior"],
                    "Age_Group_Young_Adult": pred["age_group_young_adult"],
                    "Income_Bracket_Low_Income": pred["income_bracket_low_income"],
                    "Income_Bracket_Lower_Mid": pred["income_bracket_lower_mid"],
                    "Income_Bracket_Middle": pred["income_bracket_middle"],
                    "Income_Bracket_Upper_Mid": pred["income_bracket_upper_mid"],
                    "Savings_Difficulty_Moderate": pred["savings_difficulty_moderate"],
                    "Savings_Difficulty_Very_Hard": pred["savings_difficulty_very_hard"],
                    "Savings_Difficulty_nan": pred["savings_difficulty_nan"]
                }
                
                # Reconstruct output data from ML prediction columns
                output_data = {
                    "savings_model": {
                        "can_achieve_savings": pred["savings_model_can_achieve"],
                        "confidence": pred["savings_model_confidence"]
                    },
                    "amount_model": {
                        "recommended_savings": pred["amount_model_recommended_savings"]
                    },
                    "multi_task_model": {
                        "can_achieve_savings": pred["multi_task_can_achieve"],
                        "savings_confidence": pred["multi_task_savings_confidence"],
                        "recommended_savings_amount": pred["multi_task_recommended_amount"],
                        "financial_risk": pred["multi_task_financial_risk"],
                        "risk_score": pred["multi_task_risk_score"]
                    }
                }
                
                formatted_predictions.append({
                    "id": pred["id"],
                    "timestamp": pred["timestamp"],
                    "input_data": input_data,
                    "output_data": output_data
                })
            
            return formatted_predictions
        except Exception as e:
            print(f"Error fetching predictions: {e}")
            return []
    
    @staticmethod
    def get_latest_prediction(user_id=None):
        """Get the most recent prediction for a user"""
        try:
            predictions = DatabaseService.get_user_predictions(user_id)
            return predictions[0] if predictions else None
        except Exception as e:
            print(f"Error fetching latest prediction: {e}")
            return None
    
    @staticmethod
    def delete_prediction(prediction_id):
        """Delete a prediction by ID"""
        try:
            result = supabase.table("predictions")\
                .delete()\
                .eq("id", prediction_id)\
                .execute()
            return True
        except Exception as e:
            print(f"Error deleting prediction: {e}")
            return False
    
    @staticmethod
    def update_prediction(prediction_id, update_data):
        """Update a prediction by ID"""
        try:
            result = supabase.table("predictions")\
                .update(update_data)\
                .eq("id", prediction_id)\
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error updating prediction: {e}")
            return None
