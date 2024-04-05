import json
import boto3
import os
from decimal import Decimal
from boto3.dynamodb.conditions import Key
import redis

env = os.environ.get('ENV')
aws_region = os.environ.get('REGION')

# DynamoDB configuration
dynamodb_client = boto3.client('dynamodb')
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('API_TABLE_NAME')
table = dynamodb.Table(TABLE_NAME)

# Redis configuration
redis_host = os.environ.get('Redis_Endpoint')
redis_port = int(6379)
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)
print("redis_client_keys ", redis_client.keys())

# Constants for Redis sorted set
RANKING_KEY = "ranking"

# Get data from Redis without Raning
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


# Set data into Redis without ranking
def set_data_in_redis(data_list):
    try:
        pipeline = redis_client.pipeline()
        for data in data_list:
            pipeline.set(json.dumps(data, sort_keys=True), json.dumps(data))
        pipeline.execute()
        print("Data set in Redis")
    except Exception as ex:
        print(f"Error setting data in Redis: {ex}")


# Set data into Redis sorted list with rankings
def set_data_sort(data_list):
    try:
        # Sort data list based on the year
        sorted_data = sorted(data_list, key=lambda x: x['year'])
        print("sorted_data ", sorted_data)
        # Store data in Redis and assign rankings
        for i, data in enumerate(sorted_data):
            # Assign ranking based on sorted order
            ranking = i + 1  # Start ranking from 1
            print(f"data -- {data} -- rank -- {ranking}")
            # Store data in Redis list with ranking as key
            redis_client.zadd(RANKING_KEY, {json.dumps(data): ranking})
            print("redis_client_keys in sorted fun ", redis_client.keys())
        print("Data set in Redis")
    except Exception as ex:
        print(f"Error setting data in Redis: {ex}")


# Updated function to get data from Redis sorted list
def get_data_from_redis_sorted_list(keys):
    try:
        data = []
        in_redis = []
        not_in_redis = []
        print("Sorted Set Count ", redis_client.zcard(RANKING_KEY))
        
        for key in keys:
            rank = redis_client.zrank(RANKING_KEY, json.dumps(key))
            print("rank ", rank)
            if rank is not None:
                data.append(rank)    
                in_redis.append(key)
            else:
                not_in_redis.append(key)

        print("sorted_data in get ", data)
        print("data_list_get ", in_redis)
        print("data_list_didnt get ", not_in_redis)
        return in_redis, not_in_redis
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
            for i in range(0, len(requested_data), batch_size):
                batch_data = requested_data[i:i + batch_size]
                keys_to_get = [{'year': int(item['year']), 'title': item['title']} for item in batch_data]

                # Try to fetch data from Redis first
                data_from_redis = get_data_from_redis(keys_to_get)
                print("Data from Redis", data_from_redis)
                # If data is not found in Redis, add into list
                total_redis_data.extend(data_from_redis)
                print("redis_client_before ", redis_client)
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
                    print("redis_client_after ", redis_client)
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
            
     # GET Method
    
    # GET1 Method for ranking data from redis
    elif http_method == 'GET1':
        total_redis_data = []
        total_dynamodb_data = []
        batch_size = 100
        try:
            # Batch operation to get the data from dynamodb and redis
            print("redis_client_keys_before_get ", redis_client.keys())
            for i in range(0, len(requested_data), batch_size):
                batch_data = requested_data[i:i + batch_size]
                keys_to_get = [{'year': int(item['year']), 'title': item['title']} for item in batch_data]

                # Try to fetch data from Redis first
                data_from_redis, keys_not_in_redis = get_data_from_redis_sorted_list(keys_to_get)
                print("Data from Redis", data_from_redis)
                # If data is found in Redis, add into list
                total_redis_data.extend(data_from_redis)

                # For keys not found in Redis, fetch from DynamoDB
                # keys_not_in_redis = [key for key in keys_to_get if json.dumps(key, sort_keys=True) not in redis_client.keys()]
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
                    # Data found from DynamoDB
                    total_dynamodb_data.extend(dynamo_response_items)

                    # Set fetched data in Redis
                    set_data_sort(dynamo_response_items)
                    print("redis_client_keys_after_get ", redis_client.keys())
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

    else:
        return {
            'statusCode': 405,
            'body': json.dumps('Method not allowed')
        }