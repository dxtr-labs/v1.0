#!/usr/bin/env python3

import requests
import json
from datetime import datetime

# First authenticate to get token
auth_response = requests.post("http://localhost:8002/api/auth/login", json={
    "email": "demo@example.com",
    "password": "password123"
})

if auth_response.status_code != 200:
    print("❌ Authentication failed!")
    print(auth_response.text)
    exit(1)

token = auth_response.json()["access_token"]
print(f"✅ Authenticated! Token: {token[:20]}...")

# Now make the email request with authentication
headers = {"Authorization": f"Bearer {token}"}

response = requests.post(
    "http://localhost:8002/api/chat/mcpai",
    json={"message": "send email to slakshanand1105@gmail.com"},
    headers=headers
)

print(f"📤 Status Code: {response.status_code}")
print(f"📊 Authenticated Response:")
print(json.dumps(response.json(), indent=2))
