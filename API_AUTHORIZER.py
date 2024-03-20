import json
import time
# import requests # large moule
import os
import urllib.request as url
from jose import jwt   # pip install python-jose

USER_POOL_ID = os.environ.get('AUTH_MOVIE9A1F50E7_USERPOOLID')
AWS_REGION = os.environ.get('REGION')

def handler(event, context):
    try:
        print('received event:')
        print(event)
        # access_token = event['headers']['auth-token']
        # access_token = event['headers']['authorizationToken']
        access_token = event['authorizationToken']
        print("access_token ", access_token)
        CLIENT_ID = "4nf5u9kttk94i0ur5q4m3ffpa0"    
        
        jwks_url = f'https://cognito-idp.{AWS_REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json'

        response = url.urlopen(jwks_url)
        jwks = json.loads(response.read().decode('utf-8'))
        # Fetch the keys from Cognito
        # response = requests.get(jwks_url)
        # print("response ", response)
        
        # jwks = json.loads(response.text)
        # print("jwks ", jwks)
        # print("jwks - key ", jwks['keys'])
        
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
            audience='CLIENT_ID',
            issuer=f'https://cognito-idp.{AWS_REGION}.amazonaws.com/{USER_POOL_ID}',
        )

        # Now you can access claims in the decoded_token
        print("Decoded Token:", decoded_token)
                
        # Perform additional checks or actions based on the claims
        claims = jwt.get_unverified_claims(access_token)
        print("claims ", claims)
        
        permission = "Deny"
        if time.time() <= claims['exp']:
            print('Token is valid.')
            if claims['client_id'] == CLIENT_ID:
                print('Token is issued for this audience. Pool is SAME')
                permission = "Allow"
        else:
            print('Token is expired or issued for other audience.')
            
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
    except Exception as e:
        print(f"Error adding data: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('An error occurred: {}'.format(e))
        }
  
     
        
    # return {
    #     'statusCode': 200,
    #     'headers': {
    #         'Access-Control-Allow-Headers': '*',
    #         'Access-Control-Allow-Origin': '*',
    #         'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    #     },
    #     'body': json.dumps('Hello from your new Amplify Python lambda!')
    # }