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
    
    # check if email already exists in the database; the response will be null
    # if the user does not exist
    response = table.get_item(Key={'email': email})
    db_row = response.get('Item')
    
    # user exists
    if db_row:
        existing_token = db_row['jwt']
        refresh_token = False
        try:
            jwt.decode(existing_token, SECRET_PHRASE, algorithms=["HS256"])
            print("Existing user with valid token. No token will be generated.")
        except:
            refresh_token = True
            db_row['bins'] = {}
            print("Issue with existing token. Generating a new one.")
        
    # user does not exist
    else:
        refresh_token = True
        db_row = dict(
            email=email,
            jwt="",
            bins={},
            created=datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        )
        print("New user. Generating a new token.")
        
    # now we know if we need to generate a new token or not
    if refresh_token:
        expiration = datetime.now(tz=timezone.utc)+timedelta(hours=4)
        payload = dict(
            email=email,
            exp=expiration
        )
        new_token = jwt.encode(payload, SECRET_PHRASE, algorithm="HS256")
        db_row['jwt'] = new_token
        
        # write new user to the database or update existing user
        response = table.put_item(Item=db_row)
    
        # Return value based on whether we generated a new token or not.
        # An existing token is never resent.

        body = dict(
            token=new_token,
            expiration=expiration.strftime('%d %b %Y, %H:%M:%S %Z')
        )
    
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(body)
        }
    
    # new token is not generated for one of several reasons
    else:
        
        return {
            "statusCode": 403,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": ""
        }
