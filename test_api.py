import requests
import json

url = "http://localhost:8000/predict"
payload = {
    "title": "App crash",
    "body": "Application crashes when clicking button"
}
headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
