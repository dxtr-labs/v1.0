import requests
import json

# Test the new /api/chat/mcpai endpoint
def test_mcpai_endpoint():
    # First, let's signup a new user and then login
    signup_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpass123"
    }
    
    # Signup first
    print("Creating test user...")
    signup_response = requests.post("http://127.0.0.1:8001/api/auth/signup", json=signup_data)
    print(f"Signup Status: {signup_response.status_code}")
    
    # Login with the new user
    login_data = {
        "email": "testuser@example.com",
        "password": "testpass123"
    }
    
    # Login
    login_response = requests.post("http://127.0.0.1:8001/api/auth/login", json=login_data)
    print(f"Login Status: {login_response.status_code}")
    print(f"Login Response: {login_response.text}")
    
    if login_response.status_code == 200:
        # Get session token from response JSON
        login_data = login_response.json()
        session_token = login_data.get('session_token')
        print(f"Session token: {session_token}")
        
        if not session_token:
            print("❌ No session token received")
            print(f"Full response: {login_response.text}")
            return
        
        # Test the MCP AI endpoint
        test_message = {
            "message": "Hello Sam, can you help me with automation?"
        }
        
        mcpai_response = requests.post(
            "http://127.0.0.1:8001/api/chat/mcpai", 
            json=test_message,
            cookies={"session_token": session_token},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nMCP AI Status: {mcpai_response.status_code}")
        print(f"MCP AI Response: {mcpai_response.text}")
        
        if mcpai_response.status_code == 200:
            print("\n✅ SUCCESS: sam-personal assistant is connected to custom MCP LLM!")
        else:
            print(f"\n❌ FAILED: MCP AI endpoint returned {mcpai_response.status_code}")
    else:
        print("❌ Cannot test - login failed")

if __name__ == "__main__":
    try:
        test_mcpai_endpoint()
    except requests.exceptions.ConnectionError:
        print("❌ FAILED: Cannot connect to backend server. Is it running on port 8001?")
    except Exception as e:
        print(f"❌ ERROR: {e}")
