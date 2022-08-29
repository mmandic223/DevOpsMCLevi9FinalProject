import json
import logging
import os

import boto3


logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('ddbtablename'))

def lambda_handler(event, context):
    """
    Lambda for making get request to DB
    on request from API Gateway.
    """
    
    try:
        logger.info(event)
        response= table.scan()
        print(response)
        print(response['Items'])

        return {
            'statusCode': 200,
            'body': json.dumps(response["Items"]),
            'headers': {
                'Content-Type': 'application/json',
            },
            "isBase64Encoded":'false'
        }
    except:
        logger.exception('Error occured when attempting to retrive items from dynamodb')


