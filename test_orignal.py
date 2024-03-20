import os
import boto3
import time
import json
import threading
from datetime import datetime
import AppSyncHelper
from gql import gql
import DynamoDBHelper
from chaliceHelper import app, BadRequestError, Response
import copy


gqlClient = AppSyncHelper.create_graphql_client()
dynamodb_client = boto3.resource('dynamodb')
lambda_client = boto3.client('lambda')
FUNCTION_SCHEDULEDCOMPARISONQUEUER_NAME = os.environ["FUNCTION_SCHEDULEDCOMPARISONQUEUER_NAME"]

# Defining varilable for tree structure of uservote
total_levels = 5
total_nodes = (2 ** total_levels) - 1


def generate_iso8601_string():
    # Get the current UTC time
    now = datetime.utcnow()

    # Format the datetime object to ISO 8601 string
    iso8601_string = now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

    return iso8601_string


def createComparisonStatus(user_id):
    mutation = gql(
        """
            mutation createComparisonCreatorStatus($userID: ID!, $expiry: AWSTimestamp! ) {
                createComparisonCreatorStatus(input: {userID:$userID, expiry: $expiry}) {
                    userID
                }
            }
        """
    )
    params = {
        "userID": user_id,
        "expiry": int(time.time()) + 60
    }

    gql_response = gqlClient.execute(mutation, variable_values=params)
    # print("gql response", gql_response)


def deleteComparisonStatus(user_id):
    mutation = gql(
        """
            mutation deleteComparisonCreatorStatus($userID: ID!) {
                deleteComparisonCreatorStatus(input: {userID:$userID}) {
                    userID
                }
            }
        """
    )
    params = {
        "userID": user_id
    }

    gql_response = gqlClient.execute(mutation, variable_values=params)
    # print("gql response", gql_response)


# Making binary tree from the data given in form of array.
def structer_data_in_tree(data, structured_arr):

    # finding the index in array suitable as left child
    def get_left_index_id(arr, gamma_id, objective_id):
        left_id_index = None
        for i in range(len(arr)):
            if (gamma_id == arr[i]['gamma1']['id'] or gamma_id == arr[i]['gamma2']['id']) and objective_id == arr[i]['objective']['id']:
                left_id_index = i
                return left_id_index

        for i in range(len(arr)):
            if (gamma_id == arr[i]['gamma1']['id'] or gamma_id == arr[i]['gamma2']['id']):
                left_id_index = i
                return left_id_index

        return left_id_index

    # finding the index in array suitable as right child
    def get_right_index_id(arr, gamma_id, objective_id):
        right_id_index = None
        for i in range(len(arr)):
            if (gamma_id == arr[i]['gamma1']['id'] or gamma_id == arr[i]['gamma2']['id']) and objective_id == arr[i]['objective']['id']:
                right_id_index = i
                return right_id_index

        for i in range(len(arr)):
            if (gamma_id == arr[i]['gamma1']['id'] or gamma_id == arr[i]['gamma2']['id']):
                right_id_index = i
                return right_id_index

        return right_id_index

    i = 0
    while len(structured_arr) > i:
        try:
            # Get left node object
            left_id_index = None
            right_id_index = None

            # Filling Left Child
            if (2*i)+1 < total_nodes:

                if structured_arr[i] and structured_arr[i]['gamma1']:
                    left_id_index = get_left_index_id(
                        data, structured_arr[i]['gamma1']['id'], structured_arr[i]['objective']['id'])

                # is left child exist?
                if left_id_index != None:
                    # Swap the gammas if not match as per expected
                    if structured_arr[i]['gamma1']['id'] != data[left_id_index]['gamma1']['id'] and structured_arr[i]['gamma1']['id'] == data[left_id_index]['gamma2']['id']:
                        data[left_id_index]['gamma1'], data[left_id_index]['gamma2'] = data[left_id_index]['gamma2'], data[left_id_index]['gamma1']

                    structured_arr[(2*i)+1] = data[left_id_index]

                    # Removing element as it taken in structured_arr array
                    data.pop(left_id_index)
                # left child not exist i.e assing None value
                else:
                    structured_arr[(2*i)+1] = None

            # Filling Right child
            if (2*i)+2 < total_nodes:
                # Get right node object
                if structured_arr[i] and structured_arr[i]['gamma1']:
                    right_id_index = get_right_index_id(
                        data, structured_arr[i]['gamma2']['id'], structured_arr[i]['objective']['id'])

                # is right child exist?
                if right_id_index != None:

                    # Swap the gammas if not match as per expected
                    if structured_arr[i]['gamma2']['id'] != data[right_id_index]['gamma2']['id'] and structured_arr[i]['gamma2']['id'] == data[right_id_index]['gamma1']['id']:
                        data[right_id_index]['gamma1'], data[right_id_index]['gamma2'] = data[right_id_index]['gamma2'], data[right_id_index]['gamma1']

                    structured_arr[(2*i)+2] = data[right_id_index]

                    # Removing element as it taken in structured_arr array
                    data.pop(right_id_index)

                # right child not exist i.e assing None value
                else:
                    structured_arr[(2*i)+2] = None

        except Exception as e:
            print("Error", str(e))
            break

        finally:
            i += 1
    return structured_arr


