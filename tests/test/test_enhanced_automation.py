"""
Test the enhanced OpenAI-powered intent detection and email automation
"""
import requests
import json
import time

# Test configuration
BASE_URL = "http://localhost:8002"
TEST_EMAIL = "test@example.com"

def test_authenticated_email_automation():
    """Test the complete email automation flow with proper authentication"""
    
    # Test with existing account first
    login_data = {
        "email": "testuser@example.com",
        "password": "testpass123"
    }
    
    print("� Trying to login with existing account...")
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"Login Response: {login_response.status_code}")
    
    if login_response.status_code != 200:
        # Try creating new account with unique email
        import random
        unique_email = f"testuser{random.randint(1000,9999)}@example.com"
        
        signup_data = {
            "email": unique_email,
            "password": "testpass123",
            "name": "Test User"
        }
        
        print(f"� Creating new test account: {unique_email}")
        signup_response = requests.post(f"{BASE_URL}/api/auth/signup", json=signup_data)
        print(f"Signup Response: {signup_response.status_code}")
        
        if signup_response.status_code != 200:
            print(f"❌ Signup failed: {signup_response.text}")
            return
        
        # Login with new account
        login_data["email"] = unique_email
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"Login Response: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    # Extract session cookies and user ID
    session_cookies = login_response.cookies
    session_data = login_response.json()
    user_id = session_data.get("user_id")
    
    print(f"✅ Authenticated as user {user_id}")
    
    # Step 3: Test email automation with OpenAI-powered intent detection
    print(f"\n🤖 Testing OpenAI-powered email automation...")
    
    # Test different email automation requests
    test_messages = [
        f"Draft a sales pitch and send it to {TEST_EMAIL}",
        f"Send an email to {TEST_EMAIL} about our new product",
        f"Create a professional email for {TEST_EMAIL}",
        f"Write a business proposal and email it to {TEST_EMAIL}",
        "Hi, how are you?",  # Conversational test
        "What can you do?",  # Conversational test
    ]
    
    headers = {
        "x-user-id": str(user_id),
        "Content-Type": "application/json"
    }
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📧 Test {i}: '{message}'")
        
        # Send automation request
        automation_payload = {
            "message": message
        }
        
        response = requests.post(
            f"{BASE_URL}/api/chat/mcpai", 
            json=automation_payload,
            cookies=session_cookies,
            headers=headers
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('message', 'No message')}")
            print(f"📊 Status: {result.get('status', 'No status')}")
            print(f"🎯 Automation Type: {result.get('automation_type', 'None')}")
            print(f"📧 Email Sent: {result.get('email_sent', False)}")
            print(f"🔄 Has Workflow: {result.get('hasWorkflowJson', False)}")
            
            # If this was supposed to be automation, check for expected fields
            if "email" in message.lower() and "draft" in message.lower():
                if result.get('email_sent'):
                    print(f"🎉 EMAIL AUTOMATION WORKING! Email sent to {TEST_EMAIL}")
                else:
                    print(f"⚠️ Email automation created but not sent yet")
            elif any(word in message.lower() for word in ["hi", "how", "what"]):
                if result.get('automation_type') == 'conversational':
                    print(f"💬 CONVERSATIONAL ROUTING WORKING!")
                else:
                    print(f"⚠️ Conversational message incorrectly routed to automation")
        else:
            print(f"❌ Request failed: {response.text}")
        
        # Small delay between tests
        time.sleep(1)

if __name__ == "__main__":
    print("🚀 Testing Enhanced OpenAI-Powered Email Automation System")
    print("=" * 60)
    test_authenticated_email_automation()
    print("\n" + "=" * 60)
    print("✅ Testing complete!")
