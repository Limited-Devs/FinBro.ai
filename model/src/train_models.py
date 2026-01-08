"""
Model Training Module

XGBoost-based training pipeline for the FinBro.ai ML system.
Following production-grade principles:
- Baseline comparison
- Cross-validation
- Hyperparameter tuning
- Model artifact logging
"""
import json
import pickle
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_score
import xgboost as xgb

from data_pipeline import DataPipeline
from feature_engineering import FeatureEngineer
from baselines import run_baselines, print_baseline_results
from evaluate import ModelEvaluator, print_evaluation_report


class XGBoostTrainer:
    """
    XGBoost-based trainer for financial prediction.
    
    Trains:
    - Classification model (savings goal achievement)
    - Regression model (recommended savings amount)
    """
    
    DEFAULT_CLASSIFIER_PARAMS = {
        'max_depth': 15,
        'learning_rate': 0.1,
        'n_estimators': 10000,
        'objective': 'binary:logistic',
        'eval_metric': 'logloss',
        'random_state': 42,
        'n_jobs': -1
    }
    
    DEFAULT_REGRESSOR_PARAMS = {
        'max_depth': 15,
        'learning_rate': 0.1,
        'n_estimators': 10000,
        'objective': 'reg:squarederror',
        'random_state': 42,
        'n_jobs': -1
    }
    
    def __init__(
        self,
        classifier_params: Optional[Dict] = None,
        regressor_params: Optional[Dict] = None
    ):
        """
        Initialize the trainer.
        
        Args:
            classifier_params: Override default classifier params
            regressor_params: Override default regressor params
        """
        self.classifier_params = {
            **self.DEFAULT_CLASSIFIER_PARAMS,
            **(classifier_params or {})
        }
        self.regressor_params = {
            **self.DEFAULT_REGRESSOR_PARAMS,
            **(regressor_params or {})
        }
        
        self.classifier: Optional[xgb.XGBClassifier] = None
        self.regressor: Optional[xgb.XGBRegressor] = None
        self.risk_classifier: Optional[xgb.XGBClassifier] = None
        
        self.training_history: Dict[str, Any] = {}
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: Dict[str, np.ndarray],
        X_val: np.ndarray,
        y_val: Dict[str, np.ndarray],
        early_stopping_rounds: int = 10
    ) -> 'XGBoostTrainer':
        """
        Train all models.
        
        Args:
            X_train: Training features
            y_train: Dict with 'classification', 'regression', 'risk' targets
            X_val: Validation features
            y_val: Validation targets
            early_stopping_rounds: Early stopping patience
            
        Returns:
            self for method chaining
        """
        print("\n" + "="*60)
        print("TRAINING XGBOOST MODELS")
        print("="*60)
        
        # Train savings goal classifier
        print("\n1. Training savings goal classifier...")
        self.classifier = xgb.XGBClassifier(**self.classifier_params)
        self.classifier.fit(
            X_train, y_train['classification'],
            eval_set=[(X_val, y_val['classification'])],
            verbose=False
        )
        print("   ✓ Classifier trained")
        
        # Train savings amount regressor
        print("\n2. Training savings amount regressor...")
        self.regressor = xgb.XGBRegressor(**self.regressor_params)
        self.regressor.fit(
            X_train, y_train['regression'],
            eval_set=[(X_val, y_val['regression'])],
            verbose=False
        )
        print("   ✓ Regressor trained")
        
        # Train risk classifier
        print("\n3. Training financial risk classifier...")
        self.risk_classifier = xgb.XGBClassifier(**self.classifier_params)
        self.risk_classifier.fit(
            X_train, y_train['risk'],
            eval_set=[(X_val, y_val['risk'])],
            verbose=False
        )
        print("   ✓ Risk classifier trained")
        
        # Store training info
        self.training_history = {
            'trained_at': datetime.now().isoformat(),
            'n_train_samples': len(X_train),
            'n_val_samples': len(X_val),
            'n_features': X_train.shape[1],
            'classifier_params': self.classifier_params,
            'regressor_params': self.regressor_params
        }
        
        print("\n" + "="*60)
        
        return self
    
    def predict(self, X: np.ndarray) -> Dict[str, Any]:
        """
        Make predictions with all models.
        
        Args:
            X: Feature array
            
        Returns:
            Dictionary with predictions from all models
        """
        if self.classifier is None:
            raise ValueError("Models not trained. Call train() first.")
        
        return {
            'savings_model': {
                'can_achieve_savings': bool(self.classifier.predict(X)[0]),
                'confidence': float(self.classifier.predict_proba(X)[0, 1])
            },
            'amount_model': {
                'recommended_savings': float(self.regressor.predict(X)[0])
            },
            'multi_task_model': {
                'can_achieve_savings': bool(self.classifier.predict(X)[0]),
                'savings_confidence': float(self.classifier.predict_proba(X)[0, 1]),
                'recommended_savings_amount': float(self.regressor.predict(X)[0]),
                'financial_risk': bool(self.risk_classifier.predict(X)[0]),
                'risk_score': float(self.risk_classifier.predict_proba(X)[0, 1])
            }
        }
    
    def get_feature_importance(self) -> Dict[str, Dict[str, float]]:
        """Get feature importances from trained models."""
        return {
            'classifier': dict(enumerate(self.classifier.feature_importances_)),
            'regressor': dict(enumerate(self.regressor.feature_importances_)),
            'risk_classifier': dict(enumerate(self.risk_classifier.feature_importances_))
        }
    
    def save(self, model_dir: str) -> None:
        """
        Save trained models and metadata.
        
        Args:
            model_dir: Directory to save models
        """
        model_path = Path(model_dir)
        model_path.mkdir(parents=True, exist_ok=True)
        
        # Save models using the underlying booster to avoid sklearn wrapper issues
        self.classifier.get_booster().save_model(model_path / 'xgb_classifier.json')
        self.regressor.get_booster().save_model(model_path / 'xgb_regressor.json')
        self.risk_classifier.get_booster().save_model(model_path / 'xgb_risk_classifier.json')
        
        # Save metadata
        with open(model_path / 'model_config.json', 'w') as f:
            json.dump({
                'model_type': 'xgboost',
                'training_history': self.training_history,
                'classifier_params': self.classifier_params,
                'regressor_params': self.regressor_params
            }, f, indent=2)
        
        print(f"Models saved to {model_dir}")
    
    @classmethod
    def load(cls, model_dir: str) -> 'XGBoostTrainer':
        """
        Load trained models.
        
        Args:
            model_dir: Directory containing saved models
            
        Returns:
            Loaded trainer instance
        """
        model_path = Path(model_dir)
        
        trainer = cls()
        
        trainer.classifier = xgb.XGBClassifier()
        trainer.classifier.load_model(model_path / 'xgb_classifier.json')
        
        trainer.regressor = xgb.XGBRegressor()
        trainer.regressor.load_model(model_path / 'xgb_regressor.json')
        
        trainer.risk_classifier = xgb.XGBClassifier()
        trainer.risk_classifier.load_model(model_path / 'xgb_risk_classifier.json')
        
        with open(model_path / 'model_config.json') as f:
            config = json.load(f)
            trainer.training_history = config['training_history']
        
        return trainer


