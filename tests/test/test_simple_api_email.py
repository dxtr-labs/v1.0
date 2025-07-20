#!/usr/bin/env python3

# Simple API test for email automation
import requests
import json

def test_simple_api_email():
    """Test the API email functionality without authentication"""
    print("🧪 Simple API Email Test")
    print("=" * 30)
    
    url = "http://localhost:8002/api/chat/mcpai"
    email = "slakshanand1105@gmail.com"
    
    payload = {
        "user_input": f"draft a sales pitch and send email to {email}",
        "agent_id": "test_agent_123",
        "conversation_id": "test_conv_123"
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-user-id": "test_user_123",
        "Cookie": "session_token=test_session_123"
    }
    
    try:
        print(f"📤 Sending request to: {url}")
        print(f"📧 Target email: {email}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("📋 API Response:")
            print(f"  Status: {result.get('status')}")
            print(f"  Success: {result.get('success')}")
            print(f"  Message: {result.get('message', 'No message')[:100]}...")
            print(f"  Email sent: {result.get('email_sent')}")
            print(f"  Workflow ID: {result.get('workflow_id')}")
            print(f"  Has workflow: {result.get('hasWorkflowJson')}")
            print(f"  Has preview: {result.get('hasWorkflowPreview')}")
            
            if result.get('email_sent') is True:
                print("🎉 SUCCESS: API reports email was sent!")
                return True
            elif result.get('email_sent') is None:
                print("⚠️ PARTIAL: email_sent is null (integration issue)")
                return False
            else:
                print("❌ FAILED: email_sent is false")
                return False
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

if __name__ == "__main__":
    success = test_simple_api_email()
    if success:
        print("\n✅ Email API test successful!")
    else:
        print("\n❌ Email API test failed!")
