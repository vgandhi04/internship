import os
import boto3
import time
import json
from decimal import Decimal
import threading
from datetime import datetime
import AppSyncHelper
from gql import gql
from boto3.dynamodb.conditions import Key
import DynamoDBHelper
from chaliceHelper import app, BadRequestError, Response
import copy


GQL_CLIENT = AppSyncHelper.create_graphql_client()
DYNAMODB_RESOURCE = boto3.resource('dynamodb')
OBJECTIVE_TABLE = DYNAMODB_RESOURCE.Table(
    'Objective-3xhxsmq2obec7jlynahan3otgm-dev')
STAGE_TABLE = DYNAMODB_RESOURCE.Table('Stage-3xhxsmq2obec7jlynahan3otgm-dev')
COMPARISON_TABLE = DYNAMODB_RESOURCE.Table(
    'Comparison-3xhxsmq2obec7jlynahan3otgm-dev')
GAMMA_TABLE_NAME = 'Gamma-3xhxsmq2obec7jlynahan3otgm-dev'
LAMBDA_CLIENT = boto3.client('lambda')
FUNCTION_SCHEDULEDCOMPARISONQUEUER_NAME = os.environ["FUNCTION_SCHEDULEDCOMPARISONQUEUER_NAME"]

# Defining varilable for tree structure of uservote
total_levels = 5
TOTAL_NODES = (2 ** total_levels) - 1


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

    gql_response = GQL_CLIENT.execute(mutation, variable_values=params)
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

    gql_response = GQL_CLIENT.execute(mutation, variable_values=params)
    # print("gql response", gql_response)


# Making binary tree from the data given in form of array.
def structer_data_in_tree(data, structured_arr):
    
    # finding the index
    def get_index_id(arr, gamma_id, objective_id):
        len_arr = len(arr)
        for i in range(len_arr):
            gamma_1_id = arr[i]['gamma1ID']
            gamma_2_id = arr[i]['gamma2ID']
            if (gamma_id == gamma_1_id or gamma_id == gamma_2_id) and objective_id == arr[i]['objectiveID']:
                return i

            if (gamma_id == gamma_1_id or gamma_id == gamma_2_id):
                return i
        return None
    
    
    i = 0
    len_structured_arr = len(structured_arr)
    while len_structured_arr > i:
        try:
            # Get left node object
            left_id_index = None
            right_id_index = None

            # Filling Left Child
            left_cal = (2*i)+1
            if left_cal < TOTAL_NODES:
                structured_arr_gamma1 = structured_arr[i]['gamma1ID']
                if structured_arr[i] and structured_arr_gamma1:
                    left_id_index = get_index_id(
                        data, structured_arr_gamma1, structured_arr[i]['objectiveID'])

                # is left child exist?
                if left_id_index != None:
                    # Swap the gammas if not match as per expected
                    if structured_arr_gamma1 != data[left_id_index]['gamma1ID'] and structured_arr_gamma1 == data[left_id_index]['gamma2ID']:
                        data[left_id_index]['gamma1ID'], data[left_id_index]['gamma2ID'] = data[left_id_index]['gamma2ID'], data[left_id_index]['gamma1ID']

                    structured_arr[left_cal] = data[left_id_index]

                    # Removing element as it taken in structured_arr array
                    data.pop(left_id_index)
                # left child not exist i.e assing None value
                else:
                    structured_arr[left_cal] = None

            # Filling Right child
            right_cal = (2*i)+2
            if right_cal < TOTAL_NODES:
                structured_arr_gamma2 = structured_arr[i]['gamma2ID']
                if structured_arr[i] and structured_arr[i]['gamma1ID']:
                    right_id_index = get_index_id(data, structured_arr_gamma2, structured_arr[i]['objectiveID'])

                # is right child exist?
                if right_id_index != None:

                    # Swap the gammas if not match as per expected
                    if structured_arr_gamma2 != data[right_id_index]['gamma2ID'] and structured_arr_gamma2 == data[right_id_index]['gamma1ID']:
                        data[right_id_index]['gamma1ID'], data[right_id_index]['gamma2ID'] = data[right_id_index]['gamma2ID'], data[right_id_index]['gamma1ID']

                    structured_arr[right_cal] = data[right_id_index]

                    # Removing element as it taken in structured_arr array
                    data.pop(right_id_index)

                # right child not exist i.e assing None value
                else:
                    structured_arr[right_cal] = None

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
    len_main_arr = len(main_arr)
    for i in range(len_main_arr):
        # Defining empty array
        structured_arr = [{} for _ in range((TOTAL_NODES))]

        # Assigning Root Node
        structured_arr[0] = (main_arr[i])
        structured_arr_0_gamma1 = structured_arr[0]['gamma1ID']
        structured_arr_0_gamma2 = structured_arr[0]['gamma2ID']
        gammaIdGiven = False
        if start_with_gamma_id_1 and (structured_arr_0_gamma1 != start_with_gamma_id_1 or structured_arr_0_gamma2 == start_with_gamma_id_1):
                structured_arr_0_gamma1, structured_arr_0_gamma2 = structured_arr_0_gamma2, structured_arr_0_gamma1
                gammaIdGiven = True
        elif start_with_gamma_id_2 and (structured_arr_0_gamma2 != start_with_gamma_id_2 or structured_arr_0_gamma1 == start_with_gamma_id_2):
                structured_arr_0_gamma1, structured_arr_0_gamma2 = structured_arr_0_gamma2, structured_arr_0_gamma1
                gammaIdGiven = True

        temp_arr = structer_data_in_tree(
            main_arr[:i] + main_arr[i+1:], copy.deepcopy(structured_arr))

        if not final_arr:
            final_arr = copy.deepcopy(temp_arr)

        # updating the final tree with Specific Gamma Id positions
        elif start_with_gamma_id_1:
            if final_arr[0]['gamma1ID'] != start_with_gamma_id_1 and temp_arr[0]['gamma1ID'] == start_with_gamma_id_1:
                # if final_arr[0]['objective']['id'] != objective_id or temp_arr[0]['objective']['id'] == objective_id:
                final_arr = temp_arr
                gammaIdGiven = False

        elif start_with_gamma_id_2:
            if final_arr[0]['gamma2ID'] != start_with_gamma_id_2 and temp_arr[0]['gamma2ID'] == start_with_gamma_id_2:
                # if final_arr[0]['objective']['id'] != objective_id or temp_arr[0]['objective']['id'] == objective_id:
                final_arr = temp_arr
                gammaIdGiven = False

        if final_arr.count(None) == 0 and not gammaIdGiven:
            break
        # Calculating the minimum None value in array. Minimum None value means the near to full binary tree.
        final_arr_count_none = final_arr.count(None)
        temp_arr_count_none = temp_arr.count(None)
        if final_arr_count_none > temp_arr_count_none:
            if (start_with_gamma_id_1 and temp_arr[0]['gamma1ID'] == start_with_gamma_id_1) or (start_with_gamma_id_2 and temp_arr[0]['gamma2ID'] == start_with_gamma_id_2) or (not start_with_gamma_id_1 and not start_with_gamma_id_2):
                    # if final_arr[0]['objective']['id'] != objective_id or temp_arr[0]['objective']['id'] == objective_id:
                    final_arr = copy.deepcopy(temp_arr)

    return final_arr



