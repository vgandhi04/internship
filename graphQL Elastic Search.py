import json
# from amplify.api.graphql import GraphQLResponse, get_graphql_client
# from amplify.api.exceptions import GraphQLError
# import AppSyncHelper
# from gql import gql

def handler(event, context):
    print('received event:')
    print(event['body'])
    event1 = json.loads(event['body'])
    query = event1.get("query", "")
    year = event1.get("year", "")
    print("Q - ", query)
    print("Y - ", year)

    # client = get_graphql_client(
    #     graphql_endpoint="https://dckqv6edhbatdmegyqx6w7id6i.appsync-api.ap-south-1.amazonaws.com/graphql",
    #     aws_region="ap-south-1"
    # )
    
    # # Define the search query
    # search_query = """
    #     query searchMovies($filter: SearchableMovieFilterInput) {
    #         searchMovies(filter: $filter) {
    #             items {
    #                 year
    #                 title
    #                 organizationID
    #                 organization {
    #                     id
    #                     name
    #                 }
    #                 admin
    #                 team
    #             }
    #         }
    #     }
    # """
    
    # def search_movies(search_term):
    #     try:
    #         result = client.execute_query(
    #             query=search_query,
    #             variables={
    #                 "filter": {
    #                     "title": {
    #                         "match": search_term
    #                     }
    #                 }
    #             },
    #         )
    #         print("RESult - ", result.data)
    #         return result.data["searchMovies"]["items"]
    #     except GraphQLError as e:
    #         print(f"Error: {e}")
    #         return []
    # search_results = search_movies("m1")
    # for movie in search_results:
    #     print(f"Title: {movie['title']}, Year: {movie['year']}, Organization: {movie['organization']['name']}")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from your new Amplify Python lambda!')
    }