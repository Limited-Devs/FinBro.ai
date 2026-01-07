"""Test configuration and fixtures."""
import pytest
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('testing')
    app.config['TESTING'] = True
    yield app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def sample_prediction_request():
    """Sample valid prediction request data."""
    return {
        "Income": 50000,
        "Age": 30,
        "Dependents": 2,
        "Occupation": "Salaried",
        "City_Tier": "Tier_1",
        "Rent": 15000,
        "Loan_Repayment": 5000,
        "Insurance": 2000,
        "Groceries": 8000,
        "Transport": 3000,
        "Eating_Out": 2000,
        "Entertainment": 1500,
        "Utilities": 2500,
        "Healthcare": 1000,
        "Education": 0,
        "Miscellaneous": 1000,
        "Desired_Savings_Percentage": 20,
        "Disposable_Income": 9000,
        "Potential_Savings_Groceries": 1000,
        "Potential_Savings_Transport": 500,
        "Potential_Savings_Eating_Out": 1000,
        "Potential_Savings_Entertainment": 500,
        "Potential_Savings_Utilities": 300,
        "Potential_Savings_Healthcare": 200,
        "Potential_Savings_Education": 0,
        "Potential_Savings_Miscellaneous": 500
    }
