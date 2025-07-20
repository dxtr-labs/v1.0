#!/usr/bin/env python3
"""
Test Authentication Flow
Verify that the frontend properly passes authentication to backend
"""

import requests
import json

BASE_URL = "http://localhost:8002"
FRONTEND_URL = "http://localhost:3000"

def test_backend_auth():
    """Test direct backend authentication"""
    print("🔐 Testing backend authentication...")
    
    # Login via backend
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "aitest@example.com", "password": "testpass123"}
    )
    
    if login_response.status_code == 200:
        login_data = login_response.json()
        session_token = login_data.get("session_token")
        user_id = login_data.get("user", {}).get("user_id")
        
        print(f"✅ Backend login successful")
        print(f"   Session Token: {session_token[:20]}...")
        print(f"   User ID: {user_id}")
        
        # Test authenticated endpoint
        headers = {"Cookie": f"session_token={session_token}"}
        
        test_response = requests.post(
            f"{BASE_URL}/api/chat/mcpai",
            json={"message": "Hello Sam"},
            headers=headers
        )
        
        if test_response.status_code == 200:
            print("✅ Backend authenticated request successful")
            return True
        else:
            print(f"❌ Backend authenticated request failed: {test_response.status_code}")
            print(f"   Response: {test_response.text}")
            return False
    else:
        print(f"❌ Backend login failed: {login_response.status_code}")
        return False

def test_frontend_auth():
    """Test frontend authentication flow"""
    print("\n🌐 Testing frontend authentication...")
    
    # Login via frontend
    login_response = requests.post(
        f"{FRONTEND_URL}/api/auth/login",
        json={"email": "aitest@example.com", "password": "testpass123"}
    )
    
    if login_response.status_code == 200:
        # Get cookies from response
        cookies = login_response.cookies
        session_cookie = cookies.get('session_token')
        
        if session_cookie:
            print(f"✅ Frontend login successful - Session cookie set")
            
            # Test authenticated frontend API
            test_response = requests.post(
                f"{FRONTEND_URL}/api/chat/mcpai",
                json={
                    "message": "Hello Sam",
                    "agentId": "test-agent",
                    "agentConfig": {
                        "name": "Test Agent",
                        "role": "assistant"
                    }
                },
                cookies=cookies
            )
            
            if test_response.status_code == 200:
                print("✅ Frontend authenticated request successful")
                return True
            else:
                print(f"❌ Frontend authenticated request failed: {test_response.status_code}")
                print(f"   Response: {test_response.text}")
                return False
        else:
            print("❌ No session cookie received from frontend")
            return False
    else:
        print(f"❌ Frontend login failed: {login_response.status_code}")
        return False

if __name__ == "__main__":
    print("🧪 AUTHENTICATION FLOW TEST")
    print("=" * 50)
    
    backend_auth = test_backend_auth()
    frontend_auth = test_frontend_auth()
    
    print("\n" + "=" * 50)
    print("📊 AUTHENTICATION TEST RESULTS")
    print(f"Backend Auth: {'✅ PASS' if backend_auth else '❌ FAIL'}")
    print(f"Frontend Auth: {'✅ PASS' if frontend_auth else '❌ FAIL'}")
    
    if backend_auth and frontend_auth:
        print("\n🎉 Authentication is working correctly!")
    else:
        print("\n🔧 Authentication needs fixing.")
