import os, json, boto3, firebase_admin
from firebase_admin import auth, credentials
from functools import wraps
from http import HTTPStatus

def get_firebase_cred_from_ssm():
    ssm = boto3.client('ssm')
    parameter = ssm.get_parameter(
        Name=os.environ['FIREBASE_SSM_PATH'],
        WithDecryption=True
    )
    cred_dict = json.loads(parameter['Parameter']['Value'])
    return credentials.Certificate(cred_dict)

if not firebase_admin._apps:
    cred = get_firebase_cred_from_ssm()
    firebase_admin.initialize_app(cred)

def verify_token(token):
    try:
        if token.startswith('Bearer '):
            token = token[7:]
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise Exception(f"Invalid token: {str(e)}")

def require_auth(f):
    @wraps(f)
    def decorated_function(event, context):
        if event.get('httpMethod') == 'OPTIONS':
            return {
                "statusCode": HTTPStatus.OK,
                "headers": {
                    "Access-Control-Allow-Origin": event.get('headers', {}).get('origin', '*'),
                    "Access-Control-Allow-Headers": "Authorization,Content-Type",
                    "Access-Control-Allow-Methods": "OPTIONS,GET,POST,DELETE"
                },
                "body": ""
            }
        headers = event.get('headers', {})
        auth_header = headers.get('Authorization')
        if not auth_header:
            return {
                "statusCode": HTTPStatus.UNAUTHORIZED,
                "headers": {
                    "Access-Control-Allow-Origin": headers.get('origin', '*'),
                    "Access-Control-Allow-Headers": "Authorization,Content-Type",
                    "Access-Control-Allow-Methods": "OPTIONS,GET,POST,DELETE"
                },
                "body": json.dumps({"error": "No authorization token provided"})
            }
        try:
            decoded_token = verify_token(auth_header)
            event['user'] = {
                'uid': decoded_token['uid'],
                'email': decoded_token.get('email'),
                'email_verified': decoded_token.get('email_verified', False)
            }
            return f(event, context)
        except Exception as e:
            return {
                "statusCode": HTTPStatus.UNAUTHORIZED,
                "headers": {
                    "Access-Control-Allow-Origin": headers.get('origin', '*'),
                    "Access-Control-Allow-Headers": "Authorization,Content-Type",
                    "Access-Control-Allow-Methods": "OPTIONS,GET,POST,DELETE"
                },
                "body": json.dumps({"error": str(e)})
            }
    return decorated_function
