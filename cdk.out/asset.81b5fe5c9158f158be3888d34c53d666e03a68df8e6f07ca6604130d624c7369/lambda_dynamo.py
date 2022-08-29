import os
import boto3
import json
import random
import logging
from datetime import datetime


logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('ddbtablename'))

now = datetime.now()
current_time = now.strftime("%H:%M:%S")        
names = ["Marko", "Dejan", "Nikola", "Milica", "Stefan"]   
         
def lambda_handler(event, context):
    try:
        logger.info(event)
        table.put_item(Item={
            'id': current_time,
            'name': random.choice(names)
            }
        )
        message = {
            'message': 'Name/Date successfully commited to db'
        }
        return {
            'statusCode': 200,
            'body': json.dumps(message),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            "isBase64Encoded":'false'
        }
    except:
        logger.exception('Error occured when attempting to post items to dynamodb')