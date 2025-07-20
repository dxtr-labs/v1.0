#!/usr/bin/env python3
"""
Test Frontend API Response
Check what the frontend API is actually returning
"""

import requests
import json

FRONTEND_URL = "http://localhost:3000"

def test_frontend_api():
    """Test the frontend API directly"""
    print("🧪 Testing Frontend API Response")
    print("=" * 50)
    
    # Step 1: Login
    login_response = requests.post(
        f"{FRONTEND_URL}/api/auth/login",
        json={"email": "aitest@example.com", "password": "testpass123"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    cookies = login_response.cookies
    print("✅ Login successful")
    
    # Step 2: Test the exact message
    test_message = "Using AI- generate a sales pitch to sell healthy ice cream and send email to slakshanand1105@gmail.com"
    
    print(f"\n📝 Testing message: {test_message}")
    
    payload = {
        "message": test_message,
        "agentId": "test-agent",
        "agentConfig": {
            "name": "Sam",
            "role": "Personal Assistant"
        }
    }
    
    # Test frontend API
    response = requests.post(
        f"{FRONTEND_URL}/api/chat/mcpai",
        json=payload,
        cookies=cookies
    )
    
    if response.status_code != 200:
        print(f"❌ Frontend API failed: {response.status_code}")
        print(f"Error: {response.text}")
        return
    
    result = response.json()
    
    print("\n🔍 FRONTEND API RESPONSE:")
    print(f"   Status: {result.get('status', 'not set')}")
    print(f"   Action Required: {result.get('action_required', 'not set')}")
    print(f"   Success: {result.get('success', 'not set')}")
    print(f"   Message: {result.get('message', result.get('response', 'not set'))[:100]}...")
    
    if 'ai_service_options' in result:
        services = result['ai_service_options']
        print(f"   AI Services: {[s.get('name') for s in services]}")
        print("✅ AI Service Selection should appear")
    else:
        print("❌ No AI service options found")
        print(f"   Full response keys: {list(result.keys())}")

if __name__ == "__main__":
    test_frontend_api()
