import json
import boto3
import os
from boto3.dynamodb.conditions import Key

# DynamoDB configuration
# dynamodb_client = boto3.client('dynamodb')
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('API_MOVIEGQL_USERTABLE_NAME')
table = dynamodb.Table(TABLE_NAME)
print("table - ", table)

def handler(event, context):
    print('received event:')
    print("Event in PRE - ", event)
  
    """
    This function handles adding a custom claim to the cognito ID token.
    """
    
    
    # check requestor's information
    if 'userAttributes' in event['request'] and 'cognito:user_status' in event['request']['userAttributes']:
        user_status = event['request']['userAttributes']['cognito:user_status']
        email_verified = event['request']['userAttributes'].get('email_verified', 'false')
        user_email = event['request']['userAttributes']['email']
    else:
        user_status = None
        email_verified = 'false'
        user_email = event['request']['userAttributes']['email']
    
    # Check user's status and email
    if user_status == 'CONFIRMED' and email_verified == 'true':
        # Query DynamoDB to get user's organization ID
        response = table.query(
            IndexName='byEmail',
            KeyConditionExpression=Key('email').eq(user_email)
        )
        items_found = response.get('Items', [])
        print("items_found - ", items_found)
        user_organization_ids = []
        
        for item in items_found:
            organization_id = item.get('organizationID')
            print("organization_id - ", organization_id)
            role_name = item.get('role')
            print("role_name - ", role_name)
            if organization_id:
                user_organization_ids.append(organization_id)
                user_organization_ids.append(f"{organization_id}-{role_name}")
        
        # Override the claims
        if user_organization_ids:
            pet_preference = 'dogs'
            organization_ids = user_organization_ids
            # this allows us to override claims in the id token
            # "claimsToAddOrOverride" is for single vlaue
            # "groupOverrideDetails" is for list
            event["response"]["claimsOverrideDetails"] = { 
                "claimsToAddOrOverride": { 
                    "pet_preference": pet_preference
                },
                "groupOverrideDetails" :{
                    "groupsToOverride": organization_ids
                }
            }
    
    print("Event in POST - ", event)
    # return modified ID token to Amazon Cognito 
    return event 