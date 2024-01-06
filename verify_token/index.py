import json
import os
import jwt
from datetime import datetime

SECRET_PHRASE = os.getenv('SECRET_PHRASE')

def lambda_handler(event, context):
    # retrieve the token from the path of the event
    token = event['pathParameters']['token']

    # attempt to decode the token and set the appropriate status code for
    # different failure scenarios (and 200 for success)
    try:
        decoded = jwt.decode(token, SECRET_PHRASE, algorithms=["HS256"])
        print(F"Decoded JWT: {json.dumps(decoded)}")
        status_code = 200
    except jwt.ExpiredSignatureError:
        status_code = 401
    # this is a catch-all for the many ways a token could be incorrect
    except:
        status_code = 400
    
    # attempt to convert the 'exp' field to a datetime string; this will fail
    # if the decode failed, hence the use of try/except here
    try:
        timestamp = datetime.fromtimestamp(decoded['exp'])
        expiration = timestamp.strftime('%d %b %Y, %H:%M:%S UTC')
    except:
        expiration = "unknown"

    # if there is a problem with the token, return an empty body
    if status_code == 200:
        body = json.dumps(dict(
            token=token,
            expiration=expiration
        ))
    else:
        body = ""

    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": body
    }
