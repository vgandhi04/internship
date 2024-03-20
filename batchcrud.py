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
        
        new_data = data[:10]
        
        with table.batch_writer() as batch:
            for item in new_data:
                item = json.loads(json.dumps(item), parse_float=Decimal)
                try:
                    batch.put_item(Item=item)
                except Exception as e:
                    print(f"Error while inserting for Item: {item}. Error is {e}")
        return {
            'statusCode': 200,
            'body': json.dumps(f'inserted')
        }
    
    
    
    
    elif http_method == 'GET':
        # response = table.scan()
        
        # data = response['Items']
        # while 'LastEvaluatedKey' in response:
        #     response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        #     data.extend(response['Items'])

        # # print("Data ", data)
        # return {
        #     'statusCode': 200,
        #     'body': json.dumps(f"Len {len(data)}")
        # }
        data = []
        with open('moviedata.json') as f:
            data = json.load(f)
        new_data = data[:5]
        print("Newdadta ", new_data)
        inserted_data = {}
        retu = []
        for item in new_data:
            item = json.loads(json.dumps(item), parse_float=Decimal)
            # print("item ", item)
            try:
                response =  table.query(KeyConditionExpression=Key('year').eq(item['year']) & Key('title').eq(item['title']))
                print("response__res ", response['Items'])
                if response['Items']:
                    inserted_data = {
                        'year': item['year'],
                        'title': item['title'],
                        'found': 'Yes'
                    }
                else:
                    inserted_data = {
                        'year': item['year'],
                        'title': item['title'],
                        'found': 'No'
                    }
                retu.append(inserted_data)
                print("return ", retu)
            except Exception as e:
                print(f"Error while getting for Item: {item}. Error is {e}")
            
        return {
            'statusCode': 200,
            'body': json.dumps(f"Len {retu}")
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