"""
Verification script for ML integration.
Tests the full chain: PredictionService -> FeatureProcessor -> MLModelService
"""
import os
import sys
import json
import numpy as np
from pathlib import Path

# Add backend and model paths
sys.path.insert(0, os.path.abspath('backend'))
sys.path.insert(0, os.path.abspath('model/src'))

# Mock config
class MockConfig:
    MODEL_DIR = os.path.abspath('model')
    FEATURE_INFO_FILE = 'backend/user_data.json' # Dummy path, not used with artifact loading
    ENABLE_JSON_FALLBACK = False

# MOCK MISSING DEPENDENCIES to avoid ImportError
from unittest.mock import MagicMock
sys.modules['flask'] = MagicMock()
sys.modules['flask_cors'] = MagicMock()
sys.modules['flask_sqlalchemy'] = MagicMock()
sys.modules['sqlalchemy'] = MagicMock()

import backend.app.config
backend.app.config.get_config = lambda: MockConfig()

# Import services
from backend.app.services.ml_model_service import MLModelService
from backend.app.utils.feature_processor import FeatureProcessor

def verify_integration():
    print("="*60)
    print("VERIFYING ML INTEGRATION")
    print("="*60)
    
    # 1. Initialize Services
    print("\n1. Initializing Services...")
    try:
        model_service = MLModelService(model_dir=os.path.abspath('model'))
        health = model_service.check_health()
        print(f"   MLModelService Health: {json.dumps(health, indent=2)}")
        
        if health['status'] != 'healthy':
            print("   ❌ Model service unhealthy!")
            return False
            
        processor = FeatureProcessor()
        
        # DEBUG: Inspect encoders
        if processor.engineer:
            for col, le in processor.engineer.label_encoders.items():
                print(f"   Encoded column '{col}' classes: {le.classes_}")
                
        print("   ✓ FeatureProcessor initialized")
        
    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 2. Test Prediction Data
    print("\n2. Testing Prediction...")
    test_input = {
        "Income": 75000,
        "Age": 30,
        "Dependents": 1,
        "Occupation": "Professional",
        "City_Tier": "Tier_1",
        "Rent": 20000,
        "Loan_Repayment": 5000,
        "Insurance": 2000,
        "Groceries": 8000,
        "Transport": 3000,
        "Eating_Out": 4000,
        "Entertainment": 2000,
        "Utilities": 3000,
        "Healthcare": 2000,
        "Education": 0,
        "Miscellaneous": 2000,
        "Desired_Savings_Percentage": 20,
        "Disposable_Income": 10000,
        "Potential_Savings_Groceries": 500,
        "Potential_Savings_Transport": 500,
        "Potential_Savings_Eating_Out": 1000,
        "Potential_Savings_Entertainment": 500,
        "Potential_Savings_Utilities": 200,
        "Potential_Savings_Healthcare": 0,
        "Potential_Savings_Education": 0,
        "Potential_Savings_Miscellaneous": 500
    }
    
    try:
        # Process features
        features = processor.process(test_input)
        print(f"   Generated Features Shape: {features.shape}")
        
        # Make prediction
        predictions = model_service.predict(features)
        print(f"   Prediction Result: {json.dumps(predictions, indent=2)}")
        
        # Verify structure
        assert 'savings_model' in predictions
        assert 'amount_model' in predictions
        assert 'multi_task_model' in predictions
        
        print("\n   ✓ Prediction structure verified")
        print("   ✓ Integration successful!")
        return True
        
    except Exception as e:
        print(f"\n   ❌ Prediction failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_integration()
    sys.exit(0 if success else 1)
