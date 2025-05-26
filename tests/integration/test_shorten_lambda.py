import http, os, json, boto3, sys
from moto import mock_aws
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../layers/shared/python')))

from functions.shorten.app import lambda_handler

@pytest.fixture
def dynamodb_table(monkeypatch):
    table_name = "ShortURLsTable"
    monkeypatch.setenv("SHORT_URLS_TABLE", table_name)

    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-2")
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "short_code", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "short_code", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST"
        )
        table.wait_until_exists()
        yield table

def test_lambda_handler_valid_url(dynamodb_table):
    from functions.shorten.app import lambda_handler
    event = {
        "body": json.dumps({"original_url": "https://www.google.com"}),
        "requestContext": {
            "authorizer": {
                "claims": {"sub": "test-user-id"}
            }
        }
    }
    result = lambda_handler(event, {})
    assert result["statusCode"] == http.HTTPStatus.CREATED
    body = json.loads(result["body"])
    assert body["original_url"] == "https://www.google.com"
    assert "short_code" in body

def test_lambda_handler_invalid_url(dynamodb_table):
    event = {
        "body": json.dumps({"original_url": "notaurl"}),
        "requestContext": {
            "authorizer": {
                "claims": {"sub": "test-user-id"}
            }
        }
    }
    result = lambda_handler(event, {})
    assert result["statusCode"] == http.HTTPStatus.BAD_REQUEST
    assert "Invalid" in result["body"]