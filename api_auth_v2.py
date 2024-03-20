import json
from jose import jwt

def lambda_handler(event, context):
    # Assuming the access_token is passed in the event or elsewhere
    access_token = event['headers']['Authorization'].split(' ')[1]

    # Replace 'YOUR_USER_POOL_ID' with your actual user pool ID
    user_pool_id = 'YOUR_USER_POOL_ID'

    # Replace 'YOUR_REGION' with your actual AWS region
    aws_region = 'YOUR_REGION'
    
    # CLIEND_ID = "1qfo8elllmifgfemhl6l74n8sn"

    # aws_region = "ap-south-1"
    # user_pool_id = "ap-south-1_ylHWrsSdK"

    # Get the public key from Cognito to verify the token
    jwks_url = f'https://cognito-idp.{aws_region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json'

    # Fetch the keys from Cognito
    response = requests.get(jwks_url)
    jwks = json.loads(response.text)

    # Decode and verify the access_token using the fetched keys
    unverified_header = jwt.get_unverified_header(access_token)
    rsa_key = {}
    
    rsa_key = next(({
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e'],
            } for key in jwks['keys'] if key['kid'] == unverified_header['kid']), None)
     
    # for key in jwks['keys']:
    #     if key['kid'] == unverified_header['kid']:
    #         rsa_key = {
    #             'kty': key['kty'],
    #             'kid': key['kid'],
    #             'use': key['use'],
    #             'n': key['n'],
    #             'e': key['e'],
    #         }

    # Verify the signature and decode the token
    decoded_token = jwt.decode(
        access_token,
        rsa_key,
        algorithms=['RS256'],
        audience='YOUR_APP_CLIENT_ID',  # Replace with your app client ID
        issuer=f'https://cognito-idp.{aws_region}.amazonaws.com/{user_pool_id}',
    )

    # Now you can access claims in the decoded_token
    print("Decoded Token:", decoded_token)

    # Perform additional checks or actions based on the claims

    return {
        'statusCode': 200,
        'body': json.dumps('Token verification successful'),
    }