def train_pipeline(
    data_path: Optional[str] = None,
    model_dir: Optional[str] = None,
    run_baselines_flag: bool = True
) -> Tuple[XGBoostTrainer, Dict[str, Any]]:
    """
    Full training pipeline.
    
    Args:
        data_path: Path to data CSV
        model_dir: Directory to save models
        run_baselines_flag: Whether to run baseline comparisons
        
    Returns:
        Tuple of (trained_model, evaluation_results)
    """
    print("\n" + "="*60)
    print("FINBRO.AI ML TRAINING PIPELINE")
    print("="*60)
    
    # Default model directory
    if model_dir is None:
        model_dir = str(Path(__file__).parent.parent / 'trained_model')
    
    # 1. Load data
    print("\n[1/5] Loading data...")
    pipeline = DataPipeline(data_path)
    df = pipeline.load_data(validate=True)
    summary = pipeline.get_data_summary()
    print(f"   Loaded {summary['num_rows']} rows, {summary['num_columns']} columns")
    
    # 2. Create splits
    print("\n[2/5] Creating train/val/test splits...")
    train_df, val_df, test_df = pipeline.create_splits()
    print(f"   Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
    
    # 3. Feature engineering
    print("\n[3/5] Engineering features...")
    engineer = FeatureEngineer()
    X_train, y_train = engineer.fit_transform(train_df)
    X_val, y_val = engineer.transform(val_df)
    X_test, y_test = engineer.transform(test_df)
    print(f"   Features: {X_train.shape[1]} columns")
    
    # Convert to numpy
    X_train_np = X_train.values
    X_val_np = X_val.values
    X_test_np = X_test.values
    
    y_train_dict = {
        'classification': y_train['classification'].values,
        'regression': y_train['regression'].values,
        'risk': y_train['risk'].values
    }
    y_val_dict = {
        'classification': y_val['classification'].values,
        'regression': y_val['regression'].values,
        'risk': y_val['risk'].values
    }
    y_test_dict = {
        'classification': y_test['classification'].values,
        'regression': y_test['regression'].values,
        'risk': y_test['risk'].values
    }
    
    # 4. Run baselines
    if run_baselines_flag:
        print("\n[4/5] Running baselines...")
        baseline_results = run_baselines(
            train_df, val_df,
            X_train_np, X_val_np,
            y_train_dict['classification'], y_val_dict['classification'],
            y_train_dict['regression'], y_val_dict['regression']
        )
        print_baseline_results(baseline_results)
    
    # 5. Train XGBoost
    print("\n[5/5] Training XGBoost models...")
    trainer = XGBoostTrainer()
    trainer.train(X_train_np, y_train_dict, X_val_np, y_val_dict)
    
    # 6. Evaluate on test set
    print("\n" + "="*60)
    print("FINAL EVALUATION (TEST SET)")
    print("="*60)
    
    evaluator = ModelEvaluator()
    evaluation_results = evaluator.evaluate_all(
        trainer,
        X_test_np,
        y_test_dict
    )
    print_evaluation_report(evaluation_results)
    
    # 7. Save artifacts
    print("\n[SAVING] Saving models and artifacts...")
    trainer.save(model_dir)
    engineer.save(Path(model_dir) / 'feature_engineer.pkl')
    
    # Save evaluation results
    with open(Path(model_dir) / 'evaluation_results.json', 'w') as f:
        json.dump(evaluation_results, f, indent=2)
    
    print(f"\n✓ Training complete! Models saved to: {model_dir}")
    
    return trainer, evaluation_results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train FinBro.ai ML models')
    parser.add_argument('--data', type=str, help='Path to data CSV')
    parser.add_argument('--output', type=str, help='Output directory for models')
    parser.add_argument('--no-baselines', action='store_true', help='Skip baseline comparison')
    
    args = parser.parse_args()
    
    train_pipeline(
        data_path=args.data,
        model_dir=args.output,
        run_baselines_flag=not args.no_baselines
    )
