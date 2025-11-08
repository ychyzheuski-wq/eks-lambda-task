import json
import logging
import boto3
from typing import Dict, Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SSM_PARAMETER_NAME = "/platform/account/env"

def get_ssm_environment_value(param_name: str) -> str:
    try:
        ssm_client = boto3.client('ssm') 
        
        response = ssm_client.get_parameter(
            Name=param_name,
            WithDecryption=True
        )

        env_value = response['Parameter']['Value'].lower()
        logger.info(f"Retrieved SSM value: {env_value}")
        return env_value
    except Exception as e:
        logger.error(f"Error reading SSM parameter {param_name}: {e}")
        raise

def generate_helm_values(env: str) -> Dict[str, Any]:
    replica_map = {
        "development": 1, 
        "stage": 2, 
        "prod": 2
    }

    replica_count = replica_map.get(env)

    if replica_count is None:
        logger.warning(f"Unknown environment '{env}', defaulting replica_count to 1")
        replica_count = 1
    
    response_data = {"ReplicaCount": str(replica_count)}
    logger.info(f"Returning response data: {response_data}")
    return response_data

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler for Custom Resource events."""
    logger.info(f"Received event: {json.dumps(event, indent=2)}")
    
    request_type = event['RequestType']
    
    if request_type == 'Delete':
        logger.info("Handling DELETE request, no cleanup needed.")
        return {"PhysicalResourceId": event.get('PhysicalResourceId', context.log_stream_name)}

    try:
        ssm_param_name = event.get('ResourceProperties', {}).get('SsmParameterName', SSM_PARAMETER_NAME)

        env_value = get_ssm_environment_value(ssm_param_name)
        
        response_data = generate_helm_values(env_value)
        
        logger.info(f"Returning successful response: {response_data}")
        
        return {
            "PhysicalResourceId": event.get('PhysicalResourceId', context.log_stream_name),
            "Data": response_data
        }
        
    except Exception as e:
        error_message = f"EXECUTION FAILED: {request_type} request failed during processing: {e}"
        logger.error(error_message)
        raise