# Get Full binary tree for given array.
def get_full_tree_arr(main_arr, start_with_gamma_id_1=None, start_with_gamma_id_2=None, objective_id=None):
    final_arr = None

    # Checking the max full binary tree, for every element in array forming the Binary tree.
    for i in range(len(main_arr)):
        # Defining empty array
        structured_arr = [{} for _ in range((total_nodes))]

        # Assigning Root Node
        structured_arr[0] = (main_arr[i])

        if start_with_gamma_id_1:
            if structured_arr[0]['gamma1']['id'] != start_with_gamma_id_1 or structured_arr[0]['gamma2']['id'] == start_with_gamma_id_1:
                structured_arr[0]['gamma1'], structured_arr[0]['gamma2'] = structured_arr[0]['gamma2'], structured_arr[0]['gamma1']
        elif start_with_gamma_id_2:
            if structured_arr[0]['gamma2']['id'] != start_with_gamma_id_2 or structured_arr[0]['gamma1']['id'] == start_with_gamma_id_2:
                structured_arr[0]['gamma1'], structured_arr[0]['gamma2'] = structured_arr[0]['gamma2'], structured_arr[0]['gamma1']

        temp_arr = structer_data_in_tree(
            main_arr[:i] + main_arr[i+1:], copy.deepcopy(structured_arr))

        gammaIdGiven = True if start_with_gamma_id_1 or start_with_gamma_id_2 else False

        if not final_arr:
            final_arr = copy.deepcopy(temp_arr)

        # updating the final tree with Specific Gamma Id positions
        elif start_with_gamma_id_1:
            if final_arr[0]['gamma1']['id'] != start_with_gamma_id_1 and temp_arr[0]['gamma1']['id'] == start_with_gamma_id_1:
                # if final_arr[0]['objective']['id'] != objective_id or temp_arr[0]['objective']['id'] == objective_id:
                final_arr = temp_arr
                gammaIdGiven = False

        elif start_with_gamma_id_2:
            if final_arr[0]['gamma2']['id'] != start_with_gamma_id_2 and temp_arr[0]['gamma2']['id'] == start_with_gamma_id_2:
                # if final_arr[0]['objective']['id'] != objective_id or temp_arr[0]['objective']['id'] == objective_id:
                final_arr = temp_arr
                gammaIdGiven = False

        if final_arr.count(None) == 0 and not gammaIdGiven:
            break
        # Calculating the minimum None value in array. Minimum None value means the near to full binary tree.
        if final_arr.count(None) > temp_arr.count(None):
            if start_with_gamma_id_1:
                if temp_arr[0]['gamma1']['id'] == start_with_gamma_id_1:
                    # if final_arr[0]['objective']['id'] != objective_id or temp_arr[0]['objective']['id'] == objective_id:
                    final_arr = copy.deepcopy(temp_arr)
            elif start_with_gamma_id_2:
                if temp_arr[0]['gamma2']['id'] == start_with_gamma_id_2:
                    # if final_arr[0]['objective']['id'] != objective_id or temp_arr[0]['objective']['id'] == objective_id:
                    final_arr = copy.deepcopy(temp_arr)
            else:
                final_arr = copy.deepcopy(temp_arr)

    return final_arr


