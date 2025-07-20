#!/usr/bin/env python3
"""
Simple login test using requests
"""

import requests
import json

def test_login():
    base_url = "http://localhost:8002"
    
    print("🧪 Simple Login Test")
    print("=" * 30)
    
    # Test health check
    try:
        print("1. Health check...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Server healthy: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    
    # Test login with existing user
    print("\n2. Testing login...")
    login_data = {
        "email": "test@autoflow.ai",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Login successful!")
            print(f"   User: {result.get('user', {}).get('email')}")
            print(f"   Credits: {result.get('user', {}).get('credits')}")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_login()
    if success:
        print("\n🎉 Login is working!")
    else:
        print("\n❌ Login test failed")
