import json
import requests
import boto3
# from aws_requests_auth.aws_auth import AWSRequestsAuth
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth

def handler(event, context):
    print('received event:')
    print(event['body'])
    # event1 = json.loads(event['body'])
    event1 = event['body'][0]
    query = event1.get("query", "")
    year = event1.get("year", "")
    result = "".join([f"{w}*" for w in query])
    print("Q1 - ", result)
    print("Q - ", query)
    print("Y - ", year)

    # Elasticsearch endpoint
    es_endpoint = "https://search-amplify-opense-x35r0x76s3wi-ehduhegp7wtezt7xdmeb6pokha.ap-south-1.es.amazonaws.com"
    
    index = "movie"
    type_ = "_search"

    # Elasticsearch query
    es_query = {
        "query": {
            "bool": {
                "should": [
                    {
                        "wildcard": {
                            "title": result
                        }
                    },
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["title^3"],
                            "fuzziness": "10"
                        }
                    },
                    {
                        "term": {
                            "year": year
                        }
                    }
                ]
            }
        }
    }
    # Get temporary AWS credentials
    
    # client = boto3.client('sts')
    # response = client.get_session_token(
    #                 DurationSeconds=3600
    #             )
    # print("response Session - ", response)
    # aws_access_key = response['Credentials']['AccessKeyId']
    # aws_secret_access_key = response['Credentials']['SecretAccessKey']
    # aws_session_token = response['Credentials']['SessionToken']
        
    # auth = AWSRequestsAuth(aws_access_key_id=aws_access_key,
    #                         aws_secret_access_key=aws_secret_access_key,
    #                         aws_token=aws_session_token,
    #                         aws_host=es_endpoint.split('/')[2],
    #                         aws_region='ap-south-1',
    #                         aws_service='es')
    
    auth = BotoAWSRequestsAuth(
                            aws_host=es_endpoint.split('/')[2],
                            aws_region='ap-south-1',
                            aws_service='es'
                            )
    
    print("auth - ", auth)

    # Make request to Elasticsearch
    response = requests.get(f"{es_endpoint}/{index}/{type_}", json=es_query, auth=auth)
    print(f"Response: {response.status_code} - {response.reason} - {response}")
    # Check if request was successful
    if response.status_code == 200:
        # Parse response JSON
        response_json = response.json()
        print("response_json - ", response_json)
        # Extract movie names from response
        movie_names = [hit["_source"]["title"] for hit in response_json["hits"]["hits"]]

        # Return movie names
        return {
            'statusCode': 200,
            'body': json.dumps(movie_names)
        }
    else:
        # Return error message
        return {
            'statusCode': response.status_code,
            'body': json.dumps(f"Error: {response.reason}")
        }
