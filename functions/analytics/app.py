import datetime
import os, json, boto3
from http import HTTPStatus
from collections import Counter
from firebase_auth import require_auth

dynamodb = boto3.resource('dynamodb')
click_table = dynamodb.Table(os.environ['CLICK_EVENTS_TABLE'])
url_table = dynamodb.Table(os.environ['SHORT_URLS_TABLE'])

def clicks_per_day(items):
    days = [datetime.fromisoformat(item['timestamp']).date() for item in items]
    return Counter(days)

@require_auth
def lambda_handler(event, context):
    user_id = event['user']['uid']  # Get user ID from Firebase token
    short_code = event['pathParameters']['short_code']

    # Fetch the short URL from the database
    url_resp = url_table.get_item(Key={'short_code': short_code})
    url_item = url_resp.get('Item')
    if not url_item:
        return {
            "statusCode": HTTPStatus.NOT_FOUND,
            "body": json.dumps({"error": "Short URL not found"})
        }

    if url_item['created_by'] != user_id:
        return {
            "statusCode": HTTPStatus.FORBIDDEN,
            "body": json.dumps({"error": "Not authorized to access this URL"})
        }

    # Get all click events for this short_code
    response = click_table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('short_code').eq(short_code)
    )

    items = response.get('Items', [])
    daily = clicks_per_day(items)

    total_clicks = len(items)
    unique_ips = len({item['ip'] for item in items if 'ip' in item})

    country_counts = Counter(item.get('country', 'unknown') for item in items)
    referrer_counts = Counter(item.get('referrer', 'unknown') for item in items)
    user_agent_counts = Counter(item.get('user_agent', 'unknown') for item in items)

    return {
        "statusCode": HTTPStatus.OK,
        "body": json.dumps({
            "short_code": short_code,
            "total_clicks": total_clicks,
            "unique_visitors": unique_ips,
            "countries": country_counts.most_common(),
            "referrers": referrer_counts.most_common(),
            "devices": user_agent_counts.most_common(),
            "clicks_over_time": [
                {"date": str(date), "clicks": count} 
                for date, count in sorted(daily.items())
            ]
        })
    }
