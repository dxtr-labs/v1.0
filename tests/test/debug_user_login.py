#!/usr/bin/env python3
"""
Test login with the user's existing account
"""

import requests
import json

def test_user_login():
    """Test login with the user's existing credentials"""
    
    frontend_url = "http://localhost:3002"
    
    # Login with the user's existing account
    login_data = {
        "email": "suguanu24@gmail.com",
        "password": "Lakshu11042005$"
    }
    
    print("🧪 Testing User Login...")
    print(f"📤 Login data: {json.dumps(login_data, indent=2)}")
    
    try:
        response = requests.post(f"{frontend_url}/api/auth/login", json=login_data, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ LOGIN SUCCESSFUL!")
            print(f"📋 User data: {json.dumps(result, indent=2)}")
        elif response.status_code == 401:
            result = response.json()
            print("❌ LOGIN FAILED - Invalid credentials")
            print(f"📋 Error: {json.dumps(result, indent=2)}")
        else:
            try:
                result = response.json()
                print(f"❌ LOGIN FAILED - {response.status_code}")
                print(f"📋 Response: {json.dumps(result, indent=2)}")
            except:
                print(f"📋 Raw Response: {response.text}")
                    
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_user_login()
