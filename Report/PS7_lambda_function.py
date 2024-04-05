import json
import time
import urllib.request
from jose import jwk, jwt
from jose.utils import base64url_decode

# Token to be matched with 
TOKEN = "eyJraWQiOiI5VmZ4ajhqOU56WXR5MDA3aEV2YnhOYkptd1FhSW04ZE5TN3VhdkdLUjQ0PSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI4MTEzN2Q0YS1lMDUxLTcwZmQtNzE0Zi02MDhlODE2ODc4MTQiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuYXAtc291dGgtMS5hbWF6b25hd3MuY29tXC9hcC1zb3V0aC0xX3lsSFdyc1NkSyIsInZlcnNpb24iOjIsImNsaWVudF9pZCI6IjFxZm84ZWxsbG1pZmdmZW1obDZsNzRuOHNuIiwiZXZlbnRfaWQiOiJiZWFkYjk2Zi01MThmLTRjNGUtYTEyMS1lNjVhYWU0MTJlNmYiLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6InBob25lIG9wZW5pZCBlbWFpbCIsImF1dGhfdGltZSI6MTcwNzMwODYwNSwiZXhwIjoxNzA3MzEyMjA1LCJpYXQiOjE3MDczMDg2MDUsImp0aSI6IjRjMmU5MjNhLWQ2NDAtNDYzNS1hNGQ0LTIxNzVlNjA4YmQxMSIsInVzZXJuYW1lIjoidGVzdDEifQ.EUPVk7xtrmZGVG5AWf5yMs0Zyd1wcPmWEqxmo7BXorMuKDZNGaRd_mThazllHQ7lWBaw_c54z7Bm8XgOun3RXRPxZEJPczI5r9zZauHy8xzeLayLyzAl5swVSLKF1WxOGJOZvEQMPAOHmdJhZAqbEqJ9Xc2v4BiHtubMCcctr30wFqtG41u7hgiMYbuGzjDx0eDcF7tPKv0F1WRnUcX-47k0UoasFyWUwY8oaq9rurKkp6HrLY2W8bZIqQeaAasTddRKBY23HlBJu1zhm-ncPN9zngbP4-LT1V7f7xVz7pxi7-CESCWZ6CPGi7vpSN4mhXXunlhhJkpuZh-zH0Mf_A"
REGION = "ap-south-1"
USERPOOLID = "ap-south-1_ylHWrsSdK"
CLIEND_ID = "1qfo8elllmifgfemhl6l74n8sn"

KEY_URL = "https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json".format(REGION, USERPOOLID)

with urllib.request.urlopen(KEY_URL) as f:
    response = f.read()
    
print("response ", response)
keys_res = json.loads(response.decode('utf-8'))['keys']

print("keys ", keys_res)

# response = requests.get(KEY_URL)
# print("response ", response)
# json_data = response.json()
# keys = list(json_data['keys'])

# print("json_data ", keys)


def lambda_handler(event, context):
    # TODO implement
    print("Event ", event)
    print("Context ", context)
    # Assuming the access_token is passed in the event or elsewhere
    access_token = event['headers']['authorizationToken'].split(' ')[1]
    print("access_token ", access_token)
            
    token = event['authorizationToken']
    headers = jwt.get_unverified_headers(token)
    print("headers ", headers)
    token_kid = headers['kid']
    print("header_kid ", token_kid)  
    key_index = -1
    for i in range(0,len(keys_res)):
        if token_kid == keys_res[i]['kid']:
            key_index = i
            break
    
    if key_index == -1:
        print('Public key not found in jwks.json')
        return False
    
    public_key = jwk.construct(keys_res[key_index])
    print("public_key ", public_key)

    message, encoded_signature = str(token).rsplit('.', 1)
    print("message ", message)
    print("encoded_signature ", encoded_signature)
    
    decoded_message = message.encode("utf8")
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
    print(f"decoded_signature {decoded_signature} decodedme_message {decoded_message}")
    
    if not public_key.verify(decoded_message, decoded_signature):
        print('Signature verification failed')
        return False
    
    print('Signature verification Successfull')
    
    claims = jwt.get_unverified_claims(token)
    print("claims ", claims)
    
    if time.time() > claims['exp']:
        print('Token is expired')
        return False
    
    if claims['client_id'] != CLIEND_ID:
        print('Token was not issued for this audience. Pool is different')
        return False
    
    permission = "Deny"
    
    if token == TOKEN:
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