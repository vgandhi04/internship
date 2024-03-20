import urllib.request as urlreq
import json

aws_region = "ap-south-1"
user_pool_id = "ap-south-1_ylHWrsSdK"

response = urlreq.urlopen(f"https://cognito-idp.{aws_region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json")

# print(response) 
# data = response.read()
# print(type(data))

dict_data = json.loads(response.read().decode("utf-8"))

print(dict_data['keys'])

# for key in dict_data['keys']:
#     print(key)
#     print(key['kid'])
#     print(key['alg'])
#     print(key['use'])
#     print(key['kty'])
#     print(key['n'])
#     print(key['e'])
    
    
# print(response.status) 
# print(response.headers) 
# print(response.read)
 