def get_new_comparison(userId, organization_id, limit=2, gamma_id=None, objective_id=None, nextToken=None):
    filter_str = "{}"
    input_str = ""
    if objective_id is not None and gamma_id is not None:
        input_str = ",$objectiveID:ID, $gamma1ID: ID, $gamma2ID:ID"
        filter_str = "{objectiveID: {eq: $objectiveID}, or: [{gamma1ID: {eq: $gamma1ID}}, {gamma2ID: {eq:$gamma2ID}}]}"
    query = gql(
        f"""
            query comparisonsByUserID($userID: ID!, $nextToken: String, $limit:Int {input_str}) {{
                comparisonsByUserID(userID: $userID, nextToken: $nextToken, sortDirection: ASC, limit: $limit, filter: {filter_str}) {{
                nextToken
                items {{
                    id
                    gamma1 {{
                        id
                        title
                        description
                        level {{
                            id
                            level
                            name
                        }}
                        createdAt
                        updatedAt
                    }}
                    gamma2 {{
                        id
                        title
                        description
                        level {{
                            id
                            level
                            name
                        }}
                        createdAt
                        updatedAt
                    }}
                    objective {{
                        id
                        name
                        description
                    }}
                }}
            }}
            }}
        """
    )
    print(query)
    params = {
        "userID": userId,
        "limit": 200,
        "objectiveID": objective_id,
        "gamma1ID": gamma_id,
        "gamma2ID": gamma_id,
        "nextToken": nextToken
    }
    gql_response = gqlClient.execute(query, variable_values=params)
    print("gql response", gql_response)

    gql_response["comparisonsByUserID"]["items"] = [
        item for item in gql_response["comparisonsByUserID"]["items"] if item['gamma1'] and item['gamma2']]
    return gql_response["comparisonsByUserID"]["items"]


def check_comparison_flags(organization_id, comparison_flags):
    comparisonFlags = DynamoDBHelper.get(
        dynamodb_client, os.environ["API_STRALIGN_ORGANIZATIONTABLE_NAME"], {"id": organization_id}, ["comparisonFlags"])
    print("comparisonFlags", comparisonFlags)
    comparison_flags.extend(comparisonFlags["comparisonFlags"].values())
    return comparison_flags


@app.route('/compare', cors=True, methods=['GET'], content_types=['application/json'])
def get_compare():
    threads = []
    organization_id = app.current_request.query_params.get(
        "organizationId", None)
    user_id = app.current_request.query_params.get("userId", None)
    limit = int(app.current_request.query_params.get("limit", 2))
    gamma_id = app.current_request.query_params.get("gammaId", None)
    start_with_gamma_id_1 = app.current_request.query_params.get(
        "startWithGammaId1", None)
    start_with_gamma_id_2 = app.current_request.query_params.get(
        "startWithGammaId2", None)
    last_comparison_id = app.current_request.query_params.get(
        "lastComparisonId", None)
    objective_id = app.current_request.query_params.get("objectiveId", None)
    nextToken = app.current_request.query_params.get("nextToken", None)
    if organization_id is None or organization_id == "undefined":
        raise BadRequestError(
            "No organization was selected or limit wasn't passed")

    comparison_flags = []
    threads.append(threading.Thread(target=check_comparison_flags,
                                    args=(organization_id, comparison_flags,)))
    threads[-1].start()
    comparisons = get_new_comparison(
        user_id, organization_id, limit, gamma_id, objective_id, nextToken)

    for thread in threads:
        thread.join()
    if not any(comparison_flags):
        return Response(body="Comparison disabled", status_code=400)

    if last_comparison_id:
        n = len(comparisons)
        for i in range(n):
            if comparisons[i]['id'] == last_comparison_id:
                comparisons = comparisons[:i]
                if i+1 < n:
                    comparisons += comparisons[i+1:]
                print("Remove duplicate Comparison.")
                break

    if len(comparisons) < limit:
        try:
            createComparisonStatus(user_id)
            params = {
                "type": "COMPARISONS_COMPLETED",
                "organization_id": organization_id,
                "user_id": user_id
            }
            response = lambda_client.invoke(
                FunctionName=FUNCTION_SCHEDULEDCOMPARISONQUEUER_NAME,
                InvocationType='Event',
                Payload=json.dumps(params).encode('utf-8')
            )

        except Exception as e:
            print("Comparions are already being created for user", user_id, e)
            deleteComparisonStatus(user_id)

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET'
        },
        'body': get_full_tree_arr(comparisons, start_with_gamma_id_1, start_with_gamma_id_2, objective_id)
    }