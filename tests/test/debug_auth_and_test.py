#!/usr/bin/env python3
"""Debug authentication response to understand token format"""

import requests
import json

def debug_auth_response():
    """Debug the authentication response format"""
    
    base_url = 'http://localhost:8002'
    
    # Use existing test user or create one
    test_email = "test@example.com"
    test_password = "TestPassword123!"
    
    print(f"🔍 Debugging auth response for: {test_email}")
    
    # Try login
    login_data = {
        "email": test_email,
        "password": test_password
    }
    
    try:
        login_response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"🔐 Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("\n📋 Response Headers:")
            for key, value in login_response.headers.items():
                print(f"  {key}: {value}")
            
            print("\n🍪 Response Cookies:")
            for cookie in login_response.cookies:
                print(f"  {cookie.name}: {cookie.value}")
            
            print("\n📄 Response JSON:")
            try:
                response_data = login_response.json()
                print(json.dumps(response_data, indent=2))
                
                # Try to use whatever token we get
                token = None
                if 'access_token' in response_data:
                    token = response_data['access_token']
                    print(f"\n🔑 Found access_token: {token[:20]}...")
                elif 'token' in response_data:
                    token = response_data['token']
                    print(f"\n🔑 Found token: {token[:20]}...")
                
                # Also check for session token in cookies
                for cookie in login_response.cookies:
                    if 'session' in cookie.name.lower() or 'token' in cookie.name.lower():
                        print(f"\n🍪 Found cookie token: {cookie.name} = {cookie.value[:20]}...")
                        if not token:
                            token = cookie.value
                
                return token
                
            except Exception as json_error:
                print(f"❌ JSON parsing error: {json_error}")
                print(f"Raw response: {login_response.text}")
        else:
            print(f"❌ Login failed: {login_response.text}")
        
    except Exception as e:
        print(f"💥 Auth debug error: {e}")
    
    return None

def test_with_any_method():
    """Try to test the API using various authentication methods"""
    
    # Try to get a token
    token = debug_auth_response()
    
    if not token:
        # Try without authentication (maybe there's a test endpoint)
        print("\n🧪 Trying without authentication...")
        
        url = 'http://localhost:8002/api/chat/mcpai'
        data = {
            'user_input': 'hello, test message',
            'agentConfig': {
                'agent_id': 'test_agent',
                'name': 'Test Agent'
            }
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            print(f"📊 No-auth test Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
        except Exception as e:
            print(f"❌ No-auth test failed: {e}")
    
    else:
        print(f"\n🧪 Testing with token: {token[:20]}...")
        
        # Try different header formats
        test_formats = [
            {'Authorization': f'Bearer {token}'},
            {'Cookie': f'session_token={token}'},
            {'Cookie': f'access_token={token}'},
            {'X-Auth-Token': token}
        ]
        
        for i, headers in enumerate(test_formats):
            print(f"\n🔄 Testing auth format {i+1}: {list(headers.keys())[0]}")
            
            url = 'http://localhost:8002/api/chat/mcpai'
            headers['Content-Type'] = 'application/json'
            
            data = {
                'user_input': 'hello, test message',
                'agentConfig': {
                    'agent_id': 'test_agent',
                    'name': 'Test Agent'
                }
            }
            
            try:
                response = requests.post(url, json=data, headers=headers, timeout=10)
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("  ✅ SUCCESS! This auth format works")
                    result = response.json()
                    
                    # Check for the fields we fixed
                    if 'status' in result:
                        print(f"  status: {result.get('status')}")
                    if 'hasWorkflowJson' in result:
                        print(f"  hasWorkflowJson: {result.get('hasWorkflowJson')}")
                    if 'hasWorkflowPreview' in result:
                        print(f"  hasWorkflowPreview: {result.get('hasWorkflowPreview')}")
                    
                    break
                else:
                    print(f"  ❌ Failed: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"  💥 Error: {e}")

if __name__ == "__main__":
    test_with_any_method()
