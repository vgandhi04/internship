import json
import boto3
import os
from decimal import Decimal
from boto3.dynamodb.conditions import Key
import redis

dynamodb = boto3.resource('dynamodb')
env = 'dev'
# aws_region = os.environ.get('REGION')

# Redis configuration
redis_host = "amp-re-18zzug6x6gh1h.6xkwqy.0001.aps1.cache.amazonaws.com"
redis_port = int(6379)
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)
print("redis_client ", redis_client)

if env == 'dev':
    TABLE_NAME = 'Movie-mkv4ppybrzdvndrpzlc44uxgt4-dev'
else:
    TABLE_NAME = 'MovieStage-65xuyvcblfcs5ohcxrrjeec4wu-stage'

print("TABLE_NAME ", TABLE_NAME)

table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):    
    print('received event:')
    print(event)
    print("All Redis Keys: ", redis_client.keys())
    event1 = event['body']
    print("event1 ", event1)
    print("event1 ", type(event1))
    
    
    http_method = event['httpMethod']
    requested_data = event1
    print("requested_data ", requested_data)
    def convert_to_int(obj):
        if isinstance(obj, Decimal):
            print("iiiiiiiiiiiiiii")
            return int(obj)
        return obj
        
        
    # Function to retrieve data from Redis
    def get_data_from_redis(key):
        try:
            # Use a consistent string representation of the key
            print("getkey ", key)
            print("getkey - t ", type(key))
            str_key = json.dumps(key, sort_keys=True)
            print("str_key ", str_key)
            print("str_key - t ", type(str_key))
            
            data = redis_client.get(str_key)
            print("data ", data)
            print("data type ", type(data))
            if data:
                print(f"Data found in Redis for key {key}: {data}")
                return json.loads(data)
            else:
                print(f"No data found in Redis for key {key}")
            return None
        except Exception as e:
            print(f"Error getting data from Redis: {e}")
            return None


    # Function to set data in Redis
    def set_data_in_redis(key, data):
        try:
            # Convert Decimal to int in the data
            data = json.loads(json.dumps(data, default=convert_to_int))
            # Use a consistent string representation of the key
            print(f"Key {key} data {data}")
            str_key = json.dumps(key, sort_keys=True)
            redis_client.set(json.dumps(key, sort_keys=True), json.dumps(data))
            print(f"Data set in Redis: {data}")
        except Exception as e:
            print(f"Error setting data in Redis: {e}")
    
    
    if http_method == 'POST':
        new_data = requested_data
        insert_data = []
        try:
            with table.batch_writer() as batch:
                for item in new_data:
                    # print("type1 ",type(item))
                    # item = json.loads(json.dumps(item))
                    # print("type2 ",type(item))
                    batch.put_item(Item=item)
                    insert_data.append(item)
            print("insert_data ", insert_data)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Headers': '*',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                'body': json.dumps(f'Hello from your new Amplify Python lambda! - {len(insert_data)} - inserted')
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
                print("keys_to_get ", type(keys_to_get))

                # Try to fetch data from Redis first
                for key in keys_to_get:
                    print("key ", key)
                    print("type ", type(key)) # dict
                    print("key ", json.dumps(key, sort_keys=True)) # {"title": "aT3yZf61949", "year": 19491949} 
                    print("type ", type(json.dumps(key, sort_keys=True))) # str
                    print("key ", redis_client.keys()) # list
                    print("type ", type(redis_client.keys())) # list
                    print("key ", json.dumps(key, sort_keys=True) in redis_client.keys()) # true
                    print("type ", type(json.dumps(key, sort_keys=True) in redis_client.keys())) # bool
                    
                    data_from_redis = get_data_from_redis(key)
                    print("data_from_redis ", data_from_redis)
                    if data_from_redis:
                        print("Data from Redis")
                        items_found.append(data_from_redis)

                # # For keys not found in Redis, fetch from DynamoDB
                # keys_not_in_redis = [key for key in keys_to_get if str(key) not in redis_client.keys()]
                # For keys not found in Redis, fetch from DynamoDB
                keys_not_in_redis = [key for key in keys_to_get if json.dumps(key, sort_keys=True) not in redis_client.keys()]
                print("keys_not_in_redis ", keys_not_in_redis)
                if keys_not_in_redis:
                    response = dynamodb.batch_get_item(
                        RequestItems={
                            TABLE_NAME: {
                                'Keys': keys_not_in_redis
                            }
                        }
                    )
                    print("response from dynamo", response)
                    dynamo_response_items = response.get('Responses', {}).get(TABLE_NAME, [])
                    # dynamo_response_items = [{k: int(v) if isinstance(v, Decimal) else v for k, v in item.items()} for item in dynamo_response_items]
                    items_found.extend(dynamo_response_items)
                    print("items_found ", items_found)

                    # Set fetched data in Redis
                    for item in items_found:
                        print("Set data in Redis")
                        set_data_in_redis(item, item)
                        total_data.append(item)

            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Headers': '*',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                'body': json.dumps(f'Hello from your new Amplify Python lambda! - length - {len(total_data)} - found - {items_found}')
            }

        except Exception as e:
            print(f"Error adding data: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps('An error occurred: {}'.format(e))
            }