def get_new_comparison(userId, organization_id, limit=2, gamma_id=None, objective_id=None, nextToken=None):
    start = time.time()
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
    gql_response = GQL_CLIENT.execute(query, variable_values=params)
    print("gql response", gql_response)
    print("time taken to fetch 200 comparisons", time.time()-start)

    gql_response["comparisonsByUserID"]["items"] = [
        item for item in gql_response["comparisonsByUserID"]["items"] if item['gamma1'] and item['gamma2']]
    return gql_response["comparisonsByUserID"]["items"]


def batch_list(input_list, batch_size):
    # return [dict(zip(keys[i:i+batch_size], (array[key] for key in keys[i:i+batch_size])))
    #         for i in range(0, len(array), batch_size)]
    return [input_list[i:i + batch_size] for i in range(0, len(input_list), batch_size)]


def batch_get(ddb_resource, table_name, keys, select):
    print('received input:')
    print(keys)
    items = []

    print("table name", table_name)
    table = ddb_resource.Table(table_name)
    for batch in batch_list(keys, 100):
        batch_keys = {
            table.name: {
                'Keys': batch
            }
        }
        if select:
            batch_keys[table.name]['ProjectionExpression'] = ",".join(select)
        try:
            items.extend(ddb_resource.batch_get_item(
                RequestItems=batch_keys)['Responses'][table.name])
        except Exception as e:
            print("error", e)
            return e
    return items


def get_comparisons(userId, organization_id, limit=2, gamma_id=None, objective_id=None, nextToken=None):
    comparisons_response = COMPARISON_TABLE.query(
        KeyConditionExpression=Key('userID').eq(userId),
        IndexName='byUser',
        ProjectionExpression='id,gamma1ID,gamma2ID,objectiveID',
        Limit=200
    )

    print(comparisons_response['Items'])
    return comparisons_response['Items']


def get_comparison_details(comparisons_response, gamma_details):

    unique_gammaIDs_set = {item['gamma1ID'] for item in comparisons_response}.union(
        {item['gamma2ID'] for item in comparisons_response})
    gamma_keys = [{'id': gamma_id} for gamma_id in unique_gammaIDs_set]

    res = batch_get(DYNAMODB_RESOURCE, GAMMA_TABLE_NAME, gamma_keys, [
        'id', 'title', 'description', 'levelID'])
    gamma_details.update({item['id']: item for item in res})
    print("gamma_details", gamma_details)

    return gamma_details


