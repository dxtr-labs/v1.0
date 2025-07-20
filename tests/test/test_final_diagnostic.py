import requests
import json

def test_authentication():
    print("🔍 Final Diagnostic Test with Manual Token Handling")

    # Test user credentials
    test_email = "test_mass_user@dxtr-labs.com"
    test_password = "TestPassword123!"

    try:
        print("1. Testing login to get session token...")
        login_response = requests.post(
            "http://localhost:8002/api/auth/login",
            json={
                "email": test_email,
                "password": test_password
            },
            timeout=10
        )
        print(f"   Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            session_token = login_data.get('session_token')
            user_data = login_data.get('user', {})
            user_id = user_data.get('id') if isinstance(user_data, dict) else None
            
            print(f"   ✅ Login successful")
            print(f"   Session token: {session_token[:20] if session_token else 'None'}...")
            print(f"   User ID: {user_id}")
            
            if session_token:
                print("2. Testing MCP API with session_token cookie...")
                mcp_response = requests.post(
                    "http://localhost:8002/api/chat/mcpai",
                    json={"message": "Hello, this is a test message"},
                    headers={"Content-Type": "application/json"},
                    cookies={"session_token": session_token},
                    timeout=15
                )
                print(f"   MCP API (manual cookie) status: {mcp_response.status_code}")
                
                if mcp_response.status_code == 200:
                    result = mcp_response.json()
                    print(f"   ✅ SUCCESS! Status: {result.get('status', 'unknown')}")
                    print(f"   Response: {result.get('response', 'No response')[:100]}...")
                    print(f"   Has workflow: {result.get('hasWorkflowJson', False)}")
                    return session_token  # Return the working token
                else:
                    print(f"   Error: {mcp_response.text[:200]}")
            
            if user_id:
                print("3. Testing MCP API with x-user-id header...")
                mcp_response_header = requests.post(
                    "http://localhost:8002/api/chat/mcpai",
                    json={"message": "Hello, this is a test message with header"},
                    headers={
                        "Content-Type": "application/json",
                        "x-user-id": str(user_id)
                    },
                    timeout=15
                )
                print(f"   MCP API (header) status: {mcp_response_header.status_code}")
                
                if mcp_response_header.status_code == 200:
                    result = mcp_response_header.json()
                    print(f"   ✅ SUCCESS! Status: {result.get('status', 'unknown')}")
                    print(f"   Response: {result.get('response', 'No response')[:100]}...")
                    return user_id  # Return the working user_id
                else:
                    print(f"   Error: {mcp_response_header.text[:200]}")
        else:
            print(f"   Login failed: {login_response.text[:200]}")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")

    print("\nFinal diagnostic complete.")
    return None

if __name__ == "__main__":
    result = test_authentication()
    if result:
        print(f"✅ Authentication working with: {result}")
    else:
        print("❌ Authentication failed")
