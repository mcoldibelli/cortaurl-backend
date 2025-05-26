import os, json, boto3
from http import HTTPStatus
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['SHORT_URLS_TABLE'])
click_table = dynamodb.Table(os.environ['CLICK_EVENTS_TABLE'])

def lambda_handler(event, context):
    short_code = event['pathParameters']['short_code']

    # Get the short URL from the database
    response = table.get_item(Key={'short_code': short_code})
    item = response.get('Item')
    if not item:
        return {
            "statusCode": HTTPStatus.NOT_FOUND,
            "body": json.dumps({"error": "URL not found"})
        }

    # Gather analytics data
    headers = event.get('headers', {})
    user_agent = headers.get('User-Agent', 'unknown')
    referrer = headers.get('Referer', 'unknown')
    country = headers.get('CloudFront-Viewer-Country') or headers.get("X-Country-Code") or "unknown"
    ip = headers.get('X-Forwarded-For', 'unknown')
    
    # Log the click event
    try:

        click_table.put_item(Item={
            'short_code': short_code,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'country': country,
            'ip': ip,
            'user_agent': user_agent,
            'referrer': referrer
        })
    except Exception as e:
        pass

    return {
        "statusCode": HTTPStatus.FOUND,
        "headers": {
            "Location": item['original_url']
        },
        "body": ""
    }