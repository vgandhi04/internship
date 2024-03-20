import json
import random

# Function to generate random year
def generate_random_year():
    return random.randint(1900, 2023)

# Function to generate random title
def generate_random_title(length):
    # Define characters allowed in titles
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
    return ''.join(random.choice(characters) for _ in range(length))

# Generate data
data = []
for _ in range(1000):
    data.append({
        "year": generate_random_year(),
        "title": generate_random_title(random.randint(5, 20))
    })

# Write data to JSON file
with open("data.json", "w") as f:
    json.dump(data, f, indent=4)

print("JSON file created successfully!")
