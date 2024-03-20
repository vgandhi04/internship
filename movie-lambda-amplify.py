import json
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = 'Movie-ihii2ahnyrgvlmolbufnjuocyu-dev'
table = dynamodb.Table(TABLE_NAME)

def handler(event, context):
    print('received event:')
    print(event)
    
    event1 = json.loads(event['body'])
    http_method = event1['httpMethod']
    requested_data = event1['body']
    print("requested_data ", requested_data)
    
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
            
                response = dynamodb.batch_get_item(
                    RequestItems={
                        TABLE_NAME:{
                            'Keys': keys_to_get
                        }
                    }
                )
                print("response ", response)
                items_found = response.get('Responses', {}).get(TABLE_NAME, [])
                print("items_found ", items_found)
                total_data.extend(items_found)
                print("total_data ", total_data)
            
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
