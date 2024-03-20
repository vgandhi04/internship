import json
import time
import urllib.request
# from jose import jwk, jwt
# from jose.utils import base64url_decode

TOKEN = "eyJraWQiOiI5VmZ4ajhqOU56WXR5MDA3aEV2YnhOYkptd1FhSW04ZE5TN3VhdkdLUjQ0PSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI4MTEzN2Q0YS1lMDUxLTcwZmQtNzE0Zi02MDhlODE2ODc4MTQiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuYXAtc291dGgtMS5hbWF6b25hd3MuY29tXC9hcC1zb3V0aC0xX3lsSFdyc1NkSyIsInZlcnNpb24iOjIsImNsaWVudF9pZCI6IjFxZm84ZWxsbG1pZmdmZW1obDZsNzRuOHNuIiwiZXZlbnRfaWQiOiJkNWYwNjI3MC0zMzhhLTQyNmMtYjJmMC1lYmM4YWMzOTQyYjYiLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6InBob25lIG9wZW5pZCBlbWFpbCIsImF1dGhfdGltZSI6MTcwNzE5NzU1OCwiZXhwIjoxNzA3MjAxMTU4LCJpYXQiOjE3MDcxOTc1NTgsImp0aSI6IjdlOGI2NDkzLTE2YWEtNDc1ZC04MDk1LTFhMTkyNDFmM2I0NyIsInVzZXJuYW1lIjoidGVzdDEifQ.MNTNk4nWVDjTJOk5TwZ56EjsylXrAFrv0Sl1mS87WSTWSmz4DjqFZLvJsaGSVdZ_71YhHTMRlVb1_VBhbgJaHqIaby4iMGyLohA33edMXW4uvdrOhligqguLerVuLNal5rGn_yHKJpKji94-JuVYaFoQ7enimvfvWCumu7tjcSr4ANayv7tCO_jeXjpzcD8CNyFIq-Ro2xfgSQz_1nOZ_xPvIfStK4cX9YhMwEx3DxLC1grJtRrJEFcF6oPcq9iuFvPgi4SpmHjxa69yHXPacDyLNBvefIQpP-DTg2F9WCuosw2uiot1aH-MWq0NPn1wO08C0EBK2ZPZhk_Mcf_bKQ"
REGION = "ap-south-1"
USERPOOLID = "ap-south-1_ylHWrsSdK"

KEY_URL = "https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json".format(REGION, USERPOOLID)

with urllib.request.urlopen(KEY_URL) as f:
    response = f.read()
    
print("response ", response)
keys = json.loads(response.decode('utf-8'))['keys']

print("keys ", keys)

# response = requests.get(KEY_URL)
# print("response ", response)
# json_data = response.json()
# keys = list(json_data['keys'])

# print("json_data ", keys)


def lambda_handler(event, context):
    # TODO implement
    print("Event ", event)
    print("Context ", context)
        
    token = event['authorizationToken']
    
    print("token ", token)
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
    