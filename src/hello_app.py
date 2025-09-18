"""
Guild Hello Service - Simple Lambda for DevOps Pipeline Demo

This is intentionally simple application code. 
The real challenge is deploying it properly with Infrastructure as Code!
"""

import json
import logging
import os
from typing import Dict, Any
import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))

def get_greeting_message() -> str:
    """
    Get greeting message from SSM Parameter Store with environment fallback.
    This demonstrates basic configuration management for DevOps patterns.
    """
    try:
        ssm = boto3.client('ssm')
        response = ssm.get_parameter(Name='/guild/hello-service/message')
        message = response['Parameter']['Value']
        logger.info("Retrieved message from SSM Parameter Store")
        return message
    except Exception as e:
        logger.warning(f"SSM parameter not found, using fallback: {e}")
        return os.getenv('GREETING_MESSAGE', 'Hello from Guild!')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Simple Lambda handler - the real challenge is deploying this properly!
    """
    request_id = getattr(context, 'aws_request_id', 'local-test')
    
    logger.info(f"Processing request {request_id}")
    
    try:
        # Get configurable greeting message
        message = get_greeting_message()
        
        # Get optional name from event
        name = None
        if 'body' in event:
            # API Gateway format
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
            name = body.get('name')
        else:
            # Direct invocation format
            name = event.get('name')
        
        # Build response
        if name:
            response_message = f"{message} Welcome, {name}!"
        else:
            response_message = message
        
        response = {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'message': response_message,
                'environment': os.getenv('ENVIRONMENT', 'dev'),
                'version': os.getenv('SERVICE_VERSION', '1.0.0'),
                'request_id': request_id
            })
        }
        
        logger.info(f"Request {request_id} completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Request {request_id} failed: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Internal Server Error',
                'request_id': request_id
            })
        }

# For local testing
if __name__ == "__main__":
    class MockContext:
        aws_request_id = "local-test-123"
    
    # Test direct invocation
    result = lambda_handler({'name': 'DevOps Engineer'}, MockContext())
    print(json.dumps(json.loads(result['body']), indent=2))

