"""
Simple test to verify OpenAI-powered intent detection and email automation
"""
import requests
import json

# Test configuration
BASE_URL = "http://localhost:8002"
TEST_EMAIL = "test@example.com"

def test_simple_automation():
    """Test automation without complex auth"""
    
    # Try direct auth request  
    print("🔐 Testing simple authentication...")
    
    # Use existing known user
    auth_data = {
        "email": "user@example.com",
        "password": "securepass123"
    }
    
    try:
        # Try login
        response = requests.post(f"{BASE_URL}/api/auth/login", json=auth_data)
        print(f"Login response: {response.status_code}")
        
        if response.status_code == 200:
            session_data = response.json()
            user_id = session_data.get("user_id")
            cookies = response.cookies
            
            print(f"✅ Authenticated as user: {user_id}")
            
            # Test email automation
            print(f"\n🤖 Testing email automation with OpenAI intent detection...")
            
            automation_request = {
                "message": f"Draft a sales pitch and send it to {TEST_EMAIL}"
            }
            
            headers = {
                "x-user-id": str(user_id),
                "Content-Type": "application/json"
            }
            
            print(f"Sending request to: {BASE_URL}/api/chat/mcpai")
            print(f"Headers: {headers}")
            print(f"Payload: {automation_request}")
            
            response = requests.post(
                f"{BASE_URL}/api/chat/mcpai",
                json=automation_request,
                cookies=cookies,
                headers=headers
            )
            
            print(f"\n📧 Automation Response: {response.status_code}")
            print(f"Response text: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success!")
                print(f"📊 Status: {result.get('status')}")
                print(f"🎯 Automation Type: {result.get('automation_type')}")
                print(f"📧 Email Sent: {result.get('email_sent')}")
                print(f"💬 Message: {result.get('message')}")
                
                if result.get('email_sent'):
                    print(f"🎉 EMAIL AUTOMATION IS WORKING!")
                elif result.get('automation_type') == 'ai_content_email':
                    print(f"✅ OPENAI INTENT DETECTION IS WORKING!")
                else:
                    print(f"⚠️ Unexpected response type")
            else:
                print(f"❌ Request failed")
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Testing OpenAI-Powered Email Automation")
    print("=" * 50)
    test_simple_automation()
    print("=" * 50)
    print("✅ Test complete!")
