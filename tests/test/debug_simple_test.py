#!/usr/bin/env python3

import requests
import json

# Test with proper authentication
signup_response = requests.post("http://localhost:8002/api/auth/signup", json={
    "email": "debug@example.com", 
    "password": "password123",
    "full_name": "Debug User"
})

auth_response = requests.post("http://localhost:8002/api/auth/login", json={
    "email": "debug@example.com",
    "password": "password123"
})

if auth_response.status_code == 200:
    login_data = auth_response.json()
    session_token = login_data.get("session_token")
    user_id = login_data.get("user", {}).get("user_id")
    
    cookies = {"session_token": session_token}
    headers = {"x-user-id": user_id}
    
    print("🚀 Testing with simple email request...")
    response = requests.post(
        "http://localhost:8002/api/chat/mcpai",
        json={"message": "email test@example.com"},
        cookies=cookies,
        headers=headers
    )
    
    result = response.json()
    print(f"📊 Response: workflow_id={result.get('workflow_id')}")
    print(f"📊 hasWorkflowJson: {result.get('hasWorkflowJson')}")
    print(f"📊 email_sent: {result.get('email_sent')}")
    print(f"📊 automation_type: {result.get('automation_type')}")
    
else:
    print("❌ Authentication failed")
    print(auth_response.text)
