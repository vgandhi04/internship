# Import the urllib.parse module
import urllib.parse as urlparse1

# Sample URL with tokens in the fragment part
url = "https://example.com/#id_token=eyJraWQiOiJGOFNid09aeWRsXC92cnM1QXgzS3BiNWFqdHM5cmxaM0VMa0RDUkdjMDRxZz0iLCJhbGciOiJSUzI1NiJ9.eyJhdF9oYXNoIjoibkd3bTdhZmFlRFZsa3FTcERLWDMwQSIsInN1YiI6IjllNWFiZDU4LTViMTUtNDIxNS1iMGY5LWVkNTlkYWM3OWYxZSIsImNvZ25pdG86Z3JvdXBzIjpbImQ2OGY2NTMwLTQ4NGItNGI5Ni1iOTYwLTliYzVhNzQ2ZDZjMyIsImQ2OGY2NTMwLTQ4NGItNGI5Ni1iOTYwLTliYzVhNzQ2ZDZjMy1BZG1pbiJdLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwicGV0X3ByZWZlcmVuY2UiOiJkb2dzIiwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLmFwLXNvdXRoLTEuYW1hem9uYXdzLmNvbVwvYXAtc291dGgtMV9wZTRFY0IwSEQiLCJjb2duaXRvOnVzZXJuYW1lIjoidGVzdDIzNCIsImF1ZCI6IjQxZTduNnRwdHZrMGdpYmU4Yjk1N3FmcDJhIiwiZXZlbnRfaWQiOiIyNzU5YTMxOS0xMzcwLTQ0OWQtODllMi1mNThhMzUwNWYwYjUiLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTcxNDAyNzcwMiwiZXhwIjoxNzE0MDMxMzAyLCJpYXQiOjE3MTQwMjc3MDMsImp0aSI6IjNhMTE0NjJmLWU3ODktNGIxMi1iZjRkLTU0MWQ2NjJjYzQ3NiIsImVtYWlsIjoia3VydGphbmUxODA3QGdtYWlsLmNvbSJ9.ooseKfJvAKuYl1e8o5duiW0rSk0wXxzfJcHkdyY7oSOHcTjkwFtyRDZmKq1KQE0nVo4z8J4exUCIMgVsRCJNRbzjHfcdBWD8aVj5QMDwDuEACVQRcALzRHbdRWPZXrJPrWs6e5LfA882sYCgOjUaIlDowgPpDgP18KXHe7nULnb6mWsYIC9MUvDVgDlLVm--7CtUxaNY6M3z1SumUM0d0ZyUnUb7ZnyFxoUoOOorBS06JNzt-pvpOOC67sSe__kdeObb3LV-4uV2xNstRuf98KcIaEhd89U3d2bxin0I_E1q_DNbfURNiW3KMbg25wPDlSulfipezY2V3rEylgiTQw&access_token=eyJraWQiOiJ2TjlqWDBcL1ViZjVDZlAzazZZRHdwSTJIN0NmRStHS1JVdDhTVENzclk5MD0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI5ZTVhYmQ1OC01YjE1LTQyMTUtYjBmOS1lZDU5ZGFjNzlmMWUiLCJjb2duaXRvOmdyb3VwcyI6WyJkNjhmNjUzMC00ODRiLTRiOTYtYjk2MC05YmM1YTc0NmQ2YzMiLCJkNjhmNjUzMC00ODRiLTRiOTYtYjk2MC05YmM1YTc0NmQ2YzMtQWRtaW4iXSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLmFwLXNvdXRoLTEuYW1hem9uYXdzLmNvbVwvYXAtc291dGgtMV9wZTRFY0IwSEQiLCJ2ZXJzaW9uIjoyLCJjbGllbnRfaWQiOiI0MWU3bjZ0cHR2azBnaWJlOGI5NTdxZnAyYSIsImV2ZW50X2lkIjoiMjc1OWEzMTktMTM3MC00NDlkLTg5ZTItZjU4YTM1MDVmMGI1IiwidG9rZW5fdXNlIjoiYWNjZXNzIiwic2NvcGUiOiJwaG9uZSBvcGVuaWQgZW1haWwiLCJhdXRoX3RpbWUiOjE3MTQwMjc3MDIsImV4cCI6MTcxNDAzMTMwMiwiaWF0IjoxNzE0MDI3NzAzLCJqdGkiOiJjMWE2YWZkZi1iYTFhLTRlZDgtYjNkMC02MjJjMjIxOTlmZGUiLCJ1c2VybmFtZSI6InRlc3QyMzQifQ.dj6vCPgDj8A2hZanIChhIP0oAYvHdrfla3fWzJc_oq1QDbJYDrXljQPpXZhxUMzeCehaOOChxS6hVDT5k1ZcZCTJ7HrGlhq4REz0BJcItYZjWro33KxCcun8NAKZ3K9iSTPv5LUL8RHGXSOq5-LH6tQSrgsJ14d3GmBnKLtb59YlhVMNNcunQHAzon2btFp4mxzcxOnnPyRWUnG59rWzQURITOzOOHZ4u0t_CzJBwEtlAA5HM5tgIImc16veJIvwufVHKektdgOxOhUvBqux1-76WXp6NTUh_ojpCdwVQHeLOENkv3w6E4ooQMC2Ju3Kui0xJstzubrFEZTqZ1fjdg&expires_in=3600&token_type=Bearer"

# Parse the URL
parsed_url = urlparse1.urlparse(url)
# print("parsed - ", parsed_url)
# Extract parameters from the fragment part
fragment_params = urlparse1.parse_qs(parsed_url.fragment)
# print("fragment_params - ", fragment_params)
# Retrieve values for 'id_token' and 'access_token'
id_token = fragment_params.get('id_token', [None])[0]
access_token = fragment_params.get('access_token', [None])[0]

# Print the extracted tokens
print("id_token:", id_token)
print("access_token:", access_token)
