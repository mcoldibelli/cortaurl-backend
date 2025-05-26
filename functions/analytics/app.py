import os, json, boto3
from http import HTTPStatus
from collections import Counter

dynamodb = boto3.resource('dynamodb')
click_table = dynamodb.Table(os.environ['CLICK_EVENTS_TABLE'])

def lambda_handler(event, context):
    short_code = event['pathParameters']['short_code']

    # Get all click events for this short_code
    response = click_table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('short_code').eq(short_code)
    )

    items = response.get('Items', [])

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
            "devices": user_agent_counts.most_common()
        })
    }
