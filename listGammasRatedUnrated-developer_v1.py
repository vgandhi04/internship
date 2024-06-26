import json
import AppSyncHelper
from gql import gql
import threading
import os
import boto3
from chaliceHelper import app, BadRequestError, Response
from boto3.dynamodb.conditions import Key
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth #Vivek 

#some comment

# Vivek START

OPENSEARCH_DOMAIN_ENDPOINT = os.environ['OPENSEARCH_DOMAIN_ENDPOINT']
OPENSEARCH_PORT = 443
REGION = os.environ['REGION']  # e.g. us-west-1
CREDENTIALS = boto3.Session().get_credentials()
AWS_AUTH = AWSV4SignerAuth(CREDENTIALS, REGION)
STAGE_TABLE_NAME = os.environ['API_STRALIGN_STAGETABLE_NAME']


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

# Vivek END

DEPARTMENT_TABLE_NAME = os.environ['API_STRALIGN_DEPARTMENTTABLE_NAME']
# Commented by Vivek
# get_user_ratings_by_user_query = gql(
#     """
#     query userRatingsByUserIDAndGammaID($userID: ID!, $nextToken: String) {
#         userRatingsByUserIDAndGammaID(userID: $userID, nextToken: $nextToken, limit: 10000) {
#             nextToken
#             items {
#                 userRatingObjectiveId
#                 gammaID
#                 Objective {
#                     active
#                 }
#             }
#         }
#     }

#     """
# )

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

# Commented by Vivek
# get_gammas_by_org_query = gql(
#     """
#     query gammasByOrganizationID($organizationID: ID!, $userID: ID, $nextToken: String) {
#         gammasByOrganizationID(organizationID: $organizationID, nextToken:$nextToken) {
#             nextToken
#             items {
#                 createdAt
#                 id
#                 friendlyId
#                 level {
#                     id
#                     name
#                     level
#                 }
#                 title
#                 hiddenUsers(filter: {userId: {eq: $userID}}) {
#                     items {
#                         gammaId
#                         id
#                         userId
#                     }
#                 }
#                 departments

                
#             }
            
#         }
#     }
#     """
# )


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


# Commentted by Vivek
# def get_GQL_paginated(gqlClient, query, params, list_query_name, result):
#     nextToken = None
#     count = 1

#     while (nextToken != None or count < 2):
#         count += 1

#         response = gqlClient.execute(query, variable_values=params)
#         print(response)
#         result.extend(response[list_query_name]["items"])
#         nextToken = response[list_query_name].get("nextToken", None)
#         params["nextToken"] = nextToken
#         print(nextToken)
#     return result

# Commentted by Vivek
# def get_user_ratings_data(gql_client, user_id, user_ratings_data):
#     params = {
#         "userID": user_id,
#         "nextToken": None
#     }
#     user_ratings = []
#     user_ratings = get_GQL_paginated(gql_client, get_user_ratings_by_user_query, params, "userRatingsByUserIDAndGammaID", user_ratings)

#     print("user_ratings - ", user_ratings)
#     unique_user_ratings = set((item["gammaID"], item["userRatingObjectiveId"],) for item in user_ratings if item["Objective"]["active"])
#     print("unique_user_ratings - ", unique_user_ratings)
#     for combination in unique_user_ratings:
#         gamma_id, _ = combination
#         user_ratings_data[gamma_id] = user_ratings_data.get(gamma_id, 0) + 1
#     print("get_user_ratings_data - ", get_user_ratings_data)
#     return user_ratings_data


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

# Commented by Vivek
# def input_filter_string_maker(disabled_levels):
#     levels = len(disabled_levels)
#     level_input_list = [
#         f"$levelID{i}:ID" for i in range(1, levels+1)]
#     level_filter_str = [f"$levelID{i}" for i in range(1, levels+1)]
#     level_filter_list = []
#     for level in level_filter_str:
#         level_filter_list.append({"levelID": {"ne": level}})
#     level_filter_str = ','.join(
#         str(i) for i in level_filter_list).replace("'", "")
#     level_input_str = ','.join(str(i)
#                                for i in level_input_list).replace("'", "")
#     return level_input_str, level_filter_str

# Commented by Vivek
# def get_enabled_level_gammas(gql_client, organization_id, user_id,  disabled_levels, gammas_data, nextToken):
#     params = {}
#     if disabled_levels == []:
#         query = get_gammas_by_org_query
#     else:
#         input_str, filter_str = input_filter_string_maker(disabled_levels)
#         params = {
#             f"levelID{i}": disabled_levels[i-1] for i in range(1, len(disabled_levels)+1)
#         }
#         query = gql(
#             f"""
#             query gammasByOrganizationID($organizationID:ID!, $userID:ID, $nextToken:String, {input_str} ) {{
#             gammasByOrganizationID(organizationID:$organizationID, nextToken:$nextToken, filter: {{and:[{filter_str}]}}) {{
#                 nextToken
#                 items {{
#                 createdAt
#                 id
#                 friendlyId
#                 level {{
#                     id
#                     name
#                     level
#                 }}
#                 title
#                 hiddenUsers(filter: {{userId: {{eq: $userID}}}}) {{
#                     items {{
#                         gammaId
#                         id
#                         userId
#                     }}
#                 }}
#                 departments

