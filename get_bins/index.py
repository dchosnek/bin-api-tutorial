import json
import boto3
import os
import jwt

SECRET_PHRASE = os.getenv('SECRET_PHRASE')
TABLE_NAME = os.getenv('TABLE_NAME')
table = boto3.resource('dynamodb').Table(TABLE_NAME)

def validate_token(event, secret):
    if 'Authorization' not in event['headers']:
        return (400, None)
        
    auth = event['headers']['Authorization']
    if 'Bearer' not in auth:
        return (400, None)
        
    token = auth.replace('Bearer ', '')
    print(token)
    try:
        decoded = jwt.decode(token, secret, algorithms=["HS256"])
    except Exception as error:
        print("An exception occurred:", type(error).__name__)
        return (401, None)
        
    return (200, decoded['email'])

    

def lambda_handler(event, context):
    print("EVENT IS BELOW")
    print(event)
    
    status_code, email = validate_token(event, SECRET_PHRASE)
    
    if email is None:
        body = ""
    
    else:
        # read the bins from the database
        response = table.query(
            KeyConditionExpression='email = :email',
            ExpressionAttributeValues={':email': email}
        )
        db_row = response['Items'][0]
        body = json.dumps(dict(bins=[k for k in db_row['bins']]))
        
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": body
    }
    