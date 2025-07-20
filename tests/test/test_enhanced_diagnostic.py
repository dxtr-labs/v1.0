import requests
import json

print("🔍 Enhanced Diagnostic Test with Cookie Inspection")

# Create session for authentication
session = requests.Session()

# Test user credentials
test_email = "test_mass_user@dxtr-labs.com"
test_password = "TestPassword123!"

try:
    print("1. Testing login with cookie inspection...")
    login_response = session.post(
        "http://localhost:8002/api/auth/login",
        json={
            "email": test_email,
            "password": test_password
        },
        timeout=10
    )
    print(f"   Login status: {login_response.status_code}")
    print(f"   Login cookies: {dict(login_response.cookies)}")
    print(f"   Session cookies: {dict(session.cookies)}")
    
    if login_response.status_code == 200:
        print("   ✅ Login successful")
        login_data = login_response.json()
        print(f"   Login response keys: {login_data.keys()}")
        
        # Check if we get a user_id we can use as header
        user_id = login_data.get('user', {}).get('id') if isinstance(login_data.get('user'), dict) else None
        print(f"   User ID: {user_id}")
        
        print("2. Testing MCP API with session cookies...")
        mcp_response = session.post(
            "http://localhost:8002/api/chat/mcpai",
            json={"message": "Hello, this is a test message"},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        print(f"   MCP API (cookies) status: {mcp_response.status_code}")
        
        if mcp_response.status_code != 200:
            print(f"   Error: {mcp_response.text[:200]}")
        
        # Try with user ID header if we have it
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
                print(f"   ✅ Success! Status: {result.get('status', 'unknown')}")
                print(f"   Response: {result.get('response', 'No response')[:100]}...")
            else:
                print(f"   Error: {mcp_response_header.text[:200]}")
    else:
        print(f"   Login failed: {login_response.text[:200]}")

except Exception as e:
    print(f"❌ Test failed with error: {e}")

print("\nEnhanced diagnostic complete.")
