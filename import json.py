import json
import boto3
import os
import redis
import urllib.request
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.client('dynamodb')


def lambda_handler(event, context):
    logger.info('Received event:')
    logger.info(json.dumps(event))

    # Redis configuration
    redis_host = "demo-redis-private-001.6xkwqy.0001.aps1.cache.amazonaws.com"
    redis_port = int(6379)
    
    
   

    try:
        redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)
        logger.info("Redis client: %s", redis_client)
        logger.info("Redis server is reachable.")
        item = {
            'year': {'N': '111949'},
            'title': {'S': 'a12T3yZf6'},
        }
        # Set the item in Redis
        redis_key = 'your_redis_key'
        redis_value = json.dumps(item)
        redis_client.set(redis_key, redis_value)
        logger.info(f"Item set in Redis with key '{redis_key}'")
        
   
        dynamodb_table_name = 'newmovie'

        items = {
            'year': {'N': '1949221'},
            'title': {'S': 'a1T3y22Zf6'},
        }
    

        response = dynamodb.put_item(
            TableName=dynamodb_table_name,
            Item=items
        )
        logger.info(f"DynamoDB PutItem response: {response}")
        # logger.error(f"Error performing DynamoDB PutItem: {e}")
            
        url = "http://www.google.com"
        try:
            response = urllib.request.urlopen(url, timeout=5)
            if response.getcode() == 200:
                logger.info("HTTP request to Google successful")
            else:
                logger.warning(f"HTTP request to Google failed. Status code: {response.getcode()}")
        except urllib.error.URLError as e:
            logger.error(f"HTTP request to Google failed. {e.reason}")
    
        return {
            'statusCode': 200,
            'body': json.dumps('Hello from your new Amplify Python lambda!')
        }

        
    except Exception as e:
        logger.error(f"Error connecting to Redis: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error connecting to Redis server.')
        }