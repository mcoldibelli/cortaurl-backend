import os, json
from http import HTTPStatus
from db import get_table
from firebase_auth import require_auth

@require_auth
def lambda_handler(event, context):
    origin = event.get('headers', {}).get('origin', 'https://www.cortaurl.com.br')
    CORS_HEADERS = {
        "Access-Control-Allow-Headers": "Authorization,Content-Type",
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Methods": "OPTIONS,DELETE"
    }

    # Preflight OPTIONS
    method = event.get('httpMethod') or event.get('requestContext', {}).get('method')
    if method and method.upper() == 'OPTIONS':
        return {
            "statusCode": HTTPStatus.OK,
            "headers": CORS_HEADERS,
            "body": ""
        }

    user = event['user']['uid']
    short_code = event['pathParameters']['short_code']
    table = get_table()

    response = table.get_item(Key={'short_code': short_code})
    item = response.get('Item')

    if not item:
        return {
            "statusCode": HTTPStatus.NOT_FOUND,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": "Short URL not found"})
        }

    if item['created_by'] != user:
        return {
            "statusCode": HTTPStatus.FORBIDDEN,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": "Not authorized to delete this URL"})
        }

    table.delete_item(Key={'short_code': short_code})

    return {
        "statusCode": HTTPStatus.NO_CONTENT,
        "headers": CORS_HEADERS,
        "body": json.dumps({})
    }