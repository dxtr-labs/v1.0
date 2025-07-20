#!/usr/bin/env python3
"""
Login Debug Test
"""

import requests
import json

def test_login_flow():
    base_url = "http://localhost:8002"
    
    print("🔍 Testing Login Flow Debug")
    print("=" * 50)
    
    # Test 1: Check if we can reach the server
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        print(f"✅ Server reachable: {response.status_code}")
    except Exception as e:
        print(f"❌ Server unreachable: {e}")
        return
    
    # Test 2: Try login with test credentials
    print("\n🔑 Testing Login")
    login_data = {
        "email": "test@test.com",
        "password": "test123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Login successful!")
            print(f"Session Token: {result.get('session_token', 'Not provided')}")
            return result.get('session_token')
        else:
            print(f"❌ Login failed")
            
    except Exception as e:
        print(f"❌ Login request failed: {e}")
    
    # Test 3: Try signup first then login
    print("\n📝 Testing Signup then Login")
    signup_data = {
        "email": "debug@test.com",
        "password": "debug123",
        "first_name": "Debug", 
        "last_name": "User",
        "username": "debuguser"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/signup",
            json=signup_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Signup Status: {response.status_code}")
        print(f"Signup Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Signup successful!")
            
            # Now try login with these credentials
            login_data = {
                "email": "debug@test.com",
                "password": "debug123"
            }
            
            login_response = requests.post(
                f"{base_url}/api/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"Login after signup Status: {login_response.status_code}")
            print(f"Login after signup Response: {login_response.text}")
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                print("✅ Login after signup successful!")
                return login_result.get('session_token')
        
    except Exception as e:
        print(f"❌ Signup/Login test failed: {e}")

if __name__ == "__main__":
    test_login_flow()
