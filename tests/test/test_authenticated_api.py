#!/usr/bin/env python3
"""Create test user and get session token for API testing"""

import requests
import json
import uuid

def create_test_user_and_get_token():
    """Create a test user and get authentication token"""
    
    base_url = 'http://localhost:8002'
    
    # Create test user
    test_email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
    test_password = "TestPassword123!"
    
    print(f"🔧 Creating test user: {test_email}")
    
    # Sign up test user
    signup_data = {
        "email": test_email,
        "password": test_password,
        "full_name": "Test User"
    }
    
    try:
        # Sign up
        signup_response = requests.post(f"{base_url}/api/auth/signup", json=signup_data)
        print(f"📝 Signup Status: {signup_response.status_code}")
        
        if signup_response.status_code in [200, 201]:
            print("✅ User created successfully")
        else:
            print(f"⚠️ Signup response: {signup_response.text}")
        
        # Login to get session token
        login_data = {
            "email": test_email,
            "password": test_password
        }
        
        login_response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"🔐 Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            # Extract session token from cookies or response
            session_token = None
            
            # Check cookies first
            if 'session_token' in login_response.cookies:
                session_token = login_response.cookies['session_token']
                print(f"🍪 Got session token from cookies: {session_token[:20]}...")
            
            # Check response JSON
            login_result = login_response.json()
            if 'access_token' in login_result:
                session_token = login_result['access_token']
                print(f"🔑 Got access token from response: {session_token[:20]}...")
            
            return session_token, test_email, test_password
        else:
            print(f"❌ Login failed: {login_response.text}")
            return None, None, None
            
    except Exception as e:
        print(f"💥 Authentication error: {e}")
        return None, None, None

def test_mcp_api_with_auth(session_token):
    """Test the MCP API with authentication"""
    
    if not session_token:
        print("❌ No session token available")
        return None
    
    url = 'http://localhost:8002/api/chat/mcpai'
    headers = {
        'Content-Type': 'application/json',
        'Cookie': f'session_token={session_token}'
    }
    
    data = {
        'user_input': 'draft a sales pitch email for selling the harmless antibiotics for animals and send email to slakshanand1105@gmail.com',
        'agentConfig': {
            'agent_id': 'sales_assistant',
            'name': 'Sales AI Assistant',
            'role': 'Professional Sales Agent'
        },
        'session_id': 'test_session_123'
    }
    
    try:
        print("🧪 Testing authenticated MCP API...")
        response = requests.post(url, json=data, headers=headers, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n✅ AUTHENTICATED API RESPONSE:")
            
            # Check for key fields that frontend expects
            expected_fields = [
                'status', 'hasWorkflowJson', 'hasWorkflowPreview', 
                'done', 'message', 'response', 'workflow_id',
                'automation_type', 'action_required'
            ]
            
            print(f"\n🔍 Checking for expected fields:")
            found_fields = 0
            for field in expected_fields:
                value = result.get(field)
                if value is not None:
                    found_fields += 1
                    status = "✅"
                else:
                    status = "❌"
                print(f"  {status} {field}: {value}")
            
            print(f"\n📈 Found {found_fields}/{len(expected_fields)} expected fields")
            
            # Test if this would trigger frontend automation
            has_workflow = result.get('hasWorkflowJson', False)
            has_preview = result.get('hasWorkflowPreview', False)
            status_ok = result.get('status') in ['completed', 'needs_parameters']
            
            print(f"\n🎯 Frontend Automation Analysis:")
            print(f"  hasWorkflowJson: {has_workflow}")
            print(f"  hasWorkflowPreview: {has_preview}")
            print(f"  status: {result.get('status')}")
            print(f"  Would trigger frontend automation: {has_workflow or has_preview or status_ok}")
            
            if result.get('email_sent'):
                print(f"\n📧 Email Status: SENT ✅")
            
            return result
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"💥 Test Error: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Starting Authentication and API Test...")
    session_token, email, password = create_test_user_and_get_token()
    
    if session_token:
        print(f"\n✅ Authentication successful for {email}")
        test_mcp_api_with_auth(session_token)
    else:
        print("❌ Authentication failed, cannot test API")
