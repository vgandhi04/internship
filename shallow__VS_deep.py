import copy

company = {
  "IT": [
      {"name": "John", "projects": ["projectA", "projectB"]},
      {"name": "Jane", "projects": ["projectC"]}
  ],
  "HR": [
      {"name": "Doe", "projects": ["onboarding", "recruitment"]}
  ]
}

# Using a shallow copy
shallow_company = copy.copy(company)
shallow_company["Tech"] = shallow_company.pop("IT")

# Modifying an employee's projects in the new structure
shallow_company["Tech"][0]["projects"].append("projectD")
print(shallow_company)
print(company)
# Result: ['projectA', 'projectB', 'projectD']
# Problem: The original company structure is affected!

# Resetting our example
company = {
  "IT": [
      {"name": "John", "projects": ["projectA", "projectB"]},
      {"name": "Jane", "projects": ["projectC"]}
  ],
  "HR": [
      {"name": "Doe", "projects": ["onboarding", "recruitment"]}
  ]
}

# Using a deep copy
deep_company = copy.deepcopy(company)
deep_company["Tech"] = deep_company.pop("IT")

# Modifying an employee's projects in the new structure
deep_company["Tech"][0]["projects"].append("projectD")

print(company["IT"][0]["projects"])
# Result: ['projectA', 'projectB']
# Success: The original company structure remains unaffected!