import os
import boto3
import json
import traceback
import AppSyncHelper
from gql import gql
import threading
from chaliceHelper import app
import CognitoUserHelper
FUNCTION_SAMPLEDATACREATOR_NAME = os.environ["FUNCTION_SAMPLEDATACREATOR_NAME"]

gqlClient = AppSyncHelper.create_graphql_client()
cognito_client = boto3.client('cognito-idp')
lambda_client = boto3.client('lambda')
USER_POOL_ID = os.environ['AUTH_STRALIGN5D0DB4AF_USERPOOLID']


def create_organization(organization_name):
    query = gql(
        """
            mutation CreateOrganization($name: String!) {
                createOrganization(input: {name: $name}) {
                    id
                    name
                }
                    
                }
        """
    )
    params = {
        "name": organization_name
    }
    gql_response = gqlClient.execute(query, variable_values=params)

    # response = cognito_client.create_group(
    #     GroupName=gql_response["createOrganization"]["id"],
    #     UserPoolId=USER_POOL_ID,
    #     Description=organization_name
    # )
    # print(response)

    return gql_response


def update_graphql_user(organization_id, organization_name, email, first_name, last_name, result):
    # get id from frontend instead of email, so we can remove userByemail query
    # or change chaliceHelper to pass user id
    query = gql(
        """
            query MyQuery ($email:AWSEmail!){
                userByEmail(email: $email) {
                    items {
                        id
                        email
                        }
                    }
            }
        """
    )
    params = {
        "email": email
    }

    user_id = gqlClient.execute(query, variable_values=params)[
        "userByEmail"]["items"][0]["id"]
    params = {
        "org_id": organization_id,
        "org_name": organization_name,
        "user_id": user_id
    }
    lambda_client.invoke(
        FunctionName=FUNCTION_SAMPLEDATACREATOR_NAME,
        InvocationType='Event',
        Payload=json.dumps(params).encode('utf-8'),
    )
    # user_id = gqlClient.execute(query, variable_values=params)
    # import weight from layer
    query = gql(
        """
            mutation UpdateUser($id: ID!, $organizationID: ID!, $firstName: String, $lastName: String) {
                updateUser(input: {id: $id, organizationID: $organizationID, firstName: $firstName, lastName: $lastName, role: ADMIN, weight: 5}) {
                id
                }
                
            }
        """
    )
    params = {
        "id": user_id,
        "organizationID": organization_id,
        "firstName": first_name,
        "lastName": last_name
    }
    user_data = gqlClient.execute(query, variable_values=params)
    result.update(user_data)

    user_attributes = [{
        'Name': 'given_name',
        'Value': first_name
    },
        {
        'Name': 'family_name',
        'Value': last_name
    }]
    CognitoUserHelper.update_user_attributes(
        cognito_client, USER_POOL_ID, email, user_attributes)
    return result


def update_user(organization_id, organization_name, email, first_name, last_name):
    update_graphql_response = {}
    threads = []

    threads.append(threading.Thread(target=update_graphql_user,
                                    args=(organization_id, organization_name, email, first_name, last_name, update_graphql_response,)))
    threads[-1].start()
    admin_group_response = CognitoUserHelper.add_user_to_group(
        cognito_client, USER_POOL_ID, email, "ADMIN")
    print("admin_group_response:", admin_group_response)
    # no need to create organization cognito group
    # org_group_response = CognitoUserHelper.add_user_to_group(
    #     cognito_client, USER_POOL_ID, email, organization_id)
    # print("cognito_response:", org_group_response)
    for thread in threads:
        thread.join()
    return update_graphql_response


@app.route('/signup', cors=True, methods=['POST'], content_types=['application/json'])
def signup():
    event = app.current_request.to_dict()
    body = app.current_request.json_body
    print('received event:')
    print(event)

    organization_id = body.get("organization_id", None)
    organization_name = body["organization_name"]
    first_name = body["first_name"]
    last_name = body["last_name"]

    email = body["email"].lower()
    # put badrequest error if no organization_id
    if organization_id is None:
        create_organization_response = create_organization(organization_name)
        organization_id = create_organization_response["createOrganization"]["id"]
        organization_name = create_organization_response["createOrganization"]["name"]
        try:
            user_data = update_user(
                organization_id, organization_name, email, first_name, last_name)

            response = {"message": "User signed up successfully."}
        except Exception as e:
            response = {"error": "Error signing up user"}
            traceback.print_exc()

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(response)
    }
