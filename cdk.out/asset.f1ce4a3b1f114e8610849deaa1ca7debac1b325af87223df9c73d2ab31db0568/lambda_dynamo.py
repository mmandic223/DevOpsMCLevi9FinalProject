from __future__ import print_function

import json
from curses import raw
from email import message
from urllib import response

import boto3

print('Loading function')

dynamodb = boto3.client('dynamodb')
dynamo = boto3.resource('dynamodb').Table("lambda_api_table")

def handler(event, context):
    '''Provide an event that contains the following keys:
      - payload: a parameter to pass to the operation being performed
    '''
    
    if event['path'] == '/api/v1/createPerson':
        body = json.loads(event["body"])
        responseBody = "POST method"
        
        dynamodb.put_item(TableName="lambda_api_table", Item={'id':{'S': body["payload"]["Item"]["id"]}})

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(responseBody),
            "isBase64Encoded": False
        };

    elif event['path'] == '/api/v1/getPerson':
        responseBody = dynamodb.get_item(TableName="lambda_api_table", Key={'id':{'S': event["queryStringParameters"]["id"]}})

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(responseBody),
            "isBase64Encoded": False
        };
        

    

    
        