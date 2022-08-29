import json
import logging
import os
import random
from datetime import datetime

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("dev-dynamotable-MarkoMandic-masterclass")

         
def lambda_handler(event, context):
    """
    Lambda for making post request to DB
    on request from API Gateway.
    """
    try:
        body = json.loads(event["body"])
        responseBody = "POST method"
        
        dynamodb.put_item(TableName=table, Item={'id':{'S': body["payload"]["Item"]["id"]}})

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(responseBody),
            "isBase64Encoded": False
        };
    except:
        logger.exception('Error occured when attempting to post items to dynamodb')
