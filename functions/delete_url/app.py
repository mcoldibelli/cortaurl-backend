import os, json, boto3
from http import HTTPStatus
from db import get_table

def lambda_handler(event, context):
    user = event['requestContext']['authorizer']['claims']['sub']
    short_code = event['pathParameters']['short_code']
    table = get_table()

    response = table.get_item(Key={'short_code': short_code})
    item = response.get('Item')

    if not item:
        return {
            "statusCode": HTTPStatus.NOT_FOUND,
            "body": json.dumps({"error": "Short URL not found"})
        }

    if item['created_by'] != user:
        return {
            "statusCode": HTTPStatus.FORBIDDEN,
            "body": json.dumps({"error": "Not authorized to delete this URL"})
        }

    table.delete_item(Key={'short_code': short_code})

    return {
        "statusCode": HTTPStatus.NO_CONTENT,
        "body": ""
    }