import json
import boto3
import os
import jwt
from datetime import datetime, timedelta, timezone

SECRET_PHRASE = os.getenv('SECRET_PHRASE')
TABLE_NAME = os.getenv('TABLE_NAME')
table = boto3.resource('dynamodb').Table(TABLE_NAME)

def lambda_handler(event, context):

    print(event)
    
    # email must be a valid field or this function would not have been called
    # email = event.get('email')
    email = event['queryStringParameters']['email']
    
    # check if email already exists in the database
    response = table.query(
        KeyConditionExpression='email = :email',
        ExpressionAttributeValues={':email': email}
    )
    
    # user exists
    if response.get('Items', []):
        db_row = response['Items'][0]
        existing_token = db_row['jwt']
        refresh_token = False
        try:
            jwt.decode(existing_token, SECRET_PHRASE, algorithms=["HS256"])
            print("Existing user with valid token. No token will be generated.")
        except jwt.ExpiredSignatureError:
            refresh_token = True
            print("Existing user token is expired. Generating a new one.")
        except jwt.InvalidSignatureError:
            refresh_token = True
            print("Existing user token has invalid signature. Generating a new one.")
        
    # user does not exist
    else:
        refresh_token = True
        db_row = dict(
            email=email,
            jwt="",
            bins={}
        )
        print("New user. Generating a new token.")
        
    # now we know if we need to generate a new token or not
    if refresh_token:
        expiration = datetime.now(tz=timezone.utc)+timedelta(minutes=10)
        payload = dict(
            email=email,
            exp=expiration,
            expiration=expiration.strftime('%d %b %Y, %H:%M:%S %Z')
        )
        new_token = jwt.encode(payload, SECRET_PHRASE, algorithm="HS256")
        db_row['jwt'] = new_token
        
        # write new user to the database or update existing user
        response = table.put_item(Item=db_row)
    
    # Return value based on whether we generated a new token or not.
    # An existing token is never resent.
    
    if refresh_token:
    
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"token": new_token})
        }
        
    else:
        
        return {
            "statusCode": 403,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": ""
        }
