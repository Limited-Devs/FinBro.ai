"""
Tests for prediction API endpoints.
"""
import pytest
import json


class TestHealthEndpoint:
    """Tests for /api/health endpoint."""
    
    def test_health_returns_200(self, client):
        """Health endpoint should return 200."""
        response = client.get('/api/health')
        assert response.status_code == 200
    
    def test_health_returns_status(self, client):
        """Health endpoint should return status field."""
        response = client.get('/api/health')
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] in ['healthy', 'degraded', 'unhealthy']
    
    def test_health_returns_components(self, client):
        """Health endpoint should return components."""
        response = client.get('/api/health')
        data = json.loads(response.data)
        assert 'components' in data
        assert 'ml_models' in data['components']


class TestAPIRoot:
    """Tests for /api/ root endpoint."""
    
    def test_root_returns_200(self, client):
        """Root endpoint should return 200."""
        response = client.get('/api/')
        assert response.status_code == 200
    
    def test_root_returns_version(self, client):
        """Root endpoint should return version."""
        response = client.get('/api/')
        data = json.loads(response.data)
        assert 'version' in data
        assert 'status' in data


class TestPredictionEndpoint:
    """Tests for /api/predict endpoint."""
    
    def test_predict_without_body_returns_400(self, client):
        """Predict without body should return 400."""
        response = client.post('/api/predict')
        assert response.status_code == 400
    
    def test_predict_with_invalid_json_returns_400(self, client):
        """Predict with invalid JSON should return 400."""
        response = client.post(
            '/api/predict',
            data='not json',
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_predict_with_missing_fields_returns_400(self, client):
        """Predict with missing fields should return 400."""
        response = client.post(
            '/api/predict',
            json={"Income": 50000}
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == True
        assert data['error_code'] == 'VALIDATION_ERROR'
    
    def test_predict_with_valid_data_returns_200(self, client, sample_prediction_request):
        """Predict with valid data should return 200."""
        response = client.post('/api/predict', json=sample_prediction_request)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'savings_model' in data
        assert 'amount_model' in data
        assert 'multi_task_model' in data
    
    def test_predict_response_structure(self, client, sample_prediction_request):
        """Verify prediction response structure."""
        response = client.post('/api/predict', json=sample_prediction_request)
        data = json.loads(response.data)
        
        # Check savings model structure
        assert 'can_achieve_savings' in data['savings_model']
        assert 'confidence' in data['savings_model']
        
        # Check amount model structure
        assert 'recommended_savings' in data['amount_model']
        
        # Check multi-task model structure
        assert 'can_achieve_savings' in data['multi_task_model']
        assert 'financial_risk' in data['multi_task_model']
        assert 'risk_score' in data['multi_task_model']


class TestDataEndpoint:
    """Tests for /api/data endpoint."""
    
    def test_data_returns_200(self, client):
        """Data endpoint should return 200."""
        response = client.get('/api/data')
        assert response.status_code == 200
    
    def test_data_returns_predictions_array(self, client):
        """Data endpoint should return predictions array."""
        response = client.get('/api/data')
        data = json.loads(response.data)
        assert 'predictions' in data
        assert isinstance(data['predictions'], list)
    
    def test_data_respects_limit(self, client):
        """Data endpoint should respect limit param."""
        response = client.get('/api/data?limit=5')
        assert response.status_code == 200


class TestChatEndpoint:
    """Tests for /api/chat endpoint."""
    
    def test_chat_without_body_returns_400(self, client):
        """Chat without body should return 400."""
        response = client.post('/api/chat/')
        assert response.status_code == 400
    
    def test_chat_with_empty_message_returns_400(self, client):
        """Chat with empty message should return 400."""
        response = client.post('/api/chat/', json={"message": ""})
        assert response.status_code == 400
    
    def test_chat_with_valid_message_returns_200(self, client):
        """Chat with valid message should return 200."""
        response = client.post('/api/chat/', json={"message": "Hello!"})
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'response' in data
