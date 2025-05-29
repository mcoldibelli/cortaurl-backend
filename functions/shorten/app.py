from datetime import datetime, timezone, timedelta
from http import HTTPStatus
import os, json
from utils import normalize_url, generate_code, is_valid_domain
from db import get_table
import sys
sys.path.append('/opt/python')
from firebase_auth import verify_token

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "https://www.cortaurl.com.br",
    "Access-Control-Allow-Headers": "Authorization,Content-Type",
    "Access-Control-Allow-Methods": "OPTIONS,POST"
}

def lambda_handler(event, context):
    try:
        # Robustly detect OPTIONS preflight
        method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
        if (method and method.upper() == 'OPTIONS') or (event.get('routeKey', '').endswith('OPTIONS')):
            return {
                "statusCode": HTTPStatus.OK,
                "headers": CORS_HEADERS,
                "body": ""
        }

        headers = event.get('headers', {}) or {}
        auth_header = headers.get('Authorization')
        user = 'unknown'
        if auth_header:
            try:
                decoded_token = verify_token(auth_header)
                user = decoded_token['uid']
            except Exception:
                user = 'unknown'

        if not event.get('body'):
            return {
                "statusCode": HTTPStatus.BAD_REQUEST,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Missing request body"})
            }
        try:
            data = json.loads(event['body'])
        except Exception:
            return {
                "statusCode": HTTPStatus.BAD_REQUEST,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Invalid JSON in request body"})
            }

        expires_in_days = data.get('expires_in_days', 30)
        expires_at = (datetime.now(timezone.utc) + timedelta(days=expires_in_days)).isoformat()
        original_url = data.get('original_url')

        if not original_url or not is_valid_domain(original_url):
            return {
                "statusCode": HTTPStatus.BAD_REQUEST,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Invalid or missing URL"})
            }
        
        table = get_table()
        normalized_url = normalize_url(original_url)
        short_code = generate_code()
        item = {
            'short_code': short_code,
            'original_url': normalized_url,
            'created_by': user,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'expires_at': expires_at
        }
        table.put_item(Item=item)

        return {
            "statusCode": HTTPStatus.CREATED,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "short_code": short_code,
                "original_url": normalized_url
            })
        }
    except Exception as e:
        return {
            "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)})
        }
