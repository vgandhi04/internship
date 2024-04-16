import json
import requests

def handler(event, context):
    # Extract query and year from the event
    query = event.get("query", "")
    year = event.get("year", "")

    # Elasticsearch endpoint
    es_endpoint = "your_elasticsearch_endpoint_here"
    
    # Elasticsearch index and type
    index = "movie"
    type_ = "_search"
    
    # Elasticsearch query
    es_query = {
        "query": {
            "bool": {
                "should": [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": [
                                "title^3"
                            ],
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
    
    # Convert query to JSON
    es_query_json = json.dumps(es_query)
    
    # Make request to Elasticsearch
    response = requests.get(f"{es_endpoint}/{index}/{type_}", json=es_query_json)
    
    # Check if request was successful
    if response.status_code == 200:
        # Parse response JSON
        response_json = response.json()
        
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
            'body': json.dumps(f"Error: {response.text}")
        }
