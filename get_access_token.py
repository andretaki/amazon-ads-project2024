import json
import http.client
import logging

# Initialize Logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def obtain_access_token(refresh_token, client_id, client_secret):
    try:
        conn = http.client.HTTPSConnection("api.amazon.com")
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = f"grant_type=refresh_token&refresh_token={refresh_token}&client_id={client_id}&client_secret={client_secret}"

        conn.request("POST", "/auth/o2/token", body=payload, headers=headers)
        response = conn.getresponse()
        data = json.loads(response.read().decode('utf-8'))

        if response.status != 200:
            logger.error(f"Error fetching access token. Status code: {response.status}, Response: {data}")
            return None

        return data.get('access_token')
    except Exception as e:
        logger.error(f"Exception while fetching access token: {str(e)}")
        return None

def lambda_handler(event, context):
    # Log the event payload for debugging purposes
    logger.info(f"Event payload: {json.dumps(event)}")

    # Extract the values from the 'body' key of the event payload and parse it
    body = json.loads(event.get('body', '{}'))
    refresh_token = body.get('refresh_token')
    client_id = body.get('client_id')
    client_secret = body.get('client_secret')
    
    if not all([refresh_token, client_id, client_secret]):
        logger.error("Required values are missing in the event payload")
        return {'statusCode': 400, 'body': 'Missing required values'}

    access_token = obtain_access_token(refresh_token, client_id, client_secret)
    if not access_token:
        return {'statusCode': 400, 'body': 'Unable to retrieve access token'}

    return {
        'statusCode': 200,
        'body': {
            'access_token': access_token,
            'client_id': client_id
        }
    }
