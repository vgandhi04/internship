import json
import boto3


'''
post
{
  "httpMethod": "POST",
  "body": {
	  "name": "John",
	  "age":30,
	  "role":"Developer"
	}
}
get
{
  "httpMethod": "GET",
 "body": {
	  "name": "John"
	}
}
'''



dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('person')

def lambda_handler(event, context):
    http_method = event['httpMethod']
    
    if http_method == 'POST':
        
        body = event['body']
        
        name = body['name']
        age = body['age']
        role = body['role']
        
        response = table.put_item(
            Item = {
                'name': name,
                'age': age,
                'role': role
            }
        )
        print("response", response)
        
        return {
            'statusCode': 200,
            'body': json.dumps(f'name is {name}, age is {age}, role is {role}')
        }
    elif http_method == 'GET':
        body = event['body']
        name = body['name']
        response = table.get_item(
            Key = {
                'name': name
            }   
        )
        print("Response ", response)
        item = response['Item']
        print("item ", item)
        return {
            'statusCode': 200,
            'body': json.dumps(f"Person name is {item['name']}  age is {item['age']} Role is {item['role']}")
        }
        
    elif http_method == 'DELETE':
        body = event['body']
        name = body['name']
        response = table.delete_item(
            Key={
                'name': name
            }
        )
        return {
            'statusCode': 200,
            'body': json.dumps('Item deleted')
        }