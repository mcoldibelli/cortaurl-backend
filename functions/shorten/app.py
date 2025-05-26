from datetime import datetime
from http import HTTPStatus
import os, json
from layers.shared.python.db import get_table
from layers.shared.python.utils import generate_code, is_valid_url

def lambda_handler(event, context):
    try:
        user = event['requestContext']['authorizer']['claims']['sub']
    except (KeyError, TypeError):
        user = 'local-user'

    data = json.loads(event['body'])
    original_url = data.get('original_url')

    if not original_url or not is_valid_url(original_url):
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": json.dumps({"error": "Invalid or missing URL"})
        }
    
    table = get_table()
    short_code = generate_code()
    item = {
        'short_code': short_code,
        'original_url': original_url,
        'created_by': user,
        'created_at': datetime.now().isoformat()
    }
    table.put_item(Item=item)

    return {
        "statusCode": HTTPStatus.CREATED,
        "body": json.dumps({
            "short_code": short_code,
            "original_url": original_url
        })
    }