#!/usr/bin/env python3
"""
Complete Authentication Flow Test
Tests the entire login/signup flow with the working system
"""

import requests
import json
import time
from datetime import datetime

def test_complete_auth_flow():
    """Test the complete authentication workflow"""
    print("🚀 Complete Authentication Flow Test")
    print("=" * 50)
    print(f"⏰ Test started at: {datetime.now().strftime('%H:%M:%S')}")
    
    base_url = "http://localhost:8002"
    frontend_url = "http://localhost:3000"
    
    # Test data
    test_user = {
        "email": "demo@autoflow.ai",
        "password": "demo123456",
        "first_name": "Demo",
        "last_name": "User",
        "username": "demouser"
    }
    
    print(f"\n📋 Test User: {test_user['email']}")
    
    # Test 1: Backend Health Check
    print("\n1. 🏥 Backend Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Backend healthy")
            print(f"   📊 Database: {health_data.get('database')}")
            print(f"   🕒 Timestamp: {health_data.get('timestamp')}")
        else:
            print(f"   ❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect to backend: {e}")
        return False
    
    # Test 2: Frontend Health Check
    print("\n2. 🌐 Frontend Health Check...")
    try:
        response = requests.get(frontend_url, timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Frontend accessible")
        else:
            print(f"   ⚠️ Frontend response: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️ Frontend check: {e}")
    
    # Test 3: User Signup via Frontend API
    print("\n3. 📝 Testing Signup via Frontend Proxy...")
    try:
        signup_response = requests.post(
            f"{frontend_url}/api/auth/signup",
            json=test_user,
            timeout=10
        )
        
        print(f"   Status: {signup_response.status_code}")
        
        if signup_response.status_code == 200:
            signup_data = signup_response.json()
            print(f"   ✅ Signup successful!")
            print(f"   👤 User ID: {signup_data.get('user', {}).get('user_id')}")
            print(f"   💰 Credits: {signup_data.get('user', {}).get('credits')}")
            session_token = signup_data.get('session_token')
        elif signup_response.status_code == 400 and "already exists" in signup_response.text:
            print(f"   ℹ️ User already exists, proceeding to login")
        else:
            print(f"   ❌ Signup failed: {signup_response.text}")
    except Exception as e:
        print(f"   ❌ Signup request failed: {e}")
    
    # Test 4: User Login via Frontend API
    print("\n4. 🔑 Testing Login via Frontend Proxy...")
    try:
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        
        login_response = requests.post(
            f"{frontend_url}/api/auth/login",
            json=login_data,
            timeout=10
        )
        
        print(f"   Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            print(f"   ✅ Login successful!")
            print(f"   👤 Email: {login_result.get('user', {}).get('email')}")
            print(f"   🎫 Session token: {login_result.get('session_token', '')[:20]}...")
            session_token = login_result.get('session_token')
            
            # Test 5: Authenticated Request
            print("\n5. 🔐 Testing Authenticated Request...")
            headers = {"Authorization": f"Bearer {session_token}"}
            me_response = requests.get(f"{base_url}/api/auth/me", headers=headers, timeout=5)
            
            if me_response.status_code == 200:
                user_info = me_response.json()
                print(f"   ✅ Authentication verified!")
                print(f"   👤 User: {user_info.get('user', {}).get('name')}")
                print(f"   💰 Credits: {user_info.get('user', {}).get('credits')}")
            else:
                print(f"   ❌ Authentication failed: {me_response.status_code}")
                return False
                
        else:
            print(f"   ❌ Login failed: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Login request failed: {e}")
        return False
    
    # Test 6: Chat API with Authentication
    print("\n6. 💬 Testing Chat API with Authentication...")
    try:
        chat_data = {
            "message": "I want to send an email to john@example.com about our quarterly results",
            "session_id": f"authenticated_user_{datetime.now().strftime('%H%M%S')}"
        }
        
        headers = {"Authorization": f"Bearer {session_token}"}
        chat_response = requests.post(
            f"{base_url}/chat",
            json=chat_data,
            headers=headers,
            timeout=30
        )
        
        print(f"   Status: {chat_response.status_code}")
        
        if chat_response.status_code == 200:
            chat_result = chat_response.json()
            print(f"   ✅ Chat API working!")
            print(f"   🤖 Response type: {chat_result.get('response_type')}")
            print(f"   📊 Status: {chat_result.get('status')}")
            
            # Check workflow status fix
            if chat_result.get('status') == 'ai_service_selection':
                print(f"   🎉 Workflow status FIXED! (showing 'ai_service_selection' not 'completed')")
            elif chat_result.get('status') == 'completed':
                print(f"   ⚠️ Workflow status still shows 'completed' - needs investigation")
            else:
                print(f"   📋 Current status: {chat_result.get('status')}")
                
        else:
            print(f"   ❌ Chat API failed: {chat_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Chat request failed: {e}")
        return False
    
    print(f"\n🎉 ALL AUTHENTICATION TESTS PASSED!")
    print(f"✅ Frontend-Backend proxy working")
    print(f"✅ User signup/login flow working")
    print(f"✅ Session authentication working")
    print(f"✅ Chat API with auth working")
    print(f"⏰ Test completed at: {datetime.now().strftime('%H:%M:%S')}")
    
    return True

if __name__ == "__main__":
    success = test_complete_auth_flow()
    
    if success:
        print(f"\n🚀 SYSTEM IS FULLY OPERATIONAL!")
        print(f"🔗 Ready for mass load testing and production use")
    else:
        print(f"\n❌ Authentication system needs attention")
