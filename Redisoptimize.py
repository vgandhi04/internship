import json
import os
from decimal import Decimal
import boto3
from boto3.dynamodb.conditions import Key
import redis

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
dynamodb_client = boto3.client('dynamodb')
env = os.environ.get('ENV')
aws_region = os.environ.get('REGION')

# Redis configuration
redis_host = os.environ.get('REDIS_ENDPOINT')
redis_port = int(6379)
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)


def get_data_from_redis(keys):
    try:
        pipeline = redis_client.pipeline()
        for key in keys:
            pipeline.get(json.dumps(key, sort_keys=True))
        data = pipeline.execute()
        return [json.loads(item) if item else None for item in data]
    except Exception as ex:
        print(f"Error getting data from Redis: {ex}")
        return [None] * len(keys)

def set_data_in_redis(data_list):
    try:
        pipeline = redis_client.pipeline()
        for data in data_list:
            pipeline.set(json.dumps(data, sort_keys=True), json.dumps(data))
        pipeline.execute()
        print("Data set in Redis")
    except Exception as ex:
        print(f"Error setting data in Redis: {ex}")


def process_request(event, context):
    print('Received event:')
    print(event)

    http_method = event['httpMethod']
    requested_data = json.loads(event['body'])
    
    try:
        if http_method == 'POST':
            inserted_items = []
            with dynamodb.Table(os.environ.get('API_TABLE_NAME')).batch_writer() as batch:
                for item in requested_data:
                    item = {key: int(value) if isinstance(value, Decimal) else value for key, value in item.items()}
                    batch.put_item(Item=item)
                    inserted_items.append(item)

            return {
                'statusCode': 200,
                'body': json.dumps(f'Successfully inserted {len(inserted_items)} items')
            }

        elif http_method == 'GET':
            total_redis_data = []
            total_dynamodb_data = []
            batch_size = 100
            try:
                for i in range(0, len(requested_data), batch_size):
                    batch_data = requested_data[i:i + batch_size]
                    keys_to_get = [{'year': int(item['year']), 'title': item['title']} for item in batch_data]

                    # Try to fetch data from Redis first
                    data_from_redis = get_data_from_redis(keys_to_get)
                    print("Data from Redis", data_from_redis)
                    total_redis_data.extend(data_from_redis)

                    # For keys not found in Redis, fetch from DynamoDB
                    keys_not_in_redis = [key for key in keys_to_get if json.dumps(key, sort_keys=True) not in redis_client.keys()]
                    print("Keys not in Redis", keys_not_in_redis)
                    if keys_not_in_redis:
                        dynamo_response_items = []
                        for key_batch in [keys_not_in_redis[i:i + batch_size] for i in range(0, len(keys_not_in_redis), batch_size)]:
                            response = dynamodb.batch_get_item(
                                RequestItems={
                                    TABLE_NAME: {
                                        'Keys': key_batch
                                    }
                                }
                            )
                            dynamo_response_items.extend(response.get('Responses', {}).get(TABLE_NAME, []))
                        dynamo_response_items = [{key: int(value) if isinstance(value, Decimal) else value for key, value in item.items()} for item in dynamo_response_items]
                        print("Data from DynamoDB", dynamo_response_items)
                        total_dynamodb_data.extend(dynamo_response_items)

                        # Set fetched data in Redis
                        set_data_in_redis(dynamo_response_items)

                return {
                    'statusCode': 200,
                    'headers': {
                        'Access-Control-Allow-Headers': '*',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                    },
                    'body': json.dumps({
                        'redis_data': total_redis_data,
                        'dynamodb_data': total_dynamodb_data
                    })
                }

            except Exception as ex:
                print(f"Error handling GET request: {ex}")
                return {
                    'statusCode': 500,
                    'body': json.dumps('An error occurred while processing the GET request.')
                }

        elif http_method == 'DELETE':
            not_found = []
            found = []
            try:
                for item in requested_data[:200]:
                    key = {'year': item['year'], 'title': item['title']}
                    
                    # Check if the item exists in DynamoDB
                    response = table.get_item(Key=key)
                    if 'Item' in response:
                        # If the item exists, delete it and add its key to the found list
                        table.delete_item(Key=key)
                        found.append(key)
                    else:
                        # If the item does not exist, add its key to the not_found list
                        not_found.append(key)
                return {
                    'statusCode': 200,
                    'headers': {
                        'Access-Control-Allow-Headers': '*',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                    },
                    'body': json.dumps({
                        'found': found,
                        'not_found': not_found
                    })
                }
                    
            except Exception as e:
                print(f"Error adding data: {e}")
                return {
                    'statusCode': 500,
                    'body': json.dumps('An error occurred: {}'.format(e))
                }

        else:
            return {
                'statusCode': 405,
                'body': json.dumps('Method not allowed')
            }
    except Exception as ex:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(ex)}')
        }


def lambda_handler(event, context):
    return process_request(event, context)
