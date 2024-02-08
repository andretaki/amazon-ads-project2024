# Original Lambda Function: send_report_request.py

import http.client
import json
import logging
from datetime import datetime, timedelta

# Constants
PROFILE_ID = '2427340553944639'  # Replace with your actual profile ID

# Initialize logger
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def calculate_date_range(lookback_days=30):
    """Calculate start and end dates based on lookback days."""
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=lookback_days)
    return start_date.isoformat(), end_date.isoformat()

def construct_headers(client_id, access_token):
    """Construct headers for the API request."""
    return {
        'Content-Type': 'application/vnd.createasyncreportrequest.v3+json',
        'Amazon-Advertising-API-ClientId': client_id,
        'Amazon-Advertising-API-Scope': PROFILE_ID,
        'Authorization': f'Bearer {access_token}'
    }

def construct_campaign_payload(start_date, end_date):
    """Construct the payload for the Campaign report request."""
    return {
        "name": f"Campaign report {start_date} - {end_date}",
        "startDate": start_date,
        "endDate": end_date,
        "configuration": {
            "adProduct": "SPONSORED_PRODUCTS",
            "groupBy": ["campaign"],
            "columns": ["impressions","clicks","cost"],
            "reportTypeId": "spCampaigns",
            "timeUnit": "SUMMARY",
            "format": "GZIP_JSON"
        }
    }

def send_report_request(client_id, access_token):
    """Send report request to Amazon's Advertising API."""
    start_date, end_date = calculate_date_range()
    headers = construct_headers(client_id, access_token)

    payload = construct_campaign_payload(start_date, end_date)

    conn = http.client.HTTPSConnection("advertising-api.amazon.com")
    try:
        conn.request("POST", "/reporting/reports", body=json.dumps(payload), headers=headers)
        response = conn.getresponse()
        response_data = response.read().decode()
        logger.info(f"Response data: {response_data}")

        data = json.loads(response_data)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        return {
            "report_request": {
                "error": f"Failed to parse JSON: {e}",
                "status": "ERROR"
            }
        }
    finally:
        conn.close()

    return {"report_request": data}

def lambda_handler(event, context):
    report_request = event['report_request'] 
    client_id = event['client_id']                
    access_token = event['access_token']  

    # *** Add the error handling here ***
    try:
        status = report_request["status"]  # Try to extract the status
        # Use the status value (Your original logic that used the 'status')
    except KeyError:
        logger.error("No 'status' key found in the report_request")
        # Handle the missing status situation gracefully 

    logger.info(f"Received event: {event}")

    body = event.get('body', {})
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing 'body' from event: {e}")
            return {"error": "Invalid JSON format in event 'body'", "status": "ERROR"}

    client_id = body.get('client_id')
    access_token = body.get('access_token')

    if not isinstance(client_id, str) or not isinstance(access_token, str):
        logger.error("client_id or access_token is not a string.")
        return {"error": "client_id or access_token is not a string.", "status": "ERROR"}

    campaign_report = send_report_request(client_id, access_token)
    return {
        "campaign_report": campaign_report,
        "client_id": client_id,
        "access_token": access_token,
    }
