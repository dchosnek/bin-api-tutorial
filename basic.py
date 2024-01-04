"""
This is a basic lambda handler whose only purpose is to return the event back
to the client. This is useful for initial development of a new endpoint without
having to look through CloudWatch Logs for the event structure.
"""

import json

def lambda_handler(event, context):

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(event)
    }
