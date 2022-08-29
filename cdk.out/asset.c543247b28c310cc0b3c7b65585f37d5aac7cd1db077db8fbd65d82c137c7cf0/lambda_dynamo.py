import os
import string
import boto3
import json
import random
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv() 


logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.client('dynamodb')
table = dynamodb.Table(os.environ.get('ddbtablename'))
         
def lambda_handler(event, context):
     try:
        body = json.loads(event["body"])
        responseBody = "POST method"
        
        dynamodb.put_item(TableName=table, Item={'id':{'S': body["id"]}})

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