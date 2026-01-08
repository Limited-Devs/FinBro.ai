"""
Feature Engineering Module

Handles feature transformation for the FinBro.ai ML system.
Key principles:
- Reproducible transformations (training == inference)
- Explicit feature definitions
- No data leakage from future data
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
import pickle


# Feature column definitions (shared with data_pipeline)
EXPENSE_COLUMNS = [
    'Rent', 'Loan_Repayment', 'Insurance', 'Groceries', 'Transport',
    'Eating_Out', 'Entertainment', 'Utilities', 'Healthcare', 'Education', 'Miscellaneous'
]

POTENTIAL_SAVINGS_COLUMNS = [
    'Potential_Savings_Groceries', 'Potential_Savings_Transport',
    'Potential_Savings_Eating_Out', 'Potential_Savings_Entertainment',
    'Potential_Savings_Utilities', 'Potential_Savings_Healthcare',
    'Potential_Savings_Education', 'Potential_Savings_Miscellaneous'
]

CATEGORICAL_COLUMNS = ['Occupation', 'City_Tier']

NUMERICAL_COLUMNS = [
    'Income', 'Age', 'Dependents',
    *EXPENSE_COLUMNS,
    'Desired_Savings_Percentage', 'Disposable_Income',
    *POTENTIAL_SAVINGS_COLUMNS
]


class FeatureEngineer:
    """
    Feature engineering for financial prediction.
    
    Transformations:
    - Compute derived features (total_expenses, spend_ratio, etc.)
    - Encode categorical variables
    - Standardize numerical features
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self._fitted = False
        
        # Features used for modeling
        self.feature_columns: List[str] = []
        self.target_columns: Dict[str, str] = {
            'classification': 'goal_achieved',
            'regression': 'actual_savings',
            'risk': 'financial_risk'
        }
    
    def fit(self, df: pd.DataFrame) -> 'FeatureEngineer':
        """
        Fit the feature transformers on training data.
        
        Args:
            df: Training DataFrame
            
        Returns:
            self for method chaining
        """
        # First create derived features
        df_transformed = self._create_derived_features(df.copy())
        
        # Fit label encoders
        for col in CATEGORICAL_COLUMNS:
            if col in df_transformed.columns:
                self.label_encoders[col] = LabelEncoder()
                self.label_encoders[col].fit(df_transformed[col].astype(str))
        
        # Fit scaler on numerical features
        numerical_cols = self._get_numerical_columns(df_transformed)
        self.scaler.fit(df_transformed[numerical_cols])
        
        # Define the final feature columns
        self.feature_columns = numerical_cols + [f"{col}_encoded" for col in CATEGORICAL_COLUMNS]
        
        self._fitted = True
        return self
    
    def transform(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, pd.Series]]:
        """
        Transform features for modeling.
        
        Args:
            df: DataFrame to transform
            
        Returns:
            Tuple of (feature_df, targets_dict)
        """
        if not self._fitted:
            raise ValueError("FeatureEngineer not fitted. Call fit() first.")
        
        df_transformed = self._create_derived_features(df.copy())
        
        # Encode categoricals with handling for unseen labels
        for col, encoder in self.label_encoders.items():
            if col in df_transformed.columns:
                # Convert to string to ensure matching
                values = df_transformed[col].astype(str)
                
                # Check for unseen labels
                known_classes = set(encoder.classes_)
                # Apply encoding - map unknown to first class (safe fallback)
                # In production, might want 'Unknown' class but that requires training support
                safe_values = values.apply(lambda x: x if x in known_classes else encoder.classes_[0])
                
                df_transformed[f"{col}_encoded"] = encoder.transform(safe_values)
        
        # Scale numericals
        numerical_cols = self._get_numerical_columns(df_transformed)
        df_transformed[numerical_cols] = self.scaler.transform(df_transformed[numerical_cols])
        
        # Extract targets
        targets = {}
        for target_name, col in self.target_columns.items():
            if col in df_transformed.columns:
                targets[target_name] = df_transformed[col]
        
        # Return feature columns only
        feature_df = df_transformed[self.feature_columns]
        
        return feature_df, targets
    
    def fit_transform(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, pd.Series]]:
        """Fit and transform in one step."""
        self.fit(df)
        return self.transform(df)
    
    def _create_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create derived features from raw data."""
        # Total expenses
        expense_cols = [c for c in EXPENSE_COLUMNS if c in df.columns]
        df['total_expenses'] = df[expense_cols].sum(axis=1)
        
        # Total potential savings
        savings_cols = [c for c in POTENTIAL_SAVINGS_COLUMNS if c in df.columns]
        df['total_potential_savings'] = df[savings_cols].sum(axis=1)
        
        # Ratios (with safety for division by zero)
        df['spend_ratio'] = np.where(
            df['Income'] > 0,
            df['total_expenses'] / df['Income'],
            0
        )
        
        # Actual savings
        df['actual_savings'] = df['Income'] - df['total_expenses']
        
        # Savings ratio
        df['savings_ratio'] = np.where(
            df['Income'] > 0,
            df['actual_savings'] / df['Income'],
            0
        )
        
        # Desired savings amount (if percentage given)
        if 'Desired_Savings' not in df.columns and 'Desired_Savings_Percentage' in df.columns:
            df['Desired_Savings'] = df['Income'] * df['Desired_Savings_Percentage'] / 100
        
        # Target: Goal achieved (for classification)
        if 'Desired_Savings' in df.columns:
            df['goal_achieved'] = (df['actual_savings'] >= df['Desired_Savings']).astype(int)
        
        # Target: Financial risk (high spending ratio)
        df['financial_risk'] = (df['spend_ratio'] > 0.9).astype(int)
        
        return df
    
    def _get_numerical_columns(self, df: pd.DataFrame) -> List[str]:
        """Get numerical columns that exist in the dataframe."""
        base_numerical = [
            'Income', 'Age', 'Dependents',
            'total_expenses', 'total_potential_savings',
            'spend_ratio', 'savings_ratio', 'actual_savings',
            'Desired_Savings_Percentage', 'Disposable_Income'
        ]
        # Add expense columns that exist
        for col in EXPENSE_COLUMNS:
            if col in df.columns:
                base_numerical.append(col)
        
        # Add potential savings columns that exist
        for col in POTENTIAL_SAVINGS_COLUMNS:
            if col in df.columns:
                base_numerical.append(col)
        
        return [c for c in base_numerical if c in df.columns]
    
    def save(self, path: str) -> None:
        """Save feature engineering artifacts."""
        artifacts = {
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_columns': self.feature_columns,
            'target_columns': self.target_columns
        }
        with open(path, 'wb') as f:
            pickle.dump(artifacts, f)
    
    @classmethod
    def load(cls, path: str) -> 'FeatureEngineer':
        """Load feature engineering artifacts."""
        with open(path, 'rb') as f:
            artifacts = pickle.load(f)
        
        engineer = cls()
        engineer.scaler = artifacts['scaler']
        engineer.label_encoders = artifacts['label_encoders']
        engineer.feature_columns = artifacts['feature_columns']
        engineer.target_columns = artifacts['target_columns']
        engineer._fitted = True
        
        return engineer
    
    def get_feature_info(self) -> Dict[str, Any]:
        """Get feature metadata for inference."""
        return {
            'feature_columns': self.feature_columns,
            'categorical_columns': list(self.label_encoders.keys()),
            'target_columns': self.target_columns,
            'scaler_mean': self.scaler.mean_.tolist() if hasattr(self.scaler, 'mean_') else None,
            'scaler_scale': self.scaler.scale_.tolist() if hasattr(self.scaler, 'scale_') else None
        }


if __name__ == "__main__":
    # Test the feature engineering
    from data_pipeline import DataPipeline
    
    pipeline = DataPipeline()
    df = pipeline.load_data()
    train_df, val_df, test_df = pipeline.create_splits()
    
    engineer = FeatureEngineer()
    X_train, y_train = engineer.fit_transform(train_df)
    X_val, y_val = engineer.transform(val_df)
    
    print(f"Training features shape: {X_train.shape}")
    print(f"Feature columns: {engineer.feature_columns}")
    print(f"Targets: {list(y_train.keys())}")
