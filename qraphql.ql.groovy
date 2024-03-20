query comparisonsByUserID($userID: ID!, $nextToken: String, $limit:Int {input_str}) {{
    comparisonsByUserID(userID: $userID, nextToken: $nextToken, sortDirection: ASC, limit: $limit, filter: {filter_str}) {{
    nextToken
    items {{
        id
        gamma1 {{
            id
            title
            description
            level {{
                id
                level
                name
            }}
            createdAt
            updatedAt
        }}
        gamma2 {{
            id
            title
            description
            level {{
                id
                level
                name
            }}
            createdAt
            updatedAt
        }}
        objective {{
            id
            name
            description
        }}
    }}
}}
}}
