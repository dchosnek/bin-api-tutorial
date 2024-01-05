import json
import boto3
import os
import jwt
import uuid

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
    
    # verify token and retrieve user email
    status_code, email = validate_token(event, SECRET_PHRASE)
    
    # if the email does not exist (due to invalid token), set body to empty
    if email is None:
        body = ""
    
    else:

        # generate a new and random UUID as the ID for the bin
        bin_id = str(uuid.uuid4())
        
        # add the new bin
        response = table.update_item(
            Key={'email':email},
            UpdateExpression="SET bins.#newBinKey = :newBinValue",
            ExpressionAttributeNames={'#newBinKey': bin_id},
            ExpressionAttributeValues={':newBinValue': ""},
            ReturnValues="UPDATED_NEW"
        )
        
        status_code = 201
        
        body = json.dumps(dict(binId=bin_id,contents=""))
        
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": body
    }