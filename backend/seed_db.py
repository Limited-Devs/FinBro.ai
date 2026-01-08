import os
import sys
import random
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Setup path to import app modules
# Script is in backend/ directory. We need to add backend/ to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Load env variables from backend/.env
load_dotenv(os.path.join(current_dir, '.env'))

from app.repositories.prediction_repository import PredictionRepository

def seed():
    print("🌱 Seeding database...")
    
    repo = PredictionRepository()
    if not repo.supabase:
        print("❌ Supabase not configured! Check .env file.")
        return

    user_id = 'demo-user-123'
    
    # Generate 6 months of data
    today = datetime.now()
    
    print(f"Creating records for user: {user_id}")
    
    for i in range(5, -1, -1):
        date = today - timedelta(days=30 * i)
        date_str = date.isoformat()
        
        # Varying income/expenses slightly
        base_income = 85000
        income = base_income + random.randint(-2000, 2000)
        
        # Consistent expenses
        rent = 25000
        loan = 15000
        insurance = 5000
        utilities = 3000
        healthcare = 2000
        transport = 3000
        education = 0
        misc = 1000
        entertainment = 2000
        
        # Variable expenses
        groceries = 8000 + random.randint(-500, 500)
        eating_out = 4000 + random.randint(-1000, 1000)
        
        # Input Data matching PredictionInput type (PascalCase)
        input_data = {
            "Income": income,
            "Age": 32,
            "Dependents": 1,
            "Occupation": "Self_Employed",
            "City_Tier": "Tier_1",
            "Rent": rent,
            "Loan_Repayment": loan,
            "Insurance": insurance,
            "Groceries": groceries,
            "Transport": transport,
            "Eating_Out": eating_out,
            "Entertainment": entertainment,
            "Utilities": utilities,
            "Healthcare": healthcare,
            "Education": education,
            "Miscellaneous": misc,
            "Desired_Savings_Percentage": 20,
            
            # Potential savings (mocked)
            "Potential_Savings_Groceries": 500,
            "Potential_Savings_Transport": 200,
            "Potential_Savings_Eating_Out": 1200,
            "Potential_Savings_Entertainment": 500,
            "Potential_Savings_Utilities": 300,
            "Potential_Savings_Healthcare": 0,
            "Potential_Savings_Education": 0,
            "Potential_Savings_Miscellaneous": 200
        }
        
        # Calculate derived fields
        total_expenses = sum([rent, loan, insurance, utilities, healthcare, transport, education, misc, entertainment, groceries, eating_out])
        disposable_income = income - total_expenses
        input_data["Disposable_Income"] = disposable_income
        
        # Add extra derived fields required by backend schemas if any? 
        # FeatureProcessor calculates them, but for storage we just need inputs.
        # But wait, UserData type has keys like 'Savings_Rate', 'Actual_Savings_Potential' etc.
        # These are usually calculated by FeatureProcessor on the fly?
        # Backend 'get_all' returns input_data as stored.
        # If Frontend UserData type requires them, they should be in the API response.
        # Check FeatureProcessor._compute_derived_features.
        # It adds them to the feature vector.
        # Does 'input_data' stored in DB have them? No, only raw inputs.
        # Does the API compute them before returning?
        # NO. 'get_all' -> '_format_supabase_record'. It just returns input_data from DB.
        
        # ISSUE: Frontend types 'PredictionInput' includes derived fields (e.g. Savings_Rate).
        # If DB doesn't store them, and API doesn't compute them, Frontend receiving 'input' will miss them.
        # Should we add them to input_data here? YES.
        
        # Calculating derived fields to match PredictionInput
        input_data["Savings_Rate"] = 20 / 100
        input_data["Actual_Savings_Potential"] = 2900 # Sum of potential savings
        input_data["Essential_Expenses"] = rent + loan + groceries + transport + utilities + healthcare
        input_data["Essential_Expense_Ratio"] = input_data["Essential_Expenses"] / income
        input_data["Non_Essential_Income"] = income - input_data["Essential_Expenses"]
        input_data["Expense_Efficiency"] = 2900 / disposable_income if disposable_income > 0 else 0
        input_data["Total_Expenses"] = total_expenses
        input_data["Debt_to_Income_Ratio"] = loan / income
        input_data["Financial_Stress_Score"] = 1 - (disposable_income / income)
        
        # One-hot encoded fields (Frontend type has them...)
        # We should set them or leave them 0/undefined?
        # Frontend might expect them. I'll add them as 0 or 1.
        input_data["Occupation_Self_Employed"] = 1
        input_data["Occupation_Retired"] = 0
        input_data["Occupation_Student"] = 0
        input_data["City_Tier_Tier_2"] = 0
        input_data["City_Tier_Tier_3"] = 0
        input_data["Age_Group_Mid_Career"] = 1
        input_data["Age_Group_Pre_Retirement"] = 0
        input_data["Age_Group_Senior"] = 0
        input_data["Age_Group_Young_Adult"] = 0
        input_data["Income_Bracket_Upper_Mid"] = 1
        input_data["Income_Bracket_Middle"] = 0
        input_data["Income_Bracket_Lower_Mid"] = 0
        input_data["Income_Bracket_Low_Income"] = 0
        input_data["Savings_Difficulty_Moderate"] = 0
        input_data["Savings_Difficulty_Very_Hard"] = 0
        input_data["Savings_Difficulty_nan"] = 0

        output_data = {
            "savings_model": {
                "can_achieve_savings": True,
                "confidence": 0.85
            },
            "amount_model": {
                "recommended_savings": disposable_income * 0.8
            },
            "multi_task_model": {
                "can_achieve_savings": True,
                "savings_confidence": 0.88,
                "recommended_savings_amount": disposable_income * 0.85,
                "financial_risk": False,
                "risk_score": 0.12
            }
        }
        
        try:
            # Use _create_supabase_record to specify timestamp
            # Note: We must bypass the 'create' method to inject timestamp for backdate
            repo._create_supabase_record(
                input_data=input_data,
                output_data=output_data,
                timestamp=date_str,
                user_id=user_id
            )
            print(f"✅ Created record for {date_str[:10]}")
        except Exception as e:
            print(f"❌ Failed to create record: {e}")

    print("\n✨ Seeding complete!")

if __name__ == "__main__":
    seed()
