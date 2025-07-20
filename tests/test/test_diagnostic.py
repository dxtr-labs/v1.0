import requests
import json

print("🔍 Diagnostic Test for MCP API")

# Create session for authentication
session = requests.Session()

# Test user credentials
test_email = "test_mass_user@dxtr-labs.com"
test_password = "TestPassword123!"

try:
    print("1. Testing signup...")
    signup_response = session.post(
        "http://localhost:8002/api/auth/signup",
        json={
            "email": test_email,
            "password": test_password,
            "firstName": "Test",
            "lastName": "User"
        },
        timeout=10
    )
    print(f"   Signup status: {signup_response.status_code}")
    if signup_response.status_code != 201 and signup_response.status_code != 400:
        print(f"   Signup response: {signup_response.text[:200]}")

    print("2. Testing login...")
    login_response = session.post(
        "http://localhost:8002/api/auth/login",
        json={
            "email": test_email,
            "password": test_password
        },
        timeout=10
    )
    print(f"   Login status: {login_response.status_code}")
    if login_response.status_code != 200:
        print(f"   Login response: {login_response.text[:200]}")
    else:
        print("   ✅ Login successful")

    print("3. Testing MCP API call...")
    mcp_response = session.post(
        "http://localhost:8002/api/chat/mcpai",
        json={"message": "Hello, this is a test message"},
        headers={"Content-Type": "application/json"},
        timeout=15
    )
    print(f"   MCP API status: {mcp_response.status_code}")
    if mcp_response.status_code == 200:
        result = mcp_response.json()
        print(f"   ✅ Success! Status: {result.get('status', 'unknown')}")
        print(f"   Response: {result.get('response', 'No response')[:100]}...")
    else:
        print(f"   ❌ Error response: {mcp_response.text[:300]}")

except Exception as e:
    print(f"❌ Test failed with error: {e}")

print("\nDiagnostic complete.")
