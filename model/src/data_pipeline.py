"""
Data Pipeline Module

Handles data loading, validation, and splitting for the FinBro.ai ML system.
Follows production-grade principles:
- Schema validation
- Data versioning awareness
- Reproducible splitting
"""
import os
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split


# Feature definitions
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

REQUIRED_COLUMNS = [
    'Income', 'Age', 'Dependents', 'Occupation', 'City_Tier',
    *EXPENSE_COLUMNS,
    'Desired_Savings_Percentage', 'Desired_Savings', 'Disposable_Income',
    *POTENTIAL_SAVINGS_COLUMNS
]

# Expected value ranges for validation
SCHEMA_VALIDATION = {
    'Income': {'min': 0, 'max': 1_000_000},
    'Age': {'min': 18, 'max': 100},
    'Dependents': {'min': 0, 'max': 10},
    'Desired_Savings_Percentage': {'min': 0, 'max': 100},
}


class DataValidationError(Exception):
    """Raised when data validation fails."""
    pass


class DataPipeline:
    """
    Production-grade data pipeline for financial prediction.
    
    Responsibilities:
    - Load data from CSV (not hardcoded)
    - Validate schema and value ranges
    - Create reproducible train/val/test splits
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the data pipeline.
        
        Args:
            data_path: Path to the data CSV. Defaults to ../data/data.csv
        """
        if data_path is None:
            self.data_path = Path(__file__).parent.parent.parent / 'data' / 'data.csv'
        else:
            self.data_path = Path(data_path)
        
        self.df: Optional[pd.DataFrame] = None
        self._validation_report: Dict[str, Any] = {}
    
    def load_data(self, validate: bool = True) -> pd.DataFrame:
        """
        Load data from CSV file.
        
        Args:
            validate: Whether to run validation checks
            
        Returns:
            Loaded DataFrame
            
        Raises:
            FileNotFoundError: If data file doesn't exist
            DataValidationError: If validation fails
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_path}")
        
        self.df = pd.read_csv(self.data_path)
        
        if validate:
            self._validate_schema()
            self._validate_ranges()
            self._check_missing_values()
        
        return self.df
    
    def _validate_schema(self) -> None:
        """Validate that all required columns are present."""
        missing_cols = set(REQUIRED_COLUMNS) - set(self.df.columns)
        if missing_cols:
            raise DataValidationError(f"Missing required columns: {missing_cols}")
    
    def _validate_ranges(self) -> None:
        """Validate that values are within expected ranges."""
        warnings = []
        for col, bounds in SCHEMA_VALIDATION.items():
            if col in self.df.columns:
                min_val = self.df[col].min()
                max_val = self.df[col].max()
                if min_val < bounds['min'] or max_val > bounds['max']:
                    warnings.append(
                        f"{col}: values [{min_val:.2f}, {max_val:.2f}] "
                        f"outside expected range [{bounds['min']}, {bounds['max']}]"
                    )
        self._validation_report['range_warnings'] = warnings
    
    def _check_missing_values(self) -> None:
        """Check for missing values in critical columns."""
        missing_counts = self.df[REQUIRED_COLUMNS].isnull().sum()
        missing_cols = missing_counts[missing_counts > 0]
        if not missing_cols.empty:
            self._validation_report['missing_values'] = missing_cols.to_dict()
    
    def get_validation_report(self) -> Dict[str, Any]:
        """Return validation findings."""
        return self._validation_report
    
    def create_splits(
        self,
        test_size: float = 0.15,
        val_size: float = 0.15,
        random_state: int = 42,
        stratify_col: Optional[str] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Create train/validation/test splits.
        
        Args:
            test_size: Fraction for test set
            val_size: Fraction for validation set (from remaining after test)
            random_state: Random seed for reproducibility
            stratify_col: Column to stratify on
            
        Returns:
            Tuple of (train_df, val_df, test_df)
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        stratify = self.df[stratify_col] if stratify_col else None
        
        # First split: separate test set
        train_val_df, test_df = train_test_split(
            self.df,
            test_size=test_size,
            random_state=random_state,
            stratify=stratify
        )
        
        # Second split: separate validation from training
        val_ratio = val_size / (1 - test_size)
        stratify_train = train_val_df[stratify_col] if stratify_col else None
        
        train_df, val_df = train_test_split(
            train_val_df,
            test_size=val_ratio,
            random_state=random_state,
            stratify=stratify_train
        )
        
        return train_df.reset_index(drop=True), val_df.reset_index(drop=True), test_df.reset_index(drop=True)
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary statistics about the data."""
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        return {
            'num_rows': len(self.df),
            'num_columns': len(self.df.columns),
            'columns': list(self.df.columns),
            'dtypes': self.df.dtypes.astype(str).to_dict(),
            'income_range': (self.df['Income'].min(), self.df['Income'].max()),
            'age_range': (self.df['Age'].min(), self.df['Age'].max()),
            'occupations': self.df['Occupation'].unique().tolist(),
            'city_tiers': self.df['City_Tier'].unique().tolist(),
        }


def load_and_split(
    data_path: Optional[str] = None,
    test_size: float = 0.15,
    val_size: float = 0.15,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Convenience function to load data and create splits.
    
    Args:
        data_path: Path to data CSV
        test_size: Fraction for test set
        val_size: Fraction for validation set
        random_state: Random seed
        
    Returns:
        Tuple of (train_df, val_df, test_df)
    """
    pipeline = DataPipeline(data_path)
    pipeline.load_data(validate=True)
    return pipeline.create_splits(test_size, val_size, random_state)


if __name__ == "__main__":
    # Test the pipeline
    pipeline = DataPipeline()
    df = pipeline.load_data()
    print(f"Loaded {len(df)} rows")
    print(f"Summary: {pipeline.get_data_summary()}")
    
    train, val, test = pipeline.create_splits()
    print(f"Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")
