"""
Tests for data pipeline.
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data_pipeline import DataPipeline, DataValidationError, REQUIRED_COLUMNS


class TestDataPipeline:
    """Test data loading and validation."""
    
    def test_load_data_returns_dataframe(self):
        """Data pipeline should return a DataFrame."""
        pipeline = DataPipeline()
        df = pipeline.load_data()
        assert df is not None
        assert len(df) > 0
    
    def test_all_required_columns_present(self):
        """All required columns should be in the loaded data."""
        pipeline = DataPipeline()
        df = pipeline.load_data()
        for col in REQUIRED_COLUMNS:
            assert col in df.columns, f"Missing column: {col}"
    
    def test_create_splits_returns_three_dataframes(self):
        """Split should return train, val, and test DataFrames."""
        pipeline = DataPipeline()
        pipeline.load_data()
        train, val, test = pipeline.create_splits()
        
        assert len(train) > 0
        assert len(val) > 0
        assert len(test) > 0
    
    def test_splits_are_disjoint(self):
        """Train, val, and test sets should not overlap."""
        pipeline = DataPipeline()
        pipeline.load_data()
        train, val, test = pipeline.create_splits()
        
        train_indices = set(train.index)
        val_indices = set(val.index)
        test_indices = set(test.index)
        
        assert len(train_indices & val_indices) == 0
        assert len(train_indices & test_indices) == 0
        assert len(val_indices & test_indices) == 0
    
    def test_splits_preserve_data(self):
        """Total samples in splits should equal original data."""
        pipeline = DataPipeline()
        df = pipeline.load_data()
        train, val, test = pipeline.create_splits()
        
        total = len(train) + len(val) + len(test)
        assert total == len(df)
    
    def test_validation_report_exists(self):
        """Validation report should be generated."""
        pipeline = DataPipeline()
        pipeline.load_data(validate=True)
        report = pipeline.get_validation_report()
        assert isinstance(report, dict)
    
    def test_data_summary_contains_expected_keys(self):
        """Summary should contain expected information."""
        pipeline = DataPipeline()
        pipeline.load_data()
        summary = pipeline.get_data_summary()
        
        expected_keys = ['num_rows', 'num_columns', 'columns', 'dtypes']
        for key in expected_keys:
            assert key in summary
    
    def test_file_not_found_raises_error(self):
        """Missing file should raise FileNotFoundError."""
        pipeline = DataPipeline(data_path='/nonexistent/path.csv')
        with pytest.raises(FileNotFoundError):
            pipeline.load_data()


class TestDataSplitRatios:
    """Test split ratios are approximately correct."""
    
    def test_default_split_ratios(self):
        """Default splits should be approximately 70/15/15."""
        pipeline = DataPipeline()
        pipeline.load_data()
        train, val, test = pipeline.create_splits()
        
        total = len(train) + len(val) + len(test)
        train_ratio = len(train) / total
        val_ratio = len(val) / total
        test_ratio = len(test) / total
        
        # Allow 2% tolerance
        assert 0.68 < train_ratio < 0.72, f"Train ratio: {train_ratio}"
        assert 0.13 < val_ratio < 0.17, f"Val ratio: {val_ratio}"
        assert 0.13 < test_ratio < 0.17, f"Test ratio: {test_ratio}"


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
