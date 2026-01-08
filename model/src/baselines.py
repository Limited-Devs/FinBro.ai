"""
Baseline Models

Simple models to establish baseline performance.
Every ML project needs baselines to prove complex models are worthwhile.
"""
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, r2_score


class RuleBasedBaseline:
    """
    Rule-based baseline for savings goal prediction.
    
    Simple rule: User achieves savings goal if:
    - Disposable income >= Desired savings
    """
    
    def __init__(self):
        self.threshold = 1.0  # Disposable income / Desired savings ratio
    
    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """
        Predict if user can achieve savings goal.
        
        Args:
            df: DataFrame with Disposable_Income and Desired_Savings columns
            
        Returns:
            Binary predictions (1 = can achieve, 0 = cannot)
        """
        ratio = df['Disposable_Income'] / df['Desired_Savings'].replace(0, 1)
        return (ratio >= self.threshold).astype(int).values
    
    def evaluate(self, df: pd.DataFrame, y_true: np.ndarray) -> Dict[str, float]:
        """Evaluate baseline performance."""
        y_pred = self.predict(df)
        return {
            'accuracy': accuracy_score(y_true, y_pred),
            'f1_score': f1_score(y_true, y_pred, zero_division=0)
        }


class LogisticBaseline:
    """
    Logistic regression baseline for classification.
    """
    
    def __init__(self):
        self.model = LogisticRegression(max_iter=1000, random_state=42)
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'LogisticBaseline':
        """Fit the model."""
        self.model.fit(X, y)
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels."""
        return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities."""
        return self.model.predict_proba(X)[:, 1]
    
    def evaluate(self, X: np.ndarray, y_true: np.ndarray) -> Dict[str, float]:
        """Evaluate model performance."""
        y_pred = self.predict(X)
        return {
            'accuracy': accuracy_score(y_true, y_pred),
            'f1_score': f1_score(y_true, y_pred, zero_division=0)
        }


class LinearBaseline:
    """
    Linear regression baseline for amount prediction.
    """
    
    def __init__(self):
        self.model = LinearRegression()
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'LinearBaseline':
        """Fit the model."""
        self.model.fit(X, y)
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict savings amount."""
        return self.model.predict(X)
    
    def evaluate(self, X: np.ndarray, y_true: np.ndarray) -> Dict[str, float]:
        """Evaluate model performance."""
        y_pred = self.predict(X)
        return {
            'mae': mean_absolute_error(y_true, y_pred),
            'r2': r2_score(y_true, y_pred)
        }


def run_baselines(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    X_train: np.ndarray,
    X_val: np.ndarray,
    y_train_class: np.ndarray,
    y_val_class: np.ndarray,
    y_train_reg: np.ndarray,
    y_val_reg: np.ndarray
) -> Dict[str, Dict[str, float]]:
    """
    Run all baseline models and return their metrics.
    
    Args:
        train_df: Training DataFrame (for rule-based)
        val_df: Validation DataFrame (for rule-based)
        X_train, X_val: Processed features
        y_train_class, y_val_class: Classification targets
        y_train_reg, y_val_reg: Regression targets
        
    Returns:
        Dictionary of baseline names to their metrics
    """
    results = {}
    
    # Rule-based baseline
    rule_baseline = RuleBasedBaseline()
    results['rule_based'] = {
        'train': rule_baseline.evaluate(train_df, y_train_class),
        'val': rule_baseline.evaluate(val_df, y_val_class)
    }
    
    # Logistic regression baseline
    logistic_baseline = LogisticBaseline()
    logistic_baseline.fit(X_train, y_train_class)
    results['logistic_regression'] = {
        'train': logistic_baseline.evaluate(X_train, y_train_class),
        'val': logistic_baseline.evaluate(X_val, y_val_class)
    }
    
    # Linear regression baseline
    linear_baseline = LinearBaseline()
    linear_baseline.fit(X_train, y_train_reg)
    results['linear_regression'] = {
        'train': linear_baseline.evaluate(X_train, y_train_reg),
        'val': linear_baseline.evaluate(X_val, y_val_reg)
    }
    
    return results


def print_baseline_results(results: Dict[str, Dict[str, float]]) -> None:
    """Pretty print baseline results."""
    print("\n" + "="*60)
    print("BASELINE RESULTS")
    print("="*60)
    
    for name, metrics in results.items():
        print(f"\n{name.upper().replace('_', ' ')}")
        print("-" * 40)
        for split, values in metrics.items():
            print(f"  {split}:")
            for metric, value in values.items():
                print(f"    {metric}: {value:.4f}")
    
    print("\n" + "="*60)
