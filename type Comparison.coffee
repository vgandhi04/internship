type Comparison
  @model(subscriptions: null)
  @auth(
    rules: [
      {
        allow: private
        provider: iam
        operations: [create, read, update, delete]
      }
      {
        allow: groups
        groups: ["SUPERADMIN"]
        operations: [create, read, update, delete]
      }
      {
        allow: owner
        ownerField: "userID"
        identityClaim: "sub"
        operations: [read]
      }
    ]
  ) {
  id: ID!
  gamma1ID: ID! @index(name: "byGamma1")
  gamma1: Gamma @hasOne(fields: ["gamma1ID"])
  gamma2ID: ID! @index(name: "byGamma2")
  gamma2: Gamma @hasOne(fields: ["gamma2ID"])
  objectiveID: ID! @index(name: "byObjective")
  objective: Objective! @hasOne(fields: ["objectiveID"])
  preference: COMPARISON_PREFERENCE
  userID: ID!
    @index(
      name: "byUser"
      sortKeyFields: ["preference"]
      queryField: "comparisonsByUserID"
    )
  user: User! @hasOne(fields: ["userID"])
  expiry: AWSTimestamp! @ttl
}