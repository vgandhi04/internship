import json

def lambda_handler(event, context):
    # TODO implement
    print("Event ", event)
    print("Context ", context)
    
    token = event['authorizationToken']
    
    print("token ", token)
    permission = "Deny"
    
    if token == "valid-token":
        permission = "Allow"
    
    authresponse = {
        "principalId" : 'user123',
        "policyDocument" : {
            "Version" : "2012-10-17",
            "Statement" : [
                {
                    "Action" : "execute-api:Invoke",
                    "Resource" : event['methodArn'],
                    "Effect" : f"{permission}"
                }
            ]
        }
    }
    return authresponse 
    