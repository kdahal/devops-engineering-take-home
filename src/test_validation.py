"""
Simple validation tests for the Guild Hello Service.

These tests ensure the basic application functionality works correctly
before providing it to DevOps engineering candidates.

Run with: python -m pytest test_validation.py -v
"""

import json
import os
import pytest
from unittest.mock import patch, MagicMock
import hello_app


class MockContext:
    """Mock Lambda context for testing."""
    aws_request_id = "test-request-123"


@pytest.fixture
def mock_context():
    """Provide a mock Lambda context."""
    return MockContext()


def test_lambda_handler_basic_functionality(mock_context):
    """Test basic Lambda handler functionality."""
    event = {"name": "Test Engineer"}
    
    with patch('hello_app.get_greeting_message', return_value="Hello from Guild!"):
        response = hello_app.lambda_handler(event, mock_context)
    
    # Validate response structure
    assert response['statusCode'] == 200
    assert 'Content-Type' in response['headers']
    assert response['headers']['Content-Type'] == 'application/json'
    
    # Validate response body
    body = json.loads(response['body'])
    assert 'message' in body
    assert 'Test Engineer' in body['message']
    assert body['request_id'] == 'test-request-123'
    assert 'environment' in body
    assert 'version' in body


def test_lambda_handler_without_name(mock_context):
    """Test Lambda handler with no name provided."""
    event = {}
    
    with patch('hello_app.get_greeting_message', return_value="Hello from Guild!"):
        response = hello_app.lambda_handler(event, mock_context)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['message'] == "Hello from Guild!"


def test_lambda_handler_api_gateway_format(mock_context):
    """Test Lambda handler with API Gateway event format."""
    event = {
        "body": json.dumps({"name": "API Test User"})
    }
    
    with patch('hello_app.get_greeting_message', return_value="Hello from Guild!"):
        response = hello_app.lambda_handler(event, mock_context)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'API Test User' in body['message']


def test_configuration_with_ssm_success():
    """Test configuration retrieval from SSM Parameter Store."""
    mock_ssm = MagicMock()
    mock_ssm.get_parameter.return_value = {
        'Parameter': {'Value': 'Hello from SSM!'}
    }
    
    with patch('boto3.client', return_value=mock_ssm):
        message = hello_app.get_greeting_message()
        assert message == 'Hello from SSM!'
        mock_ssm.get_parameter.assert_called_once_with(Name='/guild/hello-service/message')


def test_configuration_fallback_to_environment():
    """Test fallback to environment variable when SSM fails."""
    mock_ssm = MagicMock()
    mock_ssm.get_parameter.side_effect = Exception("SSM unavailable")
    
    with patch('boto3.client', return_value=mock_ssm):
        with patch.dict(os.environ, {'GREETING_MESSAGE': 'Hello from Environment!'}):
            message = hello_app.get_greeting_message()
            assert message == 'Hello from Environment!'


def test_configuration_default_fallback():
    """Test using default value when no configuration is available."""
    mock_ssm = MagicMock()
    mock_ssm.get_parameter.side_effect = Exception("SSM unavailable")
    
    with patch('boto3.client', return_value=mock_ssm):
        with patch.dict(os.environ, {}, clear=True):
            message = hello_app.get_greeting_message()
            assert message == 'Hello from Guild!'


def test_error_handling(mock_context):
    """Test that application handles errors gracefully."""
    event = {"name": "Test User"}
    
    # Mock get_greeting_message to raise an exception
    with patch('hello_app.get_greeting_message', side_effect=Exception("Test error")):
        response = hello_app.lambda_handler(event, mock_context)
    
    assert response['statusCode'] == 500
    body = json.loads(response['body'])
    assert body['error'] == 'Internal Server Error'
    assert body['request_id'] == 'test-request-123'


def test_environment_variables_in_response(mock_context):
    """Test that environment variables are properly included."""
    event = {}
    
    with patch('hello_app.get_greeting_message', return_value="Hello!"):
        with patch.dict(os.environ, {'ENVIRONMENT': 'test', 'SERVICE_VERSION': '2.0.0'}):
            response = hello_app.lambda_handler(event, mock_context)
    
    body = json.loads(response['body'])
    assert body['environment'] == 'test'
    assert body['version'] == '2.0.0'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
