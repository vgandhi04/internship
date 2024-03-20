import json
import time
import requests
from jose import jwt

def lambda_handler(event, context):
    # Assuming the access_token is passed in the event or elsewhere
    access_token = event['authorizationToken']
    
    CLIEND_ID = "1qfo8elllmifgfemhl6l74n8sn"

    aws_region = "ap-south-1"
    user_pool_id = "ap-south-1_ylHWrsSdK"

    jwks_url = f'https://cognito-idp.{aws_region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json'

    # Fetch the keys from Cognito
    response = requests.get(jwks_url)
    print("response ", response)
    
    jwks = json.loads(response.text)
    # print("jwks ", jwks)
    print("jwks - key ", jwks['keys'])
    
    # Decode and verify the access_token using the fetched keys
    unverified_header = jwt.get_unverified_header(access_token)
    print("unverified_header ", unverified_header)
    
    rsa_key = {}
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e'],
            }
            print("rsa_key ", rsa_key)
            break

    # Verify the signature and decode the token
    decoded_token = jwt.decode(
        access_token,
        rsa_key,
        algorithms=['RS256'],
        audience='CLIEND_ID',
        issuer=f'https://cognito-idp.{aws_region}.amazonaws.com/{user_pool_id}',
    )

    # Now you can access claims in the decoded_token
    print("Decoded Token:", decoded_token)
    permission = "Deny"
    
    # Perform additional checks or actions based on the claims
    claims = jwt.get_unverified_claims(access_token)
    print("claims ", claims)
    
    if time.time() <= claims['exp']:
        print('Token is not expired')
        permission = "Allow"
    
    if claims['client_id'] == CLIEND_ID:
        print('Token was issued for this audience. Pool is SAME')
        permission = "Allow"
    
    authresponse = {
        "principalId" : 'user123',
        "policyDocument" : {
            "Version" : "2012-10-17",
            "Statement" : [
                {
                    "Action" : "execute-api:Invoke",
                    "Resource" : event['methodArn'],  """?"""
                    "Effect" : f"{permission}"
                }
            ]
        }
    }
    return authresponse