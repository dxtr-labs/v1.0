#!/usr/bin/env python3

import requests
import json

# First try to create a user
signup_response = requests.post("http://localhost:8002/api/auth/signup", json={
    "email": "test@example.com", 
    "password": "password123",
    "full_name": "Test User"
})

print(f"Signup: {signup_response.status_code}")
if signup_response.status_code != 200:
    print(signup_response.text)

# Now try to authenticate
auth_response = requests.post("http://localhost:8002/api/auth/login", json={
    "email": "test@example.com",
    "password": "password123"
})

print(f"Login: {auth_response.status_code}")
if auth_response.status_code != 200:
    print("❌ Authentication failed!")
    print(auth_response.text)
    exit(1)

login_data = auth_response.json()
print(f"Login response: {login_data}")

# Extract the correct token field
session_token = login_data.get("session_token")
user_id = login_data.get("user", {}).get("user_id")
if not session_token:
    print("❌ No session token found in login response")
    exit(1)

print(f"✅ Authenticated! Session Token: {session_token[:20]}...")
print(f"👤 User ID: {user_id}")

# Now make the email request with authentication using cookies and headers
cookies = {"session_token": session_token}
headers = {"x-user-id": user_id}

print("🚀 Making authenticated email request...")
response = requests.post(
    "http://localhost:8002/api/chat/mcpai",
    json={"message": "send email to slakshanand1105@gmail.com"},
    cookies=cookies,
    headers=headers
)

print(f"📤 Status Code: {response.status_code}")
print(f"📊 Authenticated Response:")
print(json.dumps(response.json(), indent=2))
