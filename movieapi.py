import requests

url = "https://api.themoviedb.org/3/authentication"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJiOThlZjdiYzY4OGE2NGFiMjI4NDc5ZGY3ZDM4NmU1NCIsInN1YiI6IjY2MTRkNjllMDQ4NjM4MDE3YzFiZTVmYyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.OvAVRxkdE4H2nv4CpQfBuf1bbQHcrwyVAzlBShsYC6Y"
}

response = requests.get(url, headers=headers)

print(response.text)