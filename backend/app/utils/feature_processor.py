"""
Feature processor for ML model predictions.

Handles:
- Input data transformation using the same logic as training
- Feature engineering consistency
- One-hot encoding and scaling
"""
import os
import sys
import numpy as np
import pandas as pd
from typing import Dict, Any, List
import pickle
import warnings

# Add model source to path to import FeatureEngineer definition
# In production this would be installed as a package
FEATURE_ENGINEER_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    'model', 'src'
)
sys.path.append(FEATURE_ENGINEER_PATH)

try:
    from feature_engineering import FeatureEngineer
    HAS_ENGINEER = True
except ImportError:
    HAS_ENGINEER = False
    warnings.warn("Could not import FeatureEngineer from model package")


class FeatureProcessor:
    """
    Processes raw input data into feature vectors for ML models.
    
    Uses the trained FeatureEngineer artifact to ensure
    inference logic matches training logic exactly.
    
    Uses singleton pattern to avoid repeated disk I/O.
    """
    
    _instance: 'FeatureProcessor' = None
    _initialized: bool = False
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern to avoid repeated unpickling."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, feature_info_path: str = None):
        """
        Initialize the feature processor.
        
        Args:
            feature_info_path: Path to feature info (loading from artifact instead)
        """
        if self._initialized:
            return
            
        # Path to trained feature engineer artifact
        self.artifact_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'model', 'trained_model', 'feature_engineer.pkl'
        )
        
        self.engineer = None
        self._load_engineer()
        
        FeatureProcessor._initialized = True
            
    def _load_engineer(self):
        """Load the trained feature engineer."""
        if not os.path.exists(self.artifact_path):
            print(f"Warning: Feature engineer artifact not found at {self.artifact_path}")
            return
            
        try:
            # We need the class definition available to unpickle
            if HAS_ENGINEER:
                with open(self.artifact_path, 'rb') as f:
                    # Helper to load the internal state since FeatureEngineer.load expects a path
                    # but we might need to handle class path issues
                    artifacts = pickle.load(f)
                    
                self.engineer = FeatureEngineer()
                self.engineer.scaler = artifacts['scaler']
                self.engineer.label_encoders = artifacts['label_encoders']
                self.engineer.feature_columns = artifacts['feature_columns']
                self.engineer.target_columns = artifacts['target_columns']
                self.engineer._fitted = True
                
                print("Loaded FeatureEngineer successfully")
        except Exception as e:
            print(f"Failed to load FeatureEngineer: {e}")

    def process(self, data: Dict[str, Any]) -> np.ndarray:
        """
        Transform raw input data into a feature vector.
        
        Args:
            data: Dictionary containing all input fields
        
        Returns:
            numpy array of shape (1, num_features)
        """
        if self.engineer is None:
            raise RuntimeError("Feature processor not initialized. Please check model artifacts.")
            
        # Convert single dict to DataFrame
        # We need to make sure types match what pandas expects
        # The input data comes from API request (Pydantic model dump)
        
        # Helper to ensure float/int conversion
        cleaned_data = {}
        for k, v in data.items():
            if isinstance(v, (int, float, str)):
                cleaned_data[k] = v
        
        df = pd.DataFrame([cleaned_data])
        
        # Transform using the engineer
        # Note: transform returns (features_df, targets_dict)
        features_df, _ = self.engineer.transform(df)
        
        # Return as numpy array [1, n_features]
        return features_df.values.astype(np.float32)