def get_stages_objectives(organization_id, stage_details, objective_details):
    objectives_response = OBJECTIVE_TABLE.query(
        KeyConditionExpression=Key(
            'organizationObjectivesId').eq(organization_id),
        IndexName='byOrganization',
        ProjectionExpression='id,#n,description',
        ExpressionAttributeNames={'#n': 'name'}
    )
    stages_response = STAGE_TABLE.query(
        KeyConditionExpression=Key('organizationID').eq(organization_id),
        IndexName='byOrganization',
        ProjectionExpression='id,#n,#l',
        ExpressionAttributeNames={'#n': 'name', '#l': 'level'}
    )
    print(objectives_response['Items'])
    print(stages_response['Items'])
    stage_details.update(
        {item['id']: item for item in stages_response['Items']})
    objective_details.update(
        {item['id']: item for item in objectives_response['Items']})
    return stage_details, objective_details


def check_comparison_flags(organization_id, comparison_flags):
    comparisonFlags = DynamoDBHelper.get(
        DYNAMODB_RESOURCE, os.environ["API_STRALIGN_ORGANIZATIONTABLE_NAME"], {"id": organization_id}, ["comparisonFlags"])
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

    comparisons = get_comparisons(
        user_id, organization_id, limit, gamma_id, objective_id, nextToken)

    comparison_flags = []
    threads.append(threading.Thread(target=check_comparison_flags,
                                    args=(organization_id, comparison_flags,)))
    threads[-1].start()

    gamma_details = {}

    threads.append(threading.Thread(target=get_comparison_details,
                                    args=(comparisons, gamma_details,)))
    threads[-1].start()

    stage_details = {}
    objective_details = {}

    threads.append(threading.Thread(target=get_stages_objectives,
                                    args=(organization_id, stage_details, objective_details,)))
    threads[-1].start()

    # comparisons = get_new_comparison(
    #     user_id, organization_id, limit, gamma_id, objective_id, nextToken)

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
            response = LAMBDA_CLIENT.invoke(
                FunctionName=FUNCTION_SCHEDULEDCOMPARISONQUEUER_NAME,
                InvocationType='Event',
                Payload=json.dumps(params).encode('utf-8')
            )

        except Exception as e:
            print("Comparions are already being created for user", user_id, e)
            deleteComparisonStatus(user_id)

    comparison_tree = get_full_tree_arr(
        comparisons, start_with_gamma_id_1, start_with_gamma_id_2, objective_id)

    for thread in threads:
        thread.join()
    print("comparison_tree", comparison_tree)
    if not any(comparison_flags):
        return Response(body="Comparison disabled", status_code=400)
    print(comparison_tree)
    final_comparison_tree = [{'id': comparison['id'], 'gamma1': {**gamma_details[comparison['gamma1ID']], 'level': stage_details[gamma_details[comparison['gamma1ID']]['levelID']]}, 'gamma2': {**gamma_details[comparison['gamma2ID']], 'level': stage_details[gamma_details[comparison['gamma2ID']]['levelID']]}, 'objective': objective_details[comparison['objectiveID']]} for comparison in comparison_tree
                             if gamma_details.get(comparison['gamma1ID']) and gamma_details.get(comparison['gamma2ID'])]
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET'
        },
        'body': final_comparison_tree
    }


@app.route('/compare', cors=True, methods=['POST'], content_types=['application/json'])
def post_compare():
    event = app.current_request.to_dict()
    body = app.current_request.json_body
    # Remove unnecessary print statements
    # print('received event:')
    # print(event)
    print("body", body)

    comparison_id = body.get("comparison_id", None)
    if comparison_id is not None:
        try:
            timenow = generate_iso8601_string()
            DynamoDBHelper.batch_delete(
                DYNAMODB_RESOURCE, os.environ["API_STRALIGN_COMPARISONTABLE_NAME"], [{"id": body["comparison_id"]}])
            if body.get("user_id", None):
                user_votes = [
                    {
                        "gammaID": body["Gamma1"]["gammaId"],
                        "userID": body["user_id"],
                        "userVoteObjectiveId": body["objective_id"],
                        "userVoteVsGammaId": body["Gamma2"]["gammaId"],
                        "vote": 1 if body["Gamma1"]["selected"] else (0 if body["Gamma1"]["skipped"] else -1),
                        "weight": body["Gamma1"]["user_support"],
                        "organizationID": body["organizationId"],
                        "voteTime": int(body["Gamma2"]["voteTime"]),
                        "__typename": "UserVote",
                        "createdAt": timenow,
                        "updatedAt": timenow
                    },
                    {
                        "gammaID": body["Gamma2"]["gammaId"],
                        "userID": body["user_id"],
                        "userVoteObjectiveId": body["objective_id"],
                        "userVoteVsGammaId": body["Gamma1"]["gammaId"],
                        "vote": 1 if body["Gamma2"]["selected"] else (0 if body["Gamma2"]["skipped"] else -1),
                        "weight": body["Gamma2"]["user_support"],
                        "organizationID": body["organizationId"],
                        "voteTime": int(body["Gamma2"]["voteTime"]),
                        "__typename": "UserVote",
                        "createdAt": timenow,
                        "updatedAt": timenow
                    }
                ]
                DynamoDBHelper.batch_write(
                    DYNAMODB_RESOURCE, os.environ["API_STRALIGN_USERVOTETABLE_NAME"], user_votes)
        except Exception as e:
            print("error", e)
            raise BadRequestError(
                "insufficient data")

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST'
        },
        'body': "Comparison data posted successfully"
    }