"""
Model Evaluation Module

Comprehensive evaluation of ML models with business-aligned metrics.
"""
from typing import Dict, Any, List
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix,
    mean_absolute_error, mean_squared_error, r2_score
)


class ModelEvaluator:
    """
    Evaluate ML models with comprehensive metrics.
    """
    
    def evaluate_classifier(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: np.ndarray
    ) -> Dict[str, float]:
        """
        Evaluate a binary classifier.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Predicted probabilities
            
        Returns:
            Dictionary of metrics
        """
        # Handle edge case where all predictions are same class
        try:
            auc = roc_auc_score(y_true, y_proba)
        except ValueError:
            auc = 0.5
        
        return {
            'accuracy': float(accuracy_score(y_true, y_pred)),
            'precision': float(precision_score(y_true, y_pred, zero_division=0)),
            'recall': float(recall_score(y_true, y_pred, zero_division=0)),
            'f1_score': float(f1_score(y_true, y_pred, zero_division=0)),
            'roc_auc': float(auc)
        }
    
    def evaluate_regressor(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> Dict[str, float]:
        """
        Evaluate a regressor.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            
        Returns:
            Dictionary of metrics
        """
        return {
            'mae': float(mean_absolute_error(y_true, y_pred)),
            'rmse': float(np.sqrt(mean_squared_error(y_true, y_pred))),
            'r2': float(r2_score(y_true, y_pred))
        }
    
    def evaluate_all(
        self,
        model,
        X: np.ndarray,
        y: Dict[str, np.ndarray]
    ) -> Dict[str, Dict[str, float]]:
        """
        Evaluate all model outputs.
        
        Args:
            model: Trained model with predict method
            X: Features
            y: Dictionary with targets
            
        Returns:
            Evaluation results for all tasks
        """
        # Get predictions
        y_pred_class = model.classifier.predict(X)
        y_proba_class = model.classifier.predict_proba(X)[:, 1]
        y_pred_reg = model.regressor.predict(X)
        y_pred_risk = model.risk_classifier.predict(X)
        y_proba_risk = model.risk_classifier.predict_proba(X)[:, 1]
        
        return {
            'savings_classifier': self.evaluate_classifier(
                y['classification'], y_pred_class, y_proba_class
            ),
            'savings_regressor': self.evaluate_regressor(
                y['regression'], y_pred_reg
            ),
            'risk_classifier': self.evaluate_classifier(
                y['risk'], y_pred_risk, y_proba_risk
            )
        }
    
    def threshold_analysis(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
        thresholds: List[float] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Analyze performance at different probability thresholds.
        
        Args:
            y_true: True labels
            y_proba: Predicted probabilities
            thresholds: List of thresholds to evaluate
            
        Returns:
            Metrics at each threshold
        """
        if thresholds is None:
            thresholds = [0.3, 0.4, 0.5, 0.6, 0.7]
        
        results = {}
        for t in thresholds:
            y_pred = (y_proba >= t).astype(int)
            results[f"threshold_{t}"] = {
                'precision': float(precision_score(y_true, y_pred, zero_division=0)),
                'recall': float(recall_score(y_true, y_pred, zero_division=0)),
                'f1_score': float(f1_score(y_true, y_pred, zero_division=0))
            }
        
        return results


def print_evaluation_report(results: Dict[str, Dict[str, float]]) -> None:
    """Pretty print evaluation results."""
    print("\n" + "="*60)
    print("MODEL EVALUATION REPORT")
    print("="*60)
    
    for model_name, metrics in results.items():
        print(f"\n{model_name.upper().replace('_', ' ')}")
        print("-" * 40)
        for metric, value in metrics.items():
            print(f"  {metric}: {value:.4f}")
    
    print("\n" + "="*60)


def compare_to_baselines(
    model_results: Dict[str, Dict[str, float]],
    baseline_results: Dict[str, Dict[str, float]]
) -> Dict[str, Dict[str, str]]:
    """
    Compare model results to baselines.
    
    Returns improvement percentages.
    """
    comparisons = {}
    
    # Compare classification
    model_acc = model_results['savings_classifier']['accuracy']
    baseline_acc = baseline_results['logistic_regression']['val']['accuracy']
    
    comparisons['classification'] = {
        'model_accuracy': f"{model_acc:.4f}",
        'baseline_accuracy': f"{baseline_acc:.4f}",
        'improvement': f"{(model_acc - baseline_acc) / baseline_acc * 100:.1f}%"
    }
    
    # Compare regression
    model_mae = model_results['savings_regressor']['mae']
    baseline_mae = baseline_results['linear_regression']['val']['mae']
    
    comparisons['regression'] = {
        'model_mae': f"{model_mae:.2f}",
        'baseline_mae': f"{baseline_mae:.2f}",
        'improvement': f"{(baseline_mae - model_mae) / baseline_mae * 100:.1f}%"
    }
    
    return comparisons
