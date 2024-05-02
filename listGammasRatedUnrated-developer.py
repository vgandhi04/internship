import json
import AppSyncHelper
from gql import gql
import threading
import os
import boto3
from chaliceHelper import app, BadRequestError, Response
from boto3.dynamodb.conditions import Key


#some comment

DEPARTMENT_TABLE_NAME = os.environ['API_STRALIGN_DEPARTMENTTABLE_NAME']
get_user_ratings_by_user_query = gql(
    """
    query userRatingsByUserIDAndGammaID($userID: ID!, $nextToken: String) {
        userRatingsByUserIDAndGammaID(userID: $userID, nextToken: $nextToken, limit: 10000) {
            nextToken
            items {
                userRatingObjectiveId
                gammaID
                Objective {
                    active
                }
            }
        }
    }

    """
)
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

get_gammas_by_org_query = gql(
    """
    query gammasByOrganizationID($organizationID: ID!, $userID: ID, $nextToken: String) {
        gammasByOrganizationID(organizationID: $organizationID, nextToken:$nextToken) {
            nextToken
            items {
                createdAt
                id
                friendlyId
                level {
                    id
                    name
                    level
                }
                title
                hiddenUsers(filter: {userId: {eq: $userID}}) {
                    items {
                        gammaId
                        id
                        userId
                    }
                }
                departments

                
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


def get_GQL_paginated(gqlClient, query, params, list_query_name, result):
    nextToken = None
    count = 1

    while (nextToken != None or count < 2):
        count += 1

        response = gqlClient.execute(query, variable_values=params)
        print(response)
        result.extend(response[list_query_name]["items"])
        nextToken = response[list_query_name].get("nextToken", None)
        params["nextToken"] = nextToken
        print(nextToken)
    return result


def get_user_ratings_data(gql_client, user_id, user_ratings_data):
    params = {
        "userID": user_id,
        "nextToken": None
    }
    user_ratings = []
    user_ratings = get_GQL_paginated(
        gql_client, get_user_ratings_by_user_query, params, "userRatingsByUserIDAndGammaID", user_ratings)

    unique_user_ratings = set(
        (item["gammaID"], item["userRatingObjectiveId"],) for item in user_ratings if item["Objective"]["active"])
    for combination in unique_user_ratings:
        gamma_id, _ = combination
        user_ratings_data[gamma_id] = user_ratings_data.get(gamma_id, 0) + 1
    return user_ratings_data


def get_departments_by_organization(organization_id, departments_data):
    departments_response = get_global_department_table().query(
        KeyConditionExpression=Key(
            'organizationID').eq(organization_id),
        IndexName='byOrganization',
        ProjectionExpression='id,#n',
        ExpressionAttributeNames={'#n': 'name'}
    )
    for department in departments_response['Items']:
        departments_data[department['id']] = department['name']
    return departments_data


def input_filter_string_maker(disabled_levels):
    levels = len(disabled_levels)
    level_input_list = [
        f"$levelID{i}:ID" for i in range(1, levels+1)]
    level_filter_str = [f"$levelID{i}" for i in range(1, levels+1)]
    level_filter_list = []
    for level in level_filter_str:
        level_filter_list.append({"levelID": {"ne": level}})
    level_filter_str = ','.join(
        str(i) for i in level_filter_list).replace("'", "")
    level_input_str = ','.join(str(i)
                               for i in level_input_list).replace("'", "")
    return level_input_str, level_filter_str


def get_enabled_level_gammas(gql_client, organization_id, user_id,  disabled_levels, gammas_data, nextToken):
    params = {}
    if disabled_levels == []:
        query = get_gammas_by_org_query
    else:
        input_str, filter_str = input_filter_string_maker(disabled_levels)
        params = {
            f"levelID{i}": disabled_levels[i-1] for i in range(1, len(disabled_levels)+1)
        }
        query = gql(
            f"""
            query gammasByOrganizationID($organizationID:ID!, $userID:ID, $nextToken:String, {input_str} ) {{
            gammasByOrganizationID(organizationID:$organizationID, nextToken:$nextToken, filter: {{and:[{filter_str}]}}) {{
                nextToken
                items {{
                createdAt
                id
                friendlyId
                level {{
                    id
                    name
                    level
                }}
                title
                hiddenUsers(filter: {{userId: {{eq: $userID}}}}) {{
                    items {{
                        gammaId
                        id
                        userId
                    }}
                }}
                departments

                }}
            }}
            }}
            """
        )
    params["organizationID"] = organization_id
    params["userID"] = user_id
    params["nextToken"] = nextToken

    response = gql_client.execute(
        query, variable_values=params)["gammasByOrganizationID"]
    gammas_data = response["items"]
    return gammas_data, response["nextToken"]


GQL_CLIENT = get_graphql_client()


@app.route('/rate', cors=True, methods=['GET'], content_types=['application/json'])
def get_rate():
    user_id = app.current_request.query_params.get("id", None)
    organization_id = app.current_request.query_params.get(
        "organizationID", None)
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
        threads.append(threading.Thread(target=get_user_ratings_data,
                                        args=(get_graphql_client(), user_id, user_ratings_data, )))
        threads[-1].start()

        threads.append(threading.Thread(target=get_departments_by_organization,
                                        args=(organization_id, departments_data, )))
        threads[-1].start()

        params = {
            "id": organization_id
        }
        organization = GQL_CLIENT.execute(
            get_org_query, variable_values=params).get("getOrganization", None)
        objectives = organization["objectives"]["items"]
        rating_flags = json.loads(
            organization["ratingFlags"]) if organization["ratingFlags"] is not None else {}
        disabled_levels = [
            key for key in rating_flags if rating_flags[key] == False]
        if not any(rating_flags.values()):
            return Response(body="Rating disabled", status_code=400)
        gammas_data = []
        gammas_data, nextToken = get_enabled_level_gammas(
            GQL_CLIENT, organization_id, user_id, disabled_levels, gammas_data, nextToken)
        for thread in threads:
            thread.join()

        print("gammas_data", gammas_data)
        print("user_ratings_data", user_ratings_data)

        for gamma in gammas_data:
            existing_departments = gamma["departments"][:]
            gamma["ratingsByUser"] = user_ratings_data.get(gamma["id"], 0)
            gamma["departments"] = {"items": [{"department": {
                "id": department, "name": departments_data[department]}} for department in existing_departments if departments_data.get(department)]}
        payload = {
            "Organization": {
                "gammas": {"items": gammas_data,
                           "nextToken": nextToken},
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
