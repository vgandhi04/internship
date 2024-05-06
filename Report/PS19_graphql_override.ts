import {
  AmplifyApiGraphQlResourceStackTemplate,
  AmplifyProjectInfo,
} from "@aws-amplify/cli-extensibility-helper";

export function override(
  resources: AmplifyApiGraphQlResourceStackTemplate,
  amplifyProjectInfo: AmplifyProjectInfo
) {
  resources.opensearch.OpenSearchDomain.accessPolicies = {
    Version: "2012-10-17",
    Statement: [
      {
        Effect: "Allow",
        Principal: {
          AWS: ["arn:aws:iam::533267443935:root"],
        },
        Action: ["es:*"],
        Resource:
          "arn:aws:es:ap-south-1:533267443935:domain/amplify-opense-x35r0x76s3wi/*",
      },
    ],
  };
}
