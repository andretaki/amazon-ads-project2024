import json
import logging
import boto3
from botocore.exceptions import ClientError

# Initialize Logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Constants
REGION_NAME = "us-east-1"

def get_secret(secret_name):
    """Fetch a secret from AWS Secrets Manager."""
    try:
        secrets_client = boto3.client('secretsmanager', region_name=REGION_NAME)
        response = secrets_client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        logger.error(f"Error retrieving secret {secret_name}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error retrieving secret {secret_name}: {e}")
        return None

    # Get the SecretString value and parse it as JSON
    try:
        secret_json = json.loads(response['SecretString'])
        return secret_json[secret_name]
    except KeyError:
        logger.error(f"{secret_name} not found in secrets response")
        return None
    except json.JSONDecodeError:
        logger.error(f"Error decoding secret JSON for {secret_name}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error processing secret {secret_name}: {e}")
        return None

def lambda_handler(event, context):
    try:
        client_secret = get_secret('client_secret')
        client_id = get_secret('client_id')
        refresh_token = get_secret('refresh_token')

        # Check if any secret is None (not retrieved successfully)
        if None in [client_secret, client_id, refresh_token]:
            raise ValueError("One or more required secrets could not be retrieved")

        # Wrap credentials inside a 'body' key
        body = {
            'client_secret': client_secret,
            'client_id': client_id,
            'refresh_token': refresh_token
        }

        return {
            'statusCode': 200,
            'body': json.dumps(body)  # Convert the body to a JSON string
        }
    except Exception as e:
        logger.error(f"Exception in lambda_handler: {str(e)}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}

