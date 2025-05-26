import os, json
from http import HTTPStatus
from db import get_table

def lambda_handler(event, context):
    short_code = event['pathParameters']['short_code']
    table = get_table()
    response = table.get_item(Key={'short_code': short_code})
    item = response.get('Item')

    if item:
        return {
            "statusCode": HTTPStatus.FOUND,
            "headers": {
                "Location": item['original_url']
            },
            "body": ""
        }
    else:
        return {
            "statusCode": HTTPStatus.NOT_FOUND,
            "body": json.dumps({
                "error": "Short URL not found"
            })
        }
    