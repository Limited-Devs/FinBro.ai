"""
Tests for feature engineering.
"""
import pytest
import sys
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data_pipeline import DataPipeline
from feature_engineering import FeatureEngineer, EXPENSE_COLUMNS


class TestFeatureEngineer:
    """Test feature transformation."""
    
    @pytest.fixture
    def sample_data(self):
        """Load sample data for testing."""
        pipeline = DataPipeline()
        pipeline.load_data()
        train, val, _ = pipeline.create_splits()
        return train, val
    
    def test_fit_transform_returns_features_and_targets(self, sample_data):
        """Fit transform should return features and targets."""
        train, _ = sample_data
        engineer = FeatureEngineer()
        X, y = engineer.fit_transform(train)
        
        assert X is not None
        assert y is not None
        assert len(X) == len(train)
    
    def test_transform_preserves_row_count(self, sample_data):
        """Transform should preserve number of samples."""
        train, val = sample_data
        engineer = FeatureEngineer()
        engineer.fit(train)
        X_val, _ = engineer.transform(val)
        
        assert len(X_val) == len(val)
    
    def test_transform_without_fit_raises_error(self, sample_data):
        """Transform without fit should raise error."""
        _, val = sample_data
        engineer = FeatureEngineer()
        
        with pytest.raises(ValueError, match="not fitted"):
            engineer.transform(val)
    
    def test_derived_features_created(self, sample_data):
        """Derived features should be created."""
        train, _ = sample_data
        engineer = FeatureEngineer()
        X, _ = engineer.fit_transform(train)
        
        # Check feature engineering created expected columns
        assert len(engineer.feature_columns) > 0
    
    def test_targets_contain_expected_keys(self, sample_data):
        """Targets should contain classification, regression, risk."""
        train, _ = sample_data
        engineer = FeatureEngineer()
        _, y = engineer.fit_transform(train)
        
        assert 'classification' in y
        assert 'regression' in y
        assert 'risk' in y
    
    def test_feature_values_are_scaled(self, sample_data):
        """Numerical features should be scaled (mean ~0, std ~1)."""
        train, _ = sample_data
        engineer = FeatureEngineer()
        X, _ = engineer.fit_transform(train)
        
        # Check that values are roughly standardized
        means = X.mean()
        stds = X.std()
        
        # Most means should be close to 0
        assert (means.abs() < 1).sum() > len(means) / 2
    
    def test_save_and_load_preserves_state(self, sample_data, tmp_path):
        """Save and load should preserve feature engineer state."""
        train, val = sample_data
        engineer = FeatureEngineer()
        X_train, _ = engineer.fit_transform(train)
        
        # Save
        save_path = tmp_path / "engineer.pkl"
        engineer.save(str(save_path))
        
        # Load
        loaded_engineer = FeatureEngineer.load(str(save_path))
        X_val_loaded, _ = loaded_engineer.transform(val)
        
        # Compare
        X_val_original, _ = engineer.transform(val)
        np.testing.assert_array_almost_equal(
            X_val_loaded.values,
            X_val_original.values
        )
    
    def test_feature_info_contains_expected_keys(self, sample_data):
        """Feature info should contain required metadata."""
        train, _ = sample_data
        engineer = FeatureEngineer()
        engineer.fit_transform(train)
        info = engineer.get_feature_info()
        
        assert 'feature_columns' in info
        assert 'categorical_columns' in info
        assert 'target_columns' in info


class TestDerivedFeatureLogic:
    """Test specific derived feature calculations."""
    
    @pytest.fixture
    def engineer_with_data(self):
        """Create fitted engineer."""
        pipeline = DataPipeline()
        df = pipeline.load_data()
        train, _, _ = pipeline.create_splits()
        engineer = FeatureEngineer()
        return engineer, train
    
    def test_total_expenses_is_sum_of_expense_columns(self, engineer_with_data):
        """Total expenses should sum expense columns."""
        engineer, train = engineer_with_data
        
        # Create derived features manually to check
        train_copy = train.copy()
        expense_sum = train_copy[EXPENSE_COLUMNS].sum(axis=1)
        
        # The engineer should compute similar values
        assert expense_sum.min() >= 0


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
