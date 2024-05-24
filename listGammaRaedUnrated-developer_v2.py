import json
import AppSyncHelper
from gql import gql
import threading
import os
import boto3
from chaliceHelper import app, BadRequestError, Response
from boto3.dynamodb.conditions import Key
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth #Vivek 

# Vivek START
import time

OPENSEARCH_DOMAIN_ENDPOINT = os.environ['OPENSEARCH_DOMAIN_ENDPOINT']
OPENSEARCH_PORT = 443
REGION = os.environ['REGION']  # e.g. us-west-1
CREDENTIALS = boto3.Session().get_credentials()
AWS_AUTH = AWSV4SignerAuth(CREDENTIALS, REGION)
STAGE_TABLE_NAME = os.environ['API_STRALIGN_STAGETABLE_NAME']
USERRATING_TABLE_NAME = os.environ['API_STRALIGN_USERRATINGTABLE_NAME']
print("USERRATING_TABLE_NAME - ", USERRATING_TABLE_NAME)

def get_global_opensearch_client():
    global OPENSEARCH_CLIENT
    if 'OPENSEARCH_CLIENT' not in globals():
        OPENSEARCH_CLIENT = OpenSearch(
            hosts=[f'{OPENSEARCH_DOMAIN_ENDPOINT}:{OPENSEARCH_PORT}'],
            http_auth=AWS_AUTH,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )
    return OPENSEARCH_CLIENT


def get_openserch_client_response(request, index):
    OPENSEARCH_CLIENT = get_global_opensearch_client()
    response = OPENSEARCH_CLIENT.search(
        body=request,
        index=index
    )
    return response


def get_global_dynamodb_resource():
    global DYNAMODB_RESOURCE
    if 'DYNAMODB_RESOURCE' not in globals():
        DYNAMODB_RESOURCE = boto3.resource('dynamodb', config=botocore.client.Config(max_pool_connections=1000))
    return DYNAMODB_RESOURCE


def get_global_stage_table():
    global STAGE_TABLE
    if 'STAGE_TABLE' not in globals():
        STAGE_TABLE = get_global_dynamodb_resource().Table(STAGE_TABLE_NAME)
    return STAGE_TABLE


def get_stages(organization_id, stage_details):
    stages_response = get_global_stage_table().query(
        KeyConditionExpression=Key('organizationID').eq(organization_id),
        IndexName='byOrganization',
        ProjectionExpression='id,#n,#l',
        ExpressionAttributeNames={'#n': 'name', '#l': 'level'}
    )

    print("stages_response", stages_response)

    stage_details.update({
        stage['id']: {
            'id': stage['id'], 
            'name': stage['name'], 
            'level': int(stage['level'])
        } for stage in stages_response['Items']
    })


def get_global_userrating_table():
    global USERRATING_TABLE
    if 'USERRATING_TABLE' not in globals():
        USERRATING_TABLE = get_global_dynamodb_resource().Table(USERRATING_TABLE_NAME)
    return USERRATING_TABLE

def get_userrating(organization_id, user_id):
    start = time.time()
    user_rating_data = []
    param = {
        'KeyConditionExpression': Key('organizationID').eq(organization_id) & Key('userID').eq(user_id),
        'IndexName': 'byOrganization',
        'ProjectionExpression': 'gammaID'
    }
    while True:
        stages_response = get_global_userrating_table().query(**param)
        user_rating_data.extend(stages_response.get('Items', []))
        
        if 'LastEvaluatedKey' in stages_response:
            param['ExclusiveStartKey'] = stages_response['LastEvaluatedKey']
        else:
            break
    print("get userrating time- ", time.time() - start)
    # Extracting values from the list of dictionaries
    gamma_ids = [item['gammaID'] for item in user_rating_data]
    return gamma_ids

# Vivek END

DEPARTMENT_TABLE_NAME = os.environ['API_STRALIGN_DEPARTMENTTABLE_NAME']

get_org_query = gql(
    """
        query getOrganization($id: ID!) {
            getOrganization(id: $id) {
                ratingFlags
                objectives(filter: {active: {eq: true}}) {
                    items {
                        id
                    }
                }
                
            }
        }
    """
)

def get_graphql_client():
    print("creating a new graphql client")
    gql_client = AppSyncHelper.create_graphql_client()
    return gql_client


def get_global_dynamodb_resource():
    global DYNAMODB_RESOURCE
    if 'DYNAMODB_RESOURCE' not in globals():
        DYNAMODB_RESOURCE = boto3.resource('dynamodb')
    return DYNAMODB_RESOURCE


def get_global_department_table():
    global DEPARTMENT_TABLE
    if 'DEPARTMENT_TABLE' not in globals():
        DEPARTMENT_TABLE = get_global_dynamodb_resource().Table(DEPARTMENT_TABLE_NAME)
    return DEPARTMENT_TABLE


