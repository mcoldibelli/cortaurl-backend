import os, json
from http import HTTPStatus
from boto3.dynamodb.conditions import Attr
from db import get_table


def lambda_handler(event, context):
    user = event['requestContext']['authorizer']['claims']['sub']
    table = get_table()

    response = table.scan(
        FilterExpression=Attr('created_by').eq(user)
    )

    items = response.get('Items', [])
    return {
        "statusCode": HTTPStatus.OK,
        "body": json.dumps({
            "items": items
        })
    }