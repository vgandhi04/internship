import json
import boto3
import os
from decimal import Decimal
from boto3.dynamodb.conditions import Key
import redis

# DynamoDB configuration
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('API_TABLE_NAME')
table = dynamodb.Table(TABLE_NAME)
dynamodb_client = boto3.client('dynamodb')
env = os.environ.get('ENV')
aws_region = os.environ.get('REGION')

# Redis configuration
redis_host = os.environ.get('REDIS_ENDPOINT')
redis_port = int(6379)
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)
print("redis_client_keys ", redis_client.keys())

# Constants for Redis sorted set
RANKING_KEY = "ranking"

# Get data from Redis
def get_data_from_redis(keys):
    try:
        pipeline = redis_client.pipeline()
        for key in keys:
            pipeline.get(json.dumps(key, sort_keys=True))
        data = pipeline.execute()
        return [json.loads(item) if item else None for item in data]
    except Exception as ex:
        print(f"Error getting data from Redis: {ex}")
        # return [None] * len(keys)


# Set data into Redis sorted list with rankings
def set_data_in_redis(data_list):
    try:
        # Sort data list based on the year
        sorted_data = sorted(data_list, key=lambda x: x['year'])
        # Store data in Redis and assign rankings
        for i, data in enumerate(sorted_data):
            # Assign ranking based on sorted order
            ranking = i + 1  # Start ranking from 1
            # Store data in Redis list with ranking as key
            redis_client.lpush(f'{RANKING_KEY}:{ranking}', json.dumps(data))
        print("Data set in Redis")
    except Exception as ex:
        print(f"Error setting data in Redis: {ex}")


# Get data from Redis sorted list
def get_data_from_redis_sorted_list():
    try:
        # Get data from each key in Redis sorted list and concatenate
        data = []
        for key in redis_client.keys(f'{RANKING_KEY}:*'):
            data.extend(redis_client.lrange(key, 0, -1))
        return [json.loads(item) for item in data]
    except Exception as ex:
        print(f"Error getting data from Redis sorted list: {ex}")
        return None
    

# Lambda handler
def handler(event, context):    
    print('received event:')
    print(event)
    
    event1 = json.loads(event['body'])
    http_method = event1['httpMethod']
    requested_data = event1['body']
    
    # POST Method        
    if http_method == 'POST':
        inserted_items = []
        try:
            # Batch opration to store the data into dynamodb
            with table.batch_writer() as batch:
                for item in requested_data:
                    item = {key: int(value) if isinstance(value, Decimal) else value for key, value in item.items()}
                    batch.put_item(Item=item)
                    inserted_items.append(item)
            print("inserted_items ", inserted_items)
            
            return {
                'statusCode': 200,
                'body': json.dumps(f'Successfully inserted {len(inserted_items)} items')
            }
        except Exception as e:
            print(f"Error adding data: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps('An error occurred: {}'.format(e))
            }

    # GET Method
    elif http_method == 'GET':
        total_redis_data = []
        total_dynamodb_data = []
        batch_size = 100
        try:
            # Batch opration to get the data from dynamodb and redis
            print("redis_client_keys_before_get ", redis_client.keys())
            for i in range(0, len(requested_data), batch_size):
                batch_data = requested_data[i:i + batch_size]
                keys_to_get = [{'year': int(item['year']), 'title': item['title']} for item in batch_data]

                # Try to fetch data from Redis first
                data_from_redis = get_data_from_redis(keys_to_get)
                print("Data from Redis", data_from_redis)
                # If data is not found in Redis, add into list
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
                    # data found from dynamo
                    total_dynamodb_data.extend(dynamo_response_items)

                    # Set fetched data in Redis
                    set_data_in_redis(dynamo_response_items)
            print("redis_client_keys_after_get ", redis_client.keys())
            # Call the function to get data sorted by ranking from Redis
            sorted_data = get_data_from_redis_sorted_by_ranking()

            # Print the data and their rankings
            print("Data sorted by ranking with rankings in Redis:")
            for item, ranking in sorted_data:
                print(f"Ranking: {ranking}, Data: {item}")
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

    # Delete Method
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
                    # Also remove from Redis
                    redis_client.delete(json.dumps(key, sort_keys=True))
                    redis_client.zrem(RANKING_KEY, json.dumps(key))
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