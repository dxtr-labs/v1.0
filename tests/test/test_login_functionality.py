#!/usr/bin/env python3
"""
Test login functionality directly with HTTP requests
"""

import asyncio
import json
import aiohttp
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_login_api():
    """Test the login API endpoints"""
    base_url = "http://localhost:8002"
    
    print("🧪 Testing Login API...")
    
    # Test data
    test_email = "test@autoflow.ai"
    test_password = "testpass123"
    
    async with aiohttp.ClientSession() as session:
        
        # Test health check first
        try:
            print("\n1. Testing health check...")
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"✅ Health check: {health_data}")
                else:
                    print(f"❌ Health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            print("⚠️ Make sure the server is running on localhost:8002")
            return False
        
        # Test signup
        print("\n2. Testing signup...")
        signup_data = {
            "email": test_email,
            "password": test_password,
            "first_name": "Test",
            "last_name": "User",
            "username": "testuser"
        }
        
        try:
            async with session.post(f"{base_url}/api/auth/signup", json=signup_data) as response:
                signup_result = await response.json()
                if response.status == 200:
                    print(f"✅ Signup successful: {signup_result.get('user', {}).get('email')}")
                    session_token = signup_result.get('session_token')
                elif response.status == 400 and "already exists" in signup_result.get('error', ''):
                    print(f"ℹ️ User already exists, proceeding to login")
                else:
                    print(f"❌ Signup failed: {signup_result}")
        except Exception as e:
            print(f"❌ Signup request failed: {e}")
        
        # Test login
        print("\n3. Testing login...")
        login_data = {
            "email": test_email,
            "password": test_password
        }
        
        try:
            async with session.post(f"{base_url}/api/auth/login", json=login_data) as response:
                login_result = await response.json()
                if response.status == 200:
                    print(f"✅ Login successful: {login_result.get('user', {}).get('email')}")
                    session_token = login_result.get('session_token')
                    print(f"🔑 Session token: {session_token[:20]}...")
                    
                    # Test authenticated endpoint
                    print("\n4. Testing authenticated endpoint...")
                    headers = {"Authorization": f"Bearer {session_token}"}
                    async with session.get(f"{base_url}/api/auth/me", headers=headers) as auth_response:
                        if auth_response.status == 200:
                            user_info = await auth_response.json()
                            print(f"✅ Authenticated user info: {user_info.get('user', {}).get('email')}")
                            return True
                        else:
                            print(f"❌ Authentication failed: {auth_response.status}")
                            return False
                else:
                    print(f"❌ Login failed: {login_result}")
                    return False
        except Exception as e:
            print(f"❌ Login request failed: {e}")
            return False

if __name__ == "__main__":
    print("🚀 Login Functionality Test")
    print("=" * 50)
    
    # Run the test
    result = asyncio.run(test_login_api())
    
    if result:
        print("\n🎉 All login tests passed!")
        print("✅ Authentication system is working correctly")
    else:
        print("\n❌ Login tests failed")
        print("⚠️ Check server status and try again")