def get_departments_by_organization(organization_id, departments_data):
    departments_response = get_global_department_table().query(
        KeyConditionExpression=Key('organizationID').eq(organization_id),
        IndexName='byOrganization',
        ProjectionExpression='id,#n',
        ExpressionAttributeNames={'#n': 'name'}
    )
    for department in departments_response['Items']:
        departments_data[department['id']] = department['name']
    return departments_data


GQL_CLIENT = get_graphql_client()


@app.route('/rate', cors=True, methods=['GET'], content_types=['application/json'])
def get_rate():
    
    # Vivek start
    START = 0
    PAGE_SIZE = 20
    # OPENSEARCH_CLIENT = get_global_opensearch_client()
    INDEX_NAME = 'gamma'
    USER_RATING_INDEX = 'userrating'
    
    
    sort_field = app.current_request.query_params.get("sort_field", "friendlyId")
    sort_direction = app.current_request.query_params.get("sort_direction", "asc")
    search = app.current_request.query_params.get("search", None)
    search = None if search == "null" else search
    filter_v = app.current_request.query_params.get('filter', "{}")
    
    
    print("filter", filter_v)
    filter_v = json.loads(filter_v)
    print("filter", filter_v)
    
    # Vivek End     
    user_id = app.current_request.query_params.get("id", None)
    organization_id = app.current_request.query_params.get("organizationID", None)
    # nextToken = app.current_request.query_params.get("nextToken", None)
    # nextToken = None if nextToken == "null" else nextToken
    if user_id is None or organization_id is None:
        raise BadRequestError("organization or user not passed")
    else:
        threads = []
        user_ratings_data = {}
        departments_data = {}
        
        # Commented by Vivek
        # threads.append(threading.Thread(target=get_user_ratings_data, args=(get_graphql_client(), user_id, user_ratings_data, )))
        # threads[-1].start()

        threads.append(threading.Thread(target=get_departments_by_organization,
                                        args=(organization_id, departments_data, )))
        threads[-1].start()
        params = {
            "userID": user_id,
            # "nextToken": None,
            "id": organization_id
        }
        organization = GQL_CLIENT.execute(get_org_query, variable_values=params).get("getOrganization", None)
        objectives = organization["objectives"]["items"]
        print("objectives - ", organization)
        rating_flags = json.loads(organization["ratingFlags"]) if organization["ratingFlags"] is not None else {} 
        disabled_levels = [key for key in rating_flags if rating_flags[key] == False]        
        
        if not any(rating_flags.values()):
            return Response(body="Rating disabled", status_code=400)
        
        # Commneted by Vivek
        # gammas_data = []
        # gammas_data, nextToken = get_enabled_level_gammas(GQL_CLIENT, organization_id, user_id, disabled_levels, gammas_data, nextToken)
        
        
        # Vivek start
        
        print("disabled_levels - ", disabled_levels)
        print("rating_flags - ", rating_flags)
        
        stage_details = {}
        threads.append(threading.Thread(target=get_stages, args=(organization_id, stage_details,)))
        threads[-1].start()
    
        # Vivek end
            
        
        for thread in threads:
            thread.join()

        # print("gammas_data", gammas_data) # Vivek
        print("user_ratings_data", user_ratings_data)
        
        # vivek start
        filters = []
        if filter_v:
            if filter_v.get('Stage'):
                stages = [stage for stage, checked in filter_v['Stage'].items() if checked]
                
                filters.append(
                    {
                        "terms": {
                            "levelID.keyword": stages
                        }
                    }
                )

            if filter_v.get('Created'):
                filters.append(
                    {
                        "range": {
                            "createdAt": {
                                "gte": filter_v['Created'][0],
                                "lte": filter_v['Created'][1]
                            }
                        }
                    }
                )
            
            if filter_v.get('Department'):
                filters.append(
                    {
                        "terms": {
                            "departments.keyword": filter_v['Department']
                        }
                    }
                )
                
        request = {
            "query": {
                "bool": {
                    "must": [{
                        "term": {
                            "organizationID.keyword": organization_id
                        }
                    }],
                    "filter": filters
                }
            },
            "_source": ["createdAt", "id", "friendlyId", "levelID", "title", "departments"],
            "from": START, 
            "size": PAGE_SIZE 
        }
        
        if disabled_levels:
            request["query"]["bool"]["must_not"] = [{
                "terms": {
                    "levelID.keyword": disabled_levels
                }
            }]

        if search:
            if search.isdigit():
                search_query = {
                        "script": {
                            "script": {
                                "source": f"doc['friendlyId'].value.toString().contains('{search}')"
                            }
                        }
                    }
                request["query"]["bool"]["must"].append(search_query)
            
            search_query = {
                "wildcard": {
                    "title.keyword": {
                        "value": "*" + search + "*" if search else "*",
                        "case_insensitive": True
                    }
                }                        
            }
                
            request["query"]["bool"]["must"].append(search_query)
    
        print("sort_field - ", sort_field)
        if sort_field == "title":
        
            request["sort"] = [{
                    f"{sort_field}.keyword": {
                        "order": sort_direction.lower()
                    }
                }]
        
        elif sort_field == "friendlyId":
            
            request["sort"] = [{
                sort_field: {
                    "order": sort_direction.lower()
                }
            }]
        
        elif sort_field == "level":
            
            request["sort"] = [{
                "_script": {
                    "type": "number",
                    "order": sort_direction.lower(),
                    "script": {
                        "lang": "painless",
                        "source": "def levelID = doc['levelID.keyword'].value; if (params.scores.containsKey(levelID)) { return params.scores[levelID]; } else { return 1000; }",
                        "params": {
                            "scores": {
                                stage: info['level'] for stage, info in stage_details.items()
                            }
                        }
                    }
                }
            }]
        
        elif sort_field == "ratingsByUser":
            user_ratings_data_sort = {}
            
            # Dynamo
            userRating_response_Dynamo = get_userrating(organization_id, user_id)
            print("userRating_response_Dynamo - ", userRating_response_Dynamo)
            
            for gamma_id in userRating_response_Dynamo:
                if gamma_id not in user_ratings_data_sort:
                    user_ratings_data_sort[gamma_id] = 1
                else:
                    user_ratings_data_sort[gamma_id] += 1
            
            print("user_ratings_data_sort - ", user_ratings_data_sort)
            # OpenSearch
            # rating_request = {
            #     "size": 0,
            #     "query": {
            #         "bool": {
            #             "must": [
            #                 {
            #                     "term": {
            #                         "organizationID.keyword": {
            #                             "value": organization_id
            #                         }
            #                     }
            #                 },
            #                 {
            #                     "term": {
            #                         "userID.keyword": {
            #                             "value": user_id
            #                         }
            #                     }
            #                 }
            #             ]
            #         }
            #     },
            #     "aggs": {
            #         "gammas": {
            #             "terms": {
            #                 "field": "gammaID.keyword",
            #                 "size": 5000
            #             }
            #         }
            #     }
            # }
            # rating_response = get_openserch_client_response(rating_request, USER_RATING_INDEX)
            # rating_response = OPENSEARCH_CLIENT.search(
            #     body=rating_request,
            #     index=USER_RATING_INDEX
            # )
            
            # print("rating_response - ", rating_response['aggregations']['gammas']['buckets'])
            # user_ratings_data_sort = {item['key']: item['doc_count'] for item in rating_response['aggregations']['gammas']['buckets']}
            # print("user_ratings_data_sort - ", user_ratings_data_sort)
            
            request["sort"] = [{
                "_script": {
                    "type": "number",
                    "order": "asc" if sort_direction.lower() == "desc" else "desc",
                    "script": {
                        "lang": "painless",
                        "source": "def gammaID = doc['id.keyword'].value; if (params.scores.containsKey(gammaID)) { return params.scores[gammaID]; } else { return 0; }",
                        "params": {
                            "scores": {id_name: rating for id_name, rating in user_ratings_data_sort.items()}
                        }
                    }
                }
            }]
        
        print("request - ", request)
        
        response = get_openserch_client_response(request, INDEX_NAME)
        # response = OPENSEARCH_CLIENT.search(
        #     body=request,
        #     index=INDEX_NAME
        # )
        print("Response - ", response)
        
        sorted_gammas = response['hits']['hits']
        
        vivek_gamma = []

        for gamma in sorted_gammas:
            level_id = gamma['_source']['levelID']
            if level_id in stage_details:
                level_info = stage_details[level_id]
                formatted_level = {
                    "level": {
                        "id": level_info['id'],
                        "name": level_info['name'],
                        "level": level_info['level']
                    }
                }
                gamma['_source'].update(formatted_level)
            
            gamma['_source']["ratingsByUser"] = user_ratings_data.get(gamma['_source']["id"], 0)
                
            existing_departments = gamma['_source']["departments"][:]
            gamma['_source']["departments"] = {
                "items": [{
                    "department": {
                        "id": department, 
                        "name": departments_data.get(department)
                    }
                } for department in existing_departments if departments_data.get(department)
                ]
            }
            
            gamma_n = {
                "id": gamma['_source']['id'],
                "friendlyId": gamma['_source']['friendlyId'],
                "title": gamma['_source']['title'],
                "level": gamma['_source']['level'],
                "createdAt": gamma['_source']['createdAt'],
                "departments": gamma['_source']['departments'],
                "ratingsByUser": gamma['_source']['ratingsByUser'],
            }
            vivek_gamma.append(gamma_n)

        print("sorted data count - ", vivek_gamma)
        
        # Vivek end
    
        payload = {
            "Organization": {
                "gammas": {
                    "items": vivek_gamma, #Vivek
                    # "nextToken": nextToken
                },
                "objectives": {"items": objectives}
            }
        }
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET'
            },
            'body': payload
        }

