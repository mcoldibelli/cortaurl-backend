import logging, json
from http import HTTPStatus
from boto3.dynamodb.conditions import Attr
from firebase_auth import require_auth

@require_auth
def lambda_handler(event, context):
    origin = event.get('headers', {}).get('origin', 'https://www.cortaurl.com.br')
    CORS_HEADERS = {
        "Access-Control-Allow-Headers": "Authorization,Content-Type",
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Methods": "OPTIONS,GET"
    }

    method = event.get('httpMethod', event.get('requestContext', {}).get('method'))
    if method == 'OPTIONS':
        return {
            "statusCode": HTTPStatus.OK,
            "headers": CORS_HEADERS,
            "body": ""
        }

    from db import get_table

    user = event['user']
    logging.info(f"Listando URLs para UID: {user['uid']}")

    table = get_table()
    response = table.scan(FilterExpression=Attr('created_by').eq(user['uid']))
    items = response.get('Items', [])

    return {
        "statusCode": HTTPStatus.OK,
        "headers": CORS_HEADERS,
        "body": json.dumps({"items": items or []})
    }