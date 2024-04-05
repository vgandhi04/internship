import json
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('newmovie')

def lambda_handler(event, context):
    http_method = event['httpMethod']
    
    if http_method == 'POST':

        requested_data = event['body']
        
        new_data = requested_data[:200]
        insert_data = []
        
        with table.batch_writer() as batch:
        
            for item in new_data:
                # item = json.loads(json.dumps(item))
                item = json.loads(json.dumps(item), parse_float=Decimal)
                try:
                    batch.put_item(Item=item)
                except Exception as e:
                    print(f"Error while inserting for Item: {item}. Error is {e}")
                finally:
                    insert_data.append(f"{item}")
            print("insert_data ", insert_data)
        
        return {
            'statusCode': 200,
            'body': json.dumps(f"{insert_data}")
        }
    
    elif http_method == 'GET':
        
        requested_data = event['body']
        new_data = requested_data[:200]
        items_found = []
        batch_size = 100
        total_data = []
        for i in range(0, len(new_data), batch_size):
            
            batch_data = new_data[i:i + batch_size]
            
            keys_to_get = [{'year': int(item['year']), 'title': item['title']} for item in batch_data]
            
            print("keys_to_get ", keys_to_get)
            try:
                response = dynamodb.batch_get_item(
                    RequestItems={
                        'newmovie':{
                            'Keys': keys_to_get
                        }
                    }
                )
                # print("response ", response)
                items_found = response.get('Responses', {}).get('newmovie', [])
                print("items_found ", items_found)
                total_data.extend(items_found)
                print("total_data ", total_data)
            except Exception as e:
                print(f"Error while getting items. Error is {e}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(f"lenth - {len(total_data)}")
        }
              
    elif http_method == 'DELETE':
        
        requested_data = event['body']
        
        new_data = requested_data[:200]
        total_data = []
        
        batch_key = [{"year": item['year'], "title": item['title']} for item in new_data]
        
        with table.batch_writer() as batch:

            for key in batch_key:
                try:
                    batch.delete_item(Key=key)
                except Exception as e:
                    print(f"Error while deleting for Item: {key}. Error is {e}")

                total_data.append(f"{key}")

        return {    
            'statusCode': 200,
            'body': json.dumps(total_data)
        }