#                 }}
#             }}
#             }}
#             """
#         )
#     params["organizationID"] = organization_id
#     params["userID"] = user_id
#     params["nextToken"] = nextToken

#     response = gql_client.execute(
#         query, variable_values=params)["gammasByOrganizationID"]
#     gammas_data = response["items"]
#     return gammas_data, response["nextToken"]


GQL_CLIENT = get_graphql_client()


@app.route('/rate', cors=True, methods=['GET'], content_types=['application/json'])
def get_rate():
    
    # Vivek start
    PAGE_SIZE = 1000
    OPENSEARCH_CLIENT = get_global_opensearch_client()
    INDEX_NAME = 'gamma'
    USERRATING_INDEX = 'userrating'
    
    sort_field = app.current_request.query_params.get("sort_field", "friendlyId")
    sort_direction = app.current_request.query_params.get("sort_direction", "asc")
    search = app.current_request.query_params.get("search", None)
    search = None if search == "null" else search
    start = 0
    # filter_v = '{"byMe":"","Ranks":{},"Stage":{"675ae877-02a1-43ae-bb5b-433062d319ff":false,"7351657c-125c-4af1-b319-fcb072da9656":true,"72b0ca62-7211-4e53-aa43-88e386b1041f":false},"Department":["86a6d3f3-6251-4b13-86eb-4c1e2047d039"]}'
    filter_v = app.current_request.query_params.get('filter', "{}")
    
    
    print("filter", filter_v)
    filter_v = json.loads(filter_v)
    print("filter", filter_v)
    
    # Vivek End     
    user_id = app.current_request.query_params.get("id", None)
    organization_id = app.current_request.query_params.get("organizationID", None)
    nextToken = app.current_request.query_params.get("nextToken", None)
    nextToken = None if nextToken == "null" else nextToken
    if user_id is None or organization_id is None:
        raise BadRequestError("organization or user not passed")
    else:
        threads = []
        user_ratings_data = {}
        departments_data = {}
        params = {
            "userID": user_id,
            "nextToken": None
        }
        # Commented by Vivek
        # threads.append(threading.Thread(target=get_user_ratings_data, args=(get_graphql_client(), user_id, user_ratings_data, )))
        # threads[-1].start()

        threads.append(threading.Thread(target=get_departments_by_organization,
                                        args=(organization_id, departments_data, )))
        threads[-1].start()

        params = {
            "id": organization_id
        }
        organization = GQL_CLIENT.execute(get_org_query, variable_values=params).get("getOrganization", None)
        objectives = organization["objectives"]["items"]
        
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
        threads.append(threading.Thread(target=get_stages,
                                    args=(organization_id, stage_details,)))
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
            "from": start, 
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
            rating_request = {
                "size": 0,
                "query": {
                    "bool": {
                        "must": [
                            {
                                "term": {
                                    "organizationID.keyword": {
                                        "value": organization_id
                                    }
                                }
                            },
                            {
                                "term": {
                                    "userID.keyword": {
                                        "value": user_id
                                    }
                                }
                            }
                        ]
                    }
                },
                 "aggs": {
                    "gammas": {
                        "terms": {
                            "field": "gammaID.keyword",
                            "size": 5000
                        }
                    }
                }
            }
            
            rating_response = OPENSEARCH_CLIENT.search(
                body=rating_request,
                index=USERRATING_INDEX
            )
            
            # print("rating_response - ", rating_response['aggregations']['gammas']['buckets'])
            user_ratings_data_sort = {item['key']: item['doc_count'] for item in rating_response['aggregations']['gammas']['buckets']}
            print("user_ratings_data_sort - ", user_ratings_data_sort)
            
            request["sort"] = [{
                "_script": {
                    "type": "number",
                    "order": "asc" if sort_direction.lower() == "desc" else "desc",
                    "script": {
                        "lang": "painless",
                        "source": "def gammeID = doc['id.keyword'].value; if (params.scores.containsKey(gammeID)) { return params.scores[gammeID]; } else { return 0; }",
                        "params": {
                            "scores": {id_name: rating for id_name, rating in user_ratings_data_sort.items()}
                        }
                    }
                }
            }]
        
        print("request - ", request)
        
        response = OPENSEARCH_CLIENT.search(
            body=request,
            index=INDEX_NAME
        )
        print("Response - ", response)
        
        sorted_gammas = response['hits']['hits']
        # print("sorted data count - ", sorted_gammas)
        print("stage details - ", stage_details)
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
            
            gamma['_source']["ratingsByUser"] = user_ratings_data_sort.get(gamma['_source']["id"], 0)
                
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

