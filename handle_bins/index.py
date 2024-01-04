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
        return {
            "statusCode": status_code,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": ""
        }
    
    # retrieve the row from the table
    response = table.get_item(Key={'email': email})
    db_row = response.get('Item', dict())
    
    http_method = event['httpMethod']
    bin_id = event['pathParameters']['binId']
    bins = db_row.get('bins', dict())
    
    if bin_id not in bins:
        return {
            "statusCode": 404,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": ""
        }
    
    match http_method:
        
        case "GET":
            
            print("GET")

            status_code = 200
            body = json.dumps(bins.get(bin_id, ""))
        
        case "PUT":
            
            print("PUT")
                
            request_body = event.get('body', '{}')
            try:
                content_dict = json.loads(request_body)
                status_code = 200 if 'content' in content_dict else 400
                new_value = content_dict.get('content', '')
            except:
                status_code = 400

            if status_code == 200:
                response = table.update_item(
                    Key={'email':email},
                    UpdateExpression="SET bins.#newBinKey = :newBinValue",
                    ExpressionAttributeNames={'#newBinKey': bin_id},
                    ExpressionAttributeValues={':newBinValue': new_value},
                    ReturnValues="UPDATED_NEW"
                )
                body = ""
            else:
                body = json.dumps(event)
        
        case "DELETE":
            
            print("DELETE")
            status_code = 204
            body = ""
            response = table.update_item(
                Key={'email':email},
                UpdateExpression="REMOVE bins.#keyToRemove",
                ExpressionAttributeNames={'#keyToRemove': bin_id},
                ReturnValues="UPDATED_NEW"
            )
            
        case _:
            
            print("DEFAULT")
            status_code = 502
            body = ""
    

    
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": body
    }
