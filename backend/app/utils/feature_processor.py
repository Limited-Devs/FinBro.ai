"""
Feature processor for ML model predictions.

Handles:
- Input data transformation
- Feature engineering
- One-hot encoding for categorical variables
"""
import numpy as np
from typing import Dict, Any, List
import json
import os


class FeatureProcessor:
    """
    Processes raw input data into feature vectors for ML models.
    
    This class encapsulates all feature engineering logic,
    making it testable and reusable.
    """
    
    # Expense categories
    EXPENSE_KEYS: List[str] = [
        "Rent", "Loan_Repayment", "Insurance", "Groceries", "Transport",
        "Eating_Out", "Entertainment", "Utilities", "Healthcare", 
        "Education", "Miscellaneous"
    ]
    
    # Essential expense categories
    ESSENTIAL_EXPENSE_KEYS: List[str] = [
        "Rent", "Loan_Repayment", "Groceries", "Transport", "Utilities", "Healthcare"
    ]
    
    # Potential savings categories
    POTENTIAL_SAVINGS_KEYS: List[str] = [
        "Potential_Savings_Groceries", "Potential_Savings_Transport",
        "Potential_Savings_Eating_Out", "Potential_Savings_Entertainment",
        "Potential_Savings_Utilities", "Potential_Savings_Healthcare",
        "Potential_Savings_Education", "Potential_Savings_Miscellaneous"
    ]
    
    
    def __init__(self, feature_info_path: str):
        """
        Initialize the feature processor.
        
        Args:
            feature_info_path: Path to the feature_info.json file
        """
        try:
            with open(feature_info_path, 'r') as f:
                self.feature_info = json.load(f)
            
            self.feature_order = (
                self.feature_info.get('numerical_features', []) + 
                self.feature_info.get('categorical_features', [])
            )
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # Fallback initialization to prevent crash
            print(f"Warning: Failed to load feature info from {feature_info_path}: {e}")
            self.feature_info = {}
            self.feature_order = []
            
        self.total_features = len(self.feature_order)
    
    def process(self, data: Dict[str, Any]) -> np.ndarray:
        """
        Transform raw input data into a feature vector.
        
        Args:
            data: Dictionary containing all input fields
        
        Returns:
            numpy array of shape (1, num_features)
        """
        # Extract base data with type conversion
        base_data = self._extract_base_data(data)
        
        # Extract expenses
        expenses = self._extract_expenses(data)
        
        # Extract potential savings
        potential_savings = self._extract_potential_savings(data)
        
        # Compute derived features
        derived = self._compute_derived_features(base_data, expenses, potential_savings)
        
        # Create one-hot encoded categorical features
        categorical = self._encode_categorical(data, base_data)
        
        # Combine all features
        features = {
            **base_data,
            **expenses,
            **potential_savings,
            **derived,
            **categorical
        }
        
        # Build feature vector in correct order
        return self._build_feature_vector(features)
    
    def _extract_base_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and convert base data fields."""
        return {
            "Income": float(data["Income"]),
            "Age": int(data["Age"]),
            "Dependents": int(data["Dependents"]),
            "Desired_Savings_Percentage": float(data["Desired_Savings_Percentage"]),
            "Disposable_Income": float(data["Disposable_Income"])
        }
    
    def _extract_expenses(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Extract expense fields."""
        return {k: float(data[k]) for k in self.EXPENSE_KEYS}
    
    def _extract_potential_savings(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Extract potential savings fields."""
        return {k: float(data[k]) for k in self.POTENTIAL_SAVINGS_KEYS}
    
    def _compute_derived_features(
        self,
        base_data: Dict[str, Any],
        expenses: Dict[str, float],
        potential_savings: Dict[str, float]
    ) -> Dict[str, float]:
        """Compute derived financial features."""
        
        income = base_data["Income"]
        disposable = base_data["Disposable_Income"]
        
        total_expenses = sum(expenses.values())
        essential_expenses = sum(expenses[k] for k in self.ESSENTIAL_EXPENSE_KEYS)
        actual_savings_potential = sum(potential_savings.values())
        
        # Avoid division by zero
        expense_efficiency = (
            actual_savings_potential / disposable if disposable > 0 else 0
        )
        
        return {
            "Savings_Rate": base_data["Desired_Savings_Percentage"] / 100,
            "Actual_Savings_Potential": actual_savings_potential,
            "Essential_Expenses": essential_expenses,
            "Essential_Expense_Ratio": essential_expenses / income if income > 0 else 0,
            "Non_Essential_Income": income - essential_expenses,
            "Expense_Efficiency": expense_efficiency,
            "Total_Expenses": total_expenses,
            "Debt_to_Income_Ratio": expenses["Loan_Repayment"] / income if income > 0 else 0,
            "Financial_Stress_Score": 1 - (disposable / income) if income > 0 else 1,
        }
    
    def _encode_categorical(
        self,
        data: Dict[str, Any],
        base_data: Dict[str, Any]
    ) -> Dict[str, int]:
        """Create one-hot encoded categorical features."""
        
        occupation = data.get("Occupation", "")
        city_tier = data.get("City_Tier", "")
        age = base_data["Age"]
        income = base_data["Income"]
        
        return {
            # Occupation encoding
            "Occupation_Retired": int(occupation == "Retired"),
            "Occupation_Self_Employed": int(occupation == "Self_Employed"),
            "Occupation_Student": int(occupation == "Student"),
            
            # City tier encoding
            "City_Tier_Tier_2": int(city_tier == "Tier_2"),
            "City_Tier_Tier_3": int(city_tier == "Tier_3"),
            
            # Age group encoding
            "Age_Group_Young_Adult": int(age < 25),
            "Age_Group_Mid_Career": int(25 <= age < 40),
            "Age_Group_Pre_Retirement": int(40 <= age < 60),
            "Age_Group_Senior": int(age >= 60),
            
            # Income bracket encoding
            "Income_Bracket_Low_Income": int(income < 20000),
            "Income_Bracket_Lower_Mid": int(20000 <= income < 40000),
            "Income_Bracket_Middle": int(40000 <= income < 70000),
            "Income_Bracket_Upper_Mid": int(income >= 70000),
            
            # Savings difficulty (default values)
            "Savings_Difficulty_Moderate": 0,
            "Savings_Difficulty_Very_Hard": 0,
            "Savings_Difficulty_nan": 1
        }
    
    def _build_feature_vector(self, features: Dict[str, Any]) -> np.ndarray:
        """Build feature vector in the correct order."""
        vector = []
        for name in self.feature_order:
            if name not in features:
                raise KeyError(f"Missing feature: {name}")
            vector.append(features[name])
        
        return np.array(vector, dtype=np.float32).reshape(1, -1)
