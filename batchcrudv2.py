import json
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('newmovie')

def lambda_handler(event, context):
    http_method = event['httpMethod']
    
    if http_method == 'POST':
        
        data = []
        with open('moviedata.json') as f:
            data = json.load(f)
        print("data ", data[:1])
        print("Type ", type(data))
        
        new_data = data[:100]
        batch_size = 20
        insert_data = []
        
        for i in range(0, len(new_data), batch_size):
            batch_data = new_data[i:i+batch_size]
            
            with table.batch_writer() as batch:
                for item in batch_data:
                    # item = json.loads(json.dumps(item))
                    item = json.loads(json.dumps(item), parse_float=Decimal)
                    try:
                        batch.put_item(Item=item)
                    except Exception as e:
                        print(f"Error while inserting for Item: {item}. Error is {e}")
                print(f"Batch {i}-{i + batch_size - 1}: Items found {len(batch_data)}")
        return {
            'statusCode': 200,
            'body': json.dumps(f'inserted')
        }
    
    elif http_method == 'GET':
        
        data = []
        with open('moviedata.json') as f:
            data = json.load(f)
        new_data = data[:100]
        print("Newdata ", len(new_data))
        batch_size = 20
        total_data = []
        for i in range(0, len(new_data), batch_size):
            batch_data = new_data[i:i+batch_size]    
        
            keys_to_get = [{'year': item['year'], 'title': item['title']} for item in batch_data]
            
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
                
                print(f"Batch {i}-{i + batch_size - 1}: Items found {len(items_found)}")
                
                movie_return = [{'year': item['year'], 'title': item['title'], 'found': 'yes'} for item in items_found]
                # print("User return ", movie_return)
                total_data.extend(movie_return)
            except Exception as e:
                print(f"Error while getting items. Error is {e}")
            
        return {
            'statusCode': 200,
            'body': json.dumps(f"Year {len(total_data)}")
        }
              
    elif http_method == 'DELETE':
        
        response = table.scan()
        
        data = response['Items']
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            data.extend(response['Items'])
            
        new_data = data[:74]
        batch_key = [
            {"year": item['year'], "title": item['title']} for item in new_data
        ]
        print("batch key ", batch_key)
        with table.batch_writer() as batch:
            for key in batch_key:
                try:
                    batch.delete_item(Key=key)
                except Exception as e:
                    print(f"Error while deleting for Item: {key}. Error is {e}")
        
        return {    
            'statusCode': 200,
            'body': json.dumps(f'deleted')
        }