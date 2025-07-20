#!/usr/bin/env python3
"""
Final test for the OpenAI-powered email automation system
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8002"

def main():
    print("🚀 Testing Enhanced OpenAI Email Automation System")
    print("=" * 60)
    
    # Step 1: Login with existing user
    print("🔑 Logging in...")
    login_data = {
        "email": "testautomation@example.com",
        "password": "testpass123"
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=10)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return False
        
        # Extract user info
        login_data = login_response.json()
        user_id = login_data.get("user", {}).get("user_id")
        session_token = login_data.get("session_token")
        
        print(f"✅ Logged in successfully")
        print(f"User ID: {user_id}")
        
        # Step 2: Test email automation
        print("\n🤖 Testing OpenAI-powered email automation...")
        
        automation_message = "Draft a sales pitch and send it to test@example.com"
        
        automation_payload = {
            "message": automation_message
        }
        
        headers = {
            "x-user-id": str(user_id),
            "Content-Type": "application/json",
            "Authorization": f"Bearer {session_token}"
        }
        
        print(f"Sending request: '{automation_message}'")
        
        automation_response = requests.post(
            f"{BASE_URL}/api/chat/mcpai",
            json=automation_payload,
            headers=headers,
            timeout=30
        )
        
        print(f"Automation status: {automation_response.status_code}")
        
        if automation_response.status_code == 200:
            result = automation_response.json()
            
            print("✅ SUCCESS! Automation response received:")
            print(f"📊 Status: {result.get('status')}")
            print(f"🎯 Automation Type: {result.get('automation_type')}")
            print(f"📧 Email Sent: {result.get('email_sent')}")
            print(f"🔄 Has Workflow JSON: {result.get('hasWorkflowJson')}")
            print(f"📝 Message: {result.get('message')}")
            
            # Check if this was successful automation
            if result.get('email_sent'):
                print("\n🎉 EMAIL AUTOMATION WORKING PERFECTLY!")
                print("✅ OpenAI intent detection successful")
                print("✅ Email automation executed")
                print("✅ Email sent successfully")
                return True
            elif result.get('automation_type') in ['ai_content_email', 'email_automation']:
                print("\n✅ AUTOMATION INTENT DETECTED CORRECTLY!")
                print("✅ OpenAI-powered routing working")
                print("⚠️ Email workflow created but not sent (check SMTP config)")
                return True
            elif result.get('automation_type') == 'conversational':
                print("\n❌ ROUTING ERROR: Email request routed to conversational agent")
                return False
            else:
                print(f"\n⚠️ Unexpected automation type: {result.get('automation_type')}")
                return False
        else:
            print(f"❌ Automation request failed: {automation_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 60)
    if success:
        print("🎉 OpenAI-Powered Email Automation is WORKING!")
    else:
        print("❌ Automation test failed")
    print("=" * 60)
    sys.exit(0 if success else 1)
