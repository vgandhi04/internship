{
    'resource': '/movie', 
    'path': '/movie', 
    'httpMethod': 'POST', 
    'headers': {
        'Accept': '*/*', 
        'Accept-Encoding': 'gzip, deflate, br', 
        'auth-token': 'eyJraWQiOiJncWtRNllqSHp1V2FGeG5nSVwveVdHNXg3N05zNkZMSlVqK2dGcFV3a0g4cz0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJjMWYzNmQzYS1mMDUxLTcwYzMtNDM1ZS0yZmE0YmYxYjViMTEiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuYXAtc291dGgtMS5hbWF6b25hd3MuY29tXC9hcC1zb3V0aC0xX0drOXpLeHlDTyIsInZlcnNpb24iOjIsImNsaWVudF9pZCI6IjMxMDNzcXFpYzRzODVpcW4wdjg2MHA5OTg1IiwiZXZlbnRfaWQiOiI4MGMzMzUyMy0zMDMxLTQxYzItOTY0YS0wNDI5MzBlNDAxZjMiLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6ImF3cy5jb2duaXRvLnNpZ25pbi51c2VyLmFkbWluIHBob25lIG9wZW5pZCBwcm9maWxlIGVtYWlsIiwiYXV0aF90aW1lIjoxNzA3OTc2NDM3LCJleHAiOjE3MDc5ODAwMzcsImlhdCI6MTcwNzk3NjQzNywianRpIjoiOWQ1Mzg3YTItMzI2OS00ZDUzLWI5MDEtNTRhYmFiNzM0OTVjIiwidXNlcm5hbWUiOiJ0ZXN0MTIzIn0.fvJs_xORkOBtLJM9OSHUqlBwfhFfa8_P6E54rWMo-9y3039vzU2yOX9xuJTXroehe8i8XNqc7qUVjRlHmok-C2fuZOADY_Yh09cRU4k1HEgEcD0gA_Tz9hHcbO7fOJRhec0OBaRnEdGBwIbltiIye4iJ0p5utCkjx2NkGhm5TcalHpz_I8CzCe88UP_GPnCQjMHzhzoyyKOeKB9NXeu5YzdoQQAyGXcYnOmWsZbihtPa1myIqbcN6mcK8MZxNJRbdmaFYDRIUFPCu7Ul2D_oSrzjDOt88yj1-M_e4ihb5C7arrWPJV7iUZMInKjOoYvM1AaOml6ePT1sCDe1ro8fjA',
        'Cache-Control': 'no-cache', 
        'CloudFront-Forwarded-Proto': 'https', 
        'CloudFront-Is-Desktop-Viewer': 'true', 
        'CloudFront-Is-Mobile-Viewer': 'false', 
        'CloudFront-Is-SmartTV-Viewer': 'false', 
        'CloudFront-Is-Tablet-Viewer': 'false', 
        'CloudFront-Viewer-ASN': '14618', 
        'CloudFront-Viewer-Country': 'US', 
        'Content-Type': 'application/json', 
        'Host': 'l3xtkc2hlj.execute-api.ap-south-1.amazonaws.com', 
        'Postman-Token': '3eb90f83-632e-4f55-b1ec-6257653ab4b2', 
        'User-Agent': 'PostmanRuntime/7.36.3', 
        'Via': '1.1 4c3936cc7f5f36d3966cb34ebcbf91a6.cloudfront.net (CloudFront)', 
        'X-Amz-Cf-Id': 'vDqYc8I98CU-fyokp7WfInd795F6rhKn2OgK4gDL2dYALPl803Ulpg==', 
        'X-Amzn-Trace-Id': 'Root=1-65cda717-625c3788264f48037314be02', 
        'X-Forwarded-For': '54.86.50.139, 70.132.32.90', 
        'X-Forwarded-Port': '443', 
        'X-Forwarded-Proto': 'https'
    }, 
    'multiValueHeaders': {
        'Accept': ['*/*'], 
        'Accept-Encoding': ['gzip, deflate, br'], 
        'auth-token': ['eyJraWQiOiJncWtRNllqSHp1V2FGeG5nSVwveVdHNXg3N05zNkZMSlVqK2dGcFV3a0g4cz0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJjMWYzNmQzYS1mMDUxLTcwYzMtNDM1ZS0yZmE0YmYxYjViMTEiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuYXAtc291dGgtMS5hbWF6b25hd3MuY29tXC9hcC1zb3V0aC0xX0drOXpLeHlDTyIsInZlcnNpb24iOjIsImNsaWVudF9pZCI6IjMxMDNzcXFpYzRzODVpcW4wdjg2MHA5OTg1IiwiZXZlbnRfaWQiOiI4MGMzMzUyMy0zMDMxLTQxYzItOTY0YS0wNDI5MzBlNDAxZjMiLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6ImF3cy5jb2duaXRvLnNpZ25pbi51c2VyLmFkbWluIHBob25lIG9wZW5pZCBwcm9maWxlIGVtYWlsIiwiYXV0aF90aW1lIjoxNzA3OTc2NDM3LCJleHAiOjE3MDc5ODAwMzcsImlhdCI6MTcwNzk3NjQzNywianRpIjoiOWQ1Mzg3YTItMzI2OS00ZDUzLWI5MDEtNTRhYmFiNzM0OTVjIiwidXNlcm5hbWUiOiJ0ZXN0MTIzIn0.fvJs_xORkOBtLJM9OSHUqlBwfhFfa8_P6E54rWMo-9y3039vzU2yOX9xuJTXroehe8i8XNqc7qUVjRlHmok-C2fuZOADY_Yh09cRU4k1HEgEcD0gA_Tz9hHcbO7fOJRhec0OBaRnEdGBwIbltiIye4iJ0p5utCkjx2NkGhm5TcalHpz_I8CzCe88UP_GPnCQjMHzhzoyyKOeKB9NXeu5YzdoQQAyGXcYnOmWsZbihtPa1myIqbcN6mcK8MZxNJRbdmaFYDRIUFPCu7Ul2D_oSrzjDOt88yj1-M_e4ihb5C7arrWPJV7iUZMInKjOoYvM1AaOml6ePT1sCDe1ro8fjA'], 
        'Cache-Control': ['no-cache'], 
        'CloudFront-Forwarded-Proto': ['https'], 
        'CloudFront-Is-Desktop-Viewer': ['true'], 
        'CloudFront-Is-Mobile-Viewer': ['false'], 
        'CloudFront-Is-SmartTV-Viewer': ['false'], 
        'CloudFront-Is-Tablet-Viewer': ['false'], 
        'CloudFront-Viewer-ASN': ['14618'], 
        'CloudFront-Viewer-Country': ['US'], 
        'Content-Type': ['application/json'], 
        'Host': ['l3xtkc2hlj.execute-api.ap-south-1.amazonaws.com'], 
        'Postman-Token': ['3eb90f83-632e-4f55-b1ec-6257653ab4b2'], 
        'User-Agent': ['PostmanRuntime/7.36.3'], 
        'Via': ['1.1 4c3936cc7f5f36d3966cb34ebcbf91a6.cloudfront.net (CloudFront)'], 
        'X-Amz-Cf-Id': ['vDqYc8I98CU-fyokp7WfInd795F6rhKn2OgK4gDL2dYALPl803Ulpg=='], 
        'X-Amzn-Trace-Id': ['Root=1-65cda717-625c3788264f48037314be02'], 
        'X-Forwarded-For': ['54.86.50.139, 70.132.32.90'], 
        'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https']
    }, 
    'queryStringParameters': None, 
    'multiValueQueryStringParameters': None, 
    'pathParameters': None, 
    'stageVariables': None, 
    'requestContext': {
        'resourceId': '70w8fz', 
        'resourcePath': '/movie', 
        'httpMethod': 'POST', 
        'extendedRequestId': 'TKcLxHesBcwEMMw=', 
        'requestTime': '15/Feb/2024:05:54:31 +0000', 
        'path': '/dev/movie', 
        'accountId': '533267443935', 
        'protocol': 'HTTP/1.1', 
        'stage': 'dev', 
        'domainPrefix': 'l3xtkc2hlj', 
        'requestTimeEpoch': 1707976471825, 
        'requestId': '563fca96-acc6-4e92-b27f-cbcb8054f0ae', 
        'identity': {
            'cognitoIdentityPoolId': None, 
            'accountId': None, 
            'cognitoIdentityId': None, 
            'caller': None, 
            'sourceIp': '54.86.50.139', 
            'principalOrgId': None, 
            'accessKey': None, 
            'cognitoAuthenticationType': None, 
            'cognitoAuthenticationProvider': None, 
            'userArn': None, 
            'userAgent': 'PostmanRuntime/7.36.3', 
            'user': None
        }, 
        'domainName': 'l3xtkc2hlj.execute-api.ap-south-1.amazonaws.com', 
        'apiId': 'l3xtkc2hlj'
    }, 
    'body': '{\r\n  "httpMethod": "POST",\r\n  "body": [\r\n    {\r\n      "year": 1949,\r\n      "title": "aT3yZf6"\r\n    },\r\n    {\r\n      "year": 1917,\r\n      "title": "9cGQIfv"\r\n    },\r\n    {\r\n      "year": 192,\r\n      "title": "4cHuzIgsKSITL"\r\n    },\r\n    {\r\n      "year": 1229,\r\n      "title": "4cHuzIgsKSITL"\r\n    }\r\n  ]\r\n}', 
    'isBase64Encoded': False
}
