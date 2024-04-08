import json
import time
import os
import urllib.request as url
from jose import jwt

USER_POOL_ID = os.environ.get('AUTH_MOVIE9A1F50E7_USERPOOLID')
AWS_REGION = os.environ.get('REGION')
ENV = os.environ.get('ENV')

if ENV == "dev":
    CLIENT_ID = "6t1afmo4o4n2p7ru3d2o52robv"
else:
    CLIENT_ID = "41e7n6tptvk0gibe8b957qfp2a"
    

def handler(event, context):
    try:
        print('received event:')
        print(event)
        print('received context:')
        print(context)
        access_token = event['authorizationToken']
        print("access_token ", access_token)
                
        jwks_url = f'https://cognito-idp.{AWS_REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json'

        response = url.urlopen(jwks_url)
        jwks = json.loads(response.read().decode('utf-8'))
        
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
            print('Token is valid for time being.')
            if claims['client_id'] == CLIENT_ID:
                print('Token is issued for this audience. Pool is SAME')
                permission = "Allow"
            else:
                print('Token is not issued for this audience. Pool is DIFFERENT')
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