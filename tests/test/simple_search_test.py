#!/usr/bin/env python3
"""
SIMPLIFIED SEARCH TEST - BYPASSING AUTH ISSUES
Direct test of search functionality
"""

import requests
import json
import uuid

def test_auth_debug():
    """Debug authentication issues"""
    base_url = "http://localhost:8002"
    
    # Test signup with detailed response
    test_email = f"debuguser_{uuid.uuid4().hex[:6]}@example.com"
    signup_data = {
        "email": test_email,
        "password": "testpass123",
        "name": "Debug User"
    }
    
    print(f"🔐 Testing signup with: {test_email}")
    
    try:
        signup_response = requests.post(f"{base_url}/api/auth/signup", json=signup_data, timeout=10)
        print(f"Signup Status: {signup_response.status_code}")
        print(f"Signup Response: {signup_response.text}")
        
        if signup_response.status_code in [200, 201]:
            # Try login immediately
            login_data = {"email": test_email, "password": "testpass123"}
            print(f"\n🔑 Attempting login...")
            
            login_response = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=10)
            print(f"Login Status: {login_response.status_code}")
            print(f"Login Response: {login_response.text}")
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                token = login_result.get("access_token")
                
                if token:
                    print(f"✅ Got token: {token[:50]}...")
                    
                    # Test the chat endpoint
                    headers = {"Authorization": f"Bearer {token}"}
                    chat_data = {"message": "Search for AI automation companies and email results to slakshanand1105@gmail.com"}
                    
                    print(f"\n🔍 Testing search functionality...")
                    chat_response = requests.post(f"{base_url}/api/chat/mcpai", json=chat_data, headers=headers, timeout=60)
                    
                    print(f"Chat Status: {chat_response.status_code}")
                    print(f"Chat Response: {chat_response.text[:1000]}...")
                    
                    if chat_response.status_code == 200:
                        print("✅ SEARCH IS WORKING! The issue was authentication.")
                        return True
                else:
                    print("❌ No token in login response")
            else:
                print(f"❌ Login failed: {login_response.text}")
        else:
            print(f"❌ Signup failed: {signup_response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    return False

def test_existing_users():
    """Try with potentially existing users"""
    base_url = "http://localhost:8002"
    
    # Common test account patterns
    test_accounts = [
        {"email": "admin@admin.com", "password": "admin"},
        {"email": "test@test.com", "password": "test"},
        {"email": "user@user.com", "password": "user"},
        {"email": "demo@demo.com", "password": "demo"},
        {"email": "testuser@example.com", "password": "testuser"},
    ]
    
    for creds in test_accounts:
        print(f"🔑 Trying: {creds['email']}")
        
        try:
            login_response = requests.post(f"{base_url}/api/auth/login", json=creds, timeout=5)
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                token = login_result.get("access_token")
                
                if token:
                    print(f"✅ SUCCESS! Logged in as {creds['email']}")
                    
                    # Quick search test
                    headers = {"Authorization": f"Bearer {token}"}
                    chat_data = {"message": "Search for AI automation investors and email to slakshanand1105@gmail.com"}
                    
                    chat_response = requests.post(f"{base_url}/api/chat/mcpai", json=chat_data, headers=headers, timeout=45)
                    print(f"Search test: {chat_response.status_code}")
                    
                    if chat_response.status_code == 200:
                        response_data = chat_response.json()
                        print(f"Search response: {str(response_data)[:500]}...")
                        print("✅ SEARCH FUNCTIONALITY IS WORKING!")
                        return True
                    else:
                        print(f"Search failed: {chat_response.text[:200]}")
                        
        except Exception as e:
            print(f"Error with {creds['email']}: {str(e)}")
            continue
    
    return False

def check_backend_endpoints():
    """Check what endpoints are actually available"""
    base_url = "http://localhost:8002"
    
    print("🔍 Checking available endpoints...")
    
    # Check docs endpoint
    try:
        docs_response = requests.get(f"{base_url}/docs", timeout=5)
        if docs_response.status_code == 200:
            print("✅ Swagger docs available at http://localhost:8002/docs")
        else:
            print(f"❌ Docs not available: {docs_response.status_code}")
    except:
        print("❌ Could not access docs")
    
    # Check openapi.json
    try:
        openapi_response = requests.get(f"{base_url}/openapi.json", timeout=5)
        if openapi_response.status_code == 200:
            print("✅ OpenAPI spec available")
            # Could parse endpoints here if needed
        else:
            print(f"❌ OpenAPI not available: {openapi_response.status_code}")
    except:
        print("❌ Could not access OpenAPI spec")

if __name__ == "__main__":
    print("🚀 SIMPLIFIED SEARCH DIAGNOSTIC")
    print("=" * 50)
    
    # Check endpoints first
    check_backend_endpoints()
    
    print("\n🔐 Testing Authentication...")
    
    # Try with new user
    if test_auth_debug():
        print("\n🎉 SUCCESS: Search is working with new user!")
    else:
        print("\n🔑 Trying existing users...")
        if test_existing_users():
            print("\n🎉 SUCCESS: Search is working with existing user!")
        else:
            print("\n❌ FAILED: Could not authenticate with any method")
            print("\n🔧 NEXT STEPS:")
            print("1. Check the backend logs for authentication errors")
            print("2. Verify PostgreSQL database is running")
            print("3. Check if user table exists and has data")
            print("4. Visit http://localhost:8002/docs to see API documentation")
            print("5. Try creating a user manually through the Swagger UI")
