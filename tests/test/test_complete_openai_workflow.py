#!/usr/bin/env python3
"""
Test complete email automation workflow with OpenAI integration
"""
import requests
import json
import time

def test_email_automation():
    print("🧪 TESTING COMPLETE EMAIL AUTOMATION WITH OPENAI")
    print("=" * 60)
    
    # Backend API endpoint
    url = "http://localhost:8002/api/chat/mcpai"
    
    # Test request for email automation
    test_message = "create a sales pitch email for selling healthy protein bars and send email to slakshanand1105@gmail.com"
    
    payload = {
        "message": test_message,
        "user_id": "test-user-123"
    }
    
    print(f"📤 Sending request: {test_message}")
    print("-" * 60)
    
    try:
        response = requests.post(url, json=payload)
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response Data:")
            print(json.dumps(result, indent=2))
            
            # Check if email was sent
            if result.get('email_sent'):
                print("\n🎉 SUCCESS: Email automation completed!")
                print(f"   📧 Email sent to: {result.get('recipient_email')}")
                print(f"   📝 Subject: {result.get('email_subject')}")
                print(f"   💡 Content type: {result.get('content_type')}")
            else:
                print("\n⚠️  Email not sent - check response for details")
        else:
            print(f"❌ Request failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the backend server running?")
        print("   Run: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_email_automation()
