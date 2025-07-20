#!/usr/bin/env python3
"""
🔍 EMAIL SERVICE TEST
Test if the email service is working and can send emails
"""

import requests
import json

def test_email_service():
    """Test if email service can send actual emails"""
    
    base_url = "http://localhost:8002"
    
    # Login first
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "email": "aitest@example.com",
        "password": "testpass123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    session_token = login_response.json().get("session_token")
    headers = {"Cookie": f"session_token={session_token}"}
    
    print("📧 TESTING ACTUAL EMAIL DELIVERY")
    print("=" * 50)
    
    # Test 1: Try to send email directly
    print("🧪 Test 1: Direct automation request")
    payload = {
        "message": "Send an email to slakshanand1105@gmail.com with subject 'Test Email' and content 'This is a test email from the automation system. Please confirm you received this.'"
    }
    
    response = requests.post(f"{base_url}/api/chat/mcpai", 
        json=payload,
        headers=headers,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   automation_type: {result.get('automation_type')}")
        print(f"   message: {result.get('message', '')}")
        
        # Check if email was actually sent
        if 'sent' in result.get('message', '').lower() or 'delivered' in result.get('message', '').lower():
            print("✅ Email may have been sent!")
        else:
            print("⚠️ Email creation confirmed but delivery status unclear")
    
    print("\n🧪 Test 2: Check email service endpoint")
    
    # Try direct email endpoint if it exists
    email_test_payload = {
        "to": "slakshanand1105@gmail.com",
        "subject": "Direct Email Test",
        "content": "This is a direct email test to verify the email service is working.",
        "from_name": "DXTR Labs Test"
    }
    
    # Try different possible email endpoints
    email_endpoints = [
        "/api/email/send",
        "/api/automations/send-email", 
        "/api/send-email",
        "/email/send"
    ]
    
    for endpoint in email_endpoints:
        try:
            email_response = requests.post(f"{base_url}{endpoint}", 
                json=email_test_payload,
                headers=headers,
                timeout=30
            )
            
            print(f"   Endpoint {endpoint}: {email_response.status_code}")
            
            if email_response.status_code == 200:
                email_result = email_response.json()
                print(f"   ✅ SUCCESS: {email_result}")
                if email_result.get('success') or email_result.get('sent'):
                    print(f"   📧 EMAIL SENT TO slakshanand1105@gmail.com via {endpoint}!")
                    return
            elif email_response.status_code != 404:
                print(f"   Response: {email_response.text[:100]}")
                
        except Exception as e:
            print(f"   Error testing {endpoint}: {e}")
    
    print("\n🧪 Test 3: Check email configuration")
    
    # Check if email service is configured
    config_endpoints = [
        "/api/config/email",
        "/api/email/status",
        "/api/email/config"
    ]
    
    for endpoint in config_endpoints:
        try:
            config_response = requests.get(f"{base_url}{endpoint}", headers=headers)
            print(f"   Config {endpoint}: {config_response.status_code}")
            
            if config_response.status_code == 200:
                config_result = config_response.json()
                print(f"   Config: {config_result}")
                
        except Exception as e:
            print(f"   Error checking {endpoint}: {e}")

if __name__ == "__main__":
    test_email_service()
