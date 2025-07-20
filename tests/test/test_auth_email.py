#!/usr/bin/env python3

# Test email automation with proper authentication
import requests
import json

def test_authenticated_email():
    """Test email automation with proper signup/login flow"""
    print("🧪 Authenticated Email Test")
    print("=" * 35)
    
    base_url = "http://localhost:8002"
    email_target = "slakshanand1105@gmail.com"
    
    try:
        # Step 1: Signup
        print("1️⃣ Creating test user...")
        signup_data = {
            "username": f"test_email_user_{int(__import__('time').time())}",
            "email": f"test{int(__import__('time').time())}@example.com",
            "password": "testpass123"
        }
        
        signup_response = requests.post(f"{base_url}/api/auth/signup", json=signup_data, timeout=10)
        if signup_response.status_code == 200:
            print("✅ Signup successful")
            signup_result = signup_response.json()
            user_email = signup_data["email"]
        else:
            print(f"❌ Signup failed: {signup_response.status_code}")
            print(signup_response.text)
            return False
        
        # Step 2: Login
        print("2️⃣ Logging in...")
        login_data = {
            "email": user_email,
            "password": "testpass123"
        }
        
        login_response = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=10)
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return False
        
        login_result = login_response.json()
        user_id = login_result.get("user", {}).get("user_id")
        session_token = login_result.get("session_token")
        
        print(f"✅ Login successful: {user_id}")
        
        # Step 3: Test email automation
        print("3️⃣ Testing email automation...")
        
        headers = {
            "Content-Type": "application/json",
            "x-user-id": user_id,
            "Cookie": f"session_token={session_token}"
        }
        
        payload = {
            "message": f"draft a sales pitch and send email to {email_target}",
            "agent_id": "Sam - Personal Assistant",  # Use the actual agent name
            "conversation_id": "test_conv_123"
        }
        
        api_response = requests.post(f"{base_url}/api/chat/mcpai", json=payload, headers=headers, timeout=60)
        
        print(f"📊 API Response status: {api_response.status_code}")
        
        if api_response.status_code == 200:
            result = api_response.json()
            
            print("📋 API Response Details:")
            print(f"  Status: {result.get('status')}")
            print(f"  Success: {result.get('success')}")
            print(f"  Email sent: {result.get('email_sent')}")
            print(f"  Workflow ID: {result.get('workflow_id')}")
            print(f"  Message: {result.get('message', 'No message')[:100]}...")
            
            if result.get('email_sent') is True:
                print("🎉 SUCCESS: API reports email was sent!")
                return True
            elif result.get('email_sent') is None:
                print("⚠️ PARTIAL: email_sent is null")
                print(f"Full response: {json.dumps(result, indent=2)}")
                return False
            else:
                print("❌ FAILED: email_sent is false")
                return False
        else:
            print(f"❌ API Error {api_response.status_code}: {api_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_authenticated_email()
    if success:
        print("\n✅ Authenticated email test successful!")
    else:
        print("\n❌ Authenticated email test failed!")
