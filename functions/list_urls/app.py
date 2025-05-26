import os, json
from http import HTTPStatus
from db import get_table

def lambda_handler(event, context):
    user = event['requestContext']['authorizer']['claims']['sub']
    table = get_table()

    response = table.scan(
        FilterExpression="created_by = :u",
        ExpressionAttributeValues={":u": user}
    )

    items = response.get('Items', [])
    return {
        "statusCode": HTTPStatus.OK,
        "body": json.dumps({
            "items": items
        })
    }