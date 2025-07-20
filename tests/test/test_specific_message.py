#!/usr/bin/env python3
"""
Test Specific Message Flow
Test the exact message that should trigger AI service selection
"""

import requests
import json

BASE_URL = "http://localhost:8002"

def test_specific_message():
    """Test the specific message that should trigger AI service selection"""
    print("🧪 Testing Specific Message Flow")
    print("=" * 50)
    
    # Login first
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "aitest@example.com", "password": "testpass123"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed")
        return
    
    login_data = login_response.json()
    session_token = login_data.get("session_token")
    headers = {"Cookie": f"session_token={session_token}"}
    
    # Test the exact message
    test_message = "Using AI- generate a sales pitch to sell healthy ice cream and send email to slakshanand1105@gmail.com"
    
    print(f"📝 Testing message: {test_message}")
    print(f"   - Contains 'using ai': {'using ai' in test_message.lower()}")
    print(f"   - Contains 'generate': {'generate' in test_message.lower()}")
    print(f"   - Contains 'service:': {'service:' in test_message.lower()}")
    
    response = requests.post(
        f"{BASE_URL}/api/chat/mcpai",
        json={"message": test_message},
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Response received:")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Message: {result.get('message', 'No message')[:100]}...")
        print(f"   Action Required: {result.get('action_required', 'none')}")
        
        if result.get('status') == 'ai_service_selection':
            print("✅ CORRECT: AI service selection triggered")
            ai_services = result.get('ai_service_options', [])
            print(f"   Available services: {[s.get('name') for s in ai_services]}")
        else:
            print(f"❌ UNEXPECTED: Got {result.get('status')} instead of ai_service_selection")
            print(f"   Full response: {json.dumps(result, indent=2)}")
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(f"   Error: {response.text}")

if __name__ == "__main__":
    test_specific_message()
