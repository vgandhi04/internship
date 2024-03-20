import json
import boto3
import os
from decimal import Decimal
from boto3.dynamodb.conditions import Key
import redis


dynamodb = boto3.resource('dynamodb')
env = os.environ.get('ENV')
aws_region = os.environ.get('REGION')

# Redis configuration
redis_host = "amp-my-7kn4uaxblwzd.6xkwqy.0001.aps1.cache.amazonaws.com"
redis_port = int(6379)
print("redis_port ", type(redis_port))

try:
    redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)
    response = redis_client.ping()
    if response:
        print("Redis server is reachable.")
    else:
        print("Unable to ping Redis server.")
except Exception as e:
    print(f"Error connecting to Redis: {e}")

print("redis_client ", redis_client)

if env == 'dev':
    TABLE_NAME = 'Movie-mkv4ppybrzdvndrpzlc44uxgt4-dev'
else:
    TABLE_NAME = 'MovieStage-65xuyvcblfcs5ohcxrrjeec4wu-stage'

print("TABLE_NAME ", TABLE_NAME)

table = dynamodb.Table(TABLE_NAME)

def handler(event, context):
    print('received event:')
    print(event)
    print(type(event))
    
    event1 = json.loads(event['body'])
    # event1 = event['body'] # For test data
    http_method = event1['httpMethod']
    requested_data = event1['body']
    print("requested_data ", requested_data)

    # Function to retrieve data from Redis
    def get_data_from_redis(key):
        print("key ", key)
        print(f"Fetching data from Redis for key: {key}")
        data = redis_client.get(key)
        print("data ", data)
        if data:
            print(f"Data found in Redis: {data}")
            return json.loads(data)
        return None

    # Function to set data in Redis
    def set_data_in_redis(key, data):
        print(f"Setting data in Redis for key: {key}")
        redis_client.set(key, json.dumps(data))
        print(f"Data set in Redis: {data}")
        

    if http_method == 'POST':
        new_data = requested_data
        insert_data = []
        try:
            with table.batch_writer() as batch:
            
                for item in new_data:
                    # item = json.loads(json.dumps(item))
                    item = json.loads(json.dumps(item), parse_float=Decimal)
                    print("item ", item)
                    
                    batch.put_item(Item=item)
                    insert_data.append(f"{item}")
            print("insert_data ", insert_data)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Headers': '*',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                'body': json.dumps(f'Hello from your new Amplify Python lambda! - {len(insert_data)} - insertrd')
            }
        except Exception as e:
            print(f"Error adding data: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps('An error occurred: {}'.format(e))
            }

    elif http_method == 'GET':
        new_data = requested_data[:200]
        items_found = []
        batch_size = 100
        total_data = []

        try:
            for i in range(0, len(new_data), batch_size):
                batch_data = new_data[i:i + batch_size]
                keys_to_get = [{'year': int(item['year']), 'title': item['title']} for item in batch_data]
                print("keys_to_get ", keys_to_get)

                # Try to fetch data from Redis first
                for key in keys_to_get:
                    data_from_redis = get_data_from_redis(str(key))
                    print("data_from_redis ", data_from_redis)
                    if data_from_redis:
                        items_found.append(data_from_redis)
                    print("items_found ", items_found)

                # For keys not found in Redis, fetch from DynamoDB
                keys_not_in_redis = [key for key in keys_to_get if str(key) not in redis_client.keys()]
                if keys_not_in_redis:
                    response = dynamodb.batch_get_item(
                        RequestItems={
                            TABLE_NAME: {
                                'Keys': keys_not_in_redis
                            }
                        }
                    )
                    print("response ", response)
                    items_found.extend(response.get('Responses', {}).get(TABLE_NAME, []))
                    print("items_found ", items_found)

                    # Set fetched data in Redis
                    for item in items_found:
                        set_data_in_redis(str({'year': item['year'], 'title': item['title']}), item)

            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Headers': '*',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                'body': json.dumps(f'Hello from your new Amplify Python lambda! - lenth - {len(total_data)} - found')
            }

        except Exception as e:
            print(f"Error adding data: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps('An error occurred: {}'.format(e))
            }

    elif http_method == 'DELETE':
        new_data = requested_data[:200]
        total_data = []
        try:
            batch_key = [{"year": item['year'], "title": item['title']} for item in new_data]
            
            with table.batch_writer() as batch:

                for key in batch_key:
                    batch.delete_item(Key=key)
                    total_data.append(f"{key}")
            
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Headers': '*',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                'body': json.dumps(f'Hello from your new Amplify Python lambda! - {total_data} - deleted')
            }
                
        except Exception as e:
            print(f"Error adding data: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps('An error occurred: {}'.format(e))
            }    