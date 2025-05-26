import boto3
import os

def get_table():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.getenv('SHORT_URLS_TABLE'))
    return table