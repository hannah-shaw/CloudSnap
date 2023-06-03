
import requests

url = 'https://upt0on4bnl.execute-api.us-east-1.amazonaws.com/czystage1/upload'
response = requests.get(url)

print(response.text)