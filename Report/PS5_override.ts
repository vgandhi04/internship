// This file is used to override the REST API resources configuration
import { AmplifyApiRestResourceStackTemplate, AmplifyProjectInfo } from '@aws-amplify/cli-extensibility-helper';

export function override(resources: AmplifyApiRestResourceStackTemplate, amplifyProjectInfo: AmplifyProjectInfo) {
    // Change the default CORS response header Access-Control-Allow-Origin from "'*'" to the API's domain
    // resources.restApi.body.paths['/items'].options['x-amazon-apigateway-integration'].responses.default.responseParameters['method.response.header.Access-Control-Allow-Origin'] = { 'Fn::Sub': "'https://${ApiId}.execute-api.${AWS::Region}.amazonaws.com'" };

    // Replace the following with your Function resource name
    const functionResourcename = "apiAuthorizer";
    const functionArnParameter = "FunctionArn";

    // Adding parameter to your Cloud Formation Template for Authorizer function arn
    resources.addCfnParameter(
    {
        type: "String",
        description: "The ARN of an existing Lambda Function to authorize requests",
        default: "NONE",
    },
    functionArnParameter,
    { "Fn::GetAtt": [`function${functionResourcename}`, "Outputs.Arn"], }
    );


    // Create the authorizer using the functionArnParameter parameter defined above
    resources.restApi.addPropertyOverride("Body.securityDefinitions", {
        Lambda: {
        type: "apiKey",
        name: "Authorization",
        in: "header",
        "x-amazon-apigateway-authtype": "oauth2",
        "x-amazon-apigateway-authorizer": {
            type: "token",
            authorizerUri: 
            {
            'Fn::Join': [
                '', 
                [
                "arn:aws:apigateway:",
                { Ref: 'AWS::Region' },
                ":lambda:path/2015-03-31/functions/",
                { Ref: functionArnParameter },
                "/invocations"
                ]
                ],
            },
            authorizerResultTtlInSeconds: 0
            },
        },
    });



    // Adding Resource Based policy to Lambda authorizer function
    resources.addCfnResource(
        {
        type: "AWS::Lambda::Permission",
        properties: {
            Action: "lambda:InvokeFunction",
            FunctionName: {Ref: functionArnParameter},
            Principal: "apigateway.amazonaws.com",
            SourceArn:{
            "Fn::Join": [
                "",
                [
                "arn:aws:execute-api:",
                {
                    "Ref": "AWS::Region"
                },
                ":",
                {
                    "Ref": "AWS::AccountId"
                },
                ":",
                {
                    "Ref": "movie"
                },
                "/*/*"
                ]
                ]
            }
            }
        },
        "LambdaAuthorizerResourceBasedPolicy"
    );


    for (const path in resources.restApi.body.paths) {
        // Add the Authorization header as a parameter to requests
        resources.restApi.addPropertyOverride(
          `Body.paths.${path}.x-amazon-apigateway-any-method.parameters`,
          [
            ...resources.restApi.body.paths[path]["x-amazon-apigateway-any-method"]
              .parameters,
            {
              name: "Authorization",
              in: "header",
              required: false,
              type: "string",
            },
          ]
        );
        // Use your new Lambda authorizer for security
        resources.restApi.addPropertyOverride(
          `Body.paths.${path}.x-amazon-apigateway-any-method.security`,
          [ { Lambda: [], }, ]
        );
    }
}