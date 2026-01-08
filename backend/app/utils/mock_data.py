"""
Mock data utilities for Demo Mode.
Generates realistic seed data for demo users.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random

def generate_mock_predictions(count: int = 10) -> List[Dict[str, Any]]:
    """Generate a list of mock prediction records."""
    predictions = []
    base_date = datetime.now()
    
    # Base financial profile
    base_profile = {
        "Income": 85000,
        "Age": 28,
        "Dependents": 0,
        "Occupation": "Software Engineer",
        "City_Tier": "Tier_1",
        "Rent": 25000,
        "Loan_Repayment": 5000,
        "Insurance": 3000,
        "Groceries": 8000,
        "Transport": 3000,
        "Eating_Out": 6000,
        "Entertainment": 4000,
        "Utilities": 2500,
        "Healthcare": 2000,
        "Education": 0,
        "Miscellaneous": 3000,
        "Desired_Savings_Percentage": 20,
    }

    for i in range(count):
        # Add some variance
        variance = random.uniform(0.95, 1.05)
        
        input_data = base_profile.copy()
        for key in ["Income", "Rent", "Groceries", "Eating_Out", "Entertainment"]:
            input_data[key] = int(input_data[key] * variance) if isinstance(input_data[key], (int, float)) else input_data[key]
            
        # Calculate derived fields
        total_expenses = sum([val for key, val in input_data.items() if key not in ["Income", "Age", "Dependents", "Occupation", "City_Tier", "Desired_Savings_Percentage"] and isinstance(val, (int, float))])
        input_data["Disposable_Income"] = input_data["Income"] - total_expenses
        
        # Mock Output
        output_data = {
            "savings_model": {
                "can_achieve_savings": input_data["Disposable_Income"] > (input_data["Income"] * 0.2),
                "confidence": random.uniform(0.85, 0.98)
            },
            "amount_model": {
                "recommended_savings": int(input_data["Income"] * 0.25)
            },
            "multi_task_model": {
                "financial_risk": False,
                "risk_score": random.uniform(0.1, 0.3),
                "recommended_savings_amount": int(input_data["Income"] * 0.22)
            }
        }

        # Date decreasing by 1 month approx
        timestamp = (base_date - timedelta(days=i*30)).isoformat()
        
        predictions.append({
            "id": f"demo-{i}",
            "timestamp": timestamp,
            "input_data": input_data,
            "output_data": output_data
        })
        
    return predictions

def generate_mock_trends(months: int = 6) -> List[Dict[str, Any]]:
    """Generate aggregated monthly trend data."""
    predictions = generate_mock_predictions(months)
    trends = []
    
    for pred in reversed(predictions): # Oldest first
        dt = datetime.fromisoformat(pred["timestamp"])
        trends.append({
            "month": dt.strftime("%b"),
            "month_key": dt.strftime("%Y-%m"),
            "actual_savings": pred["input_data"]["Disposable_Income"],
            "target_savings": pred["output_data"]["amount_model"]["recommended_savings"]
        })
        
    return trends
