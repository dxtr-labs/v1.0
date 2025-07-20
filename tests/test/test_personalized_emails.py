#!/usr/bin/env python3
"""
Test different types of personalized email automation
"""
import requests
import json
import time

def test_email_automation(message, description):
    print(f"\n🧪 TESTING: {description}")
    print("=" * 80)
    
    # Backend API endpoint
    url = "http://localhost:8002/api/chat/mcpai"
    
    # Authentication
    auth_url = "http://localhost:8002/auth/login"
    auth_payload = {
        "username": "testuser",
        "password": "testpassword"
    }
    
    auth_response = requests.post(auth_url, json=auth_payload)
    if auth_response.status_code != 200:
        print("❌ Authentication failed")
        return
    
    token = auth_response.json().get("access_token")
    user_id = auth_response.json().get("user_id")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "message": message,
        "user_id": user_id
    }
    
    print(f"📤 Request: {message}")
    print("-" * 80)
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('email_sent', False)}")
            print(f"📧 Recipient: {result.get('recipient_email')}")
            print(f"📝 Subject: {result.get('email_subject')}")
            print(f"💡 Content Type: {result.get('content_type')}")
            print(f"🤖 Message: {result.get('message')}")
            
            if result.get('email_content'):
                print(f"\n📋 Generated Content Preview:")
                content = result.get('email_content', '')
                preview = content[:200] + "..." if len(content) > 200 else content
                print(f"   {preview}")
                
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 TESTING PERSONALIZED AI EMAIL AUTOMATION")
    print("=" * 80)
    
    test_cases = [
        ("create a sales pitch email for selling premium organic coffee beans and send to slakshanand1105@gmail.com", 
         "Premium Coffee Sales Pitch"),
        
        ("draft a professional welcome email for new customers joining our fitness program and send to slakshanand1105@gmail.com",
         "Fitness Program Welcome Email"),
        
        ("create a thank you email for a client who just purchased our web development services and send to slakshanand1105@gmail.com",
         "Web Development Thank You Email"),
        
        ("write a follow-up email for a potential customer interested in our AI automation services and send to slakshanand1105@gmail.com",
         "AI Services Follow-up Email")
    ]
    
    for message, description in test_cases:
        test_email_automation(message, description)
        time.sleep(2)  # Brief pause between tests
    
    print("\n🎉 All email automation tests completed!")
    print("📬 Check your inbox at slakshanand1105@gmail.com for the personalized emails")
