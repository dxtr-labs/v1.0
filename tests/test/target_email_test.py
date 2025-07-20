#!/usr/bin/env python3
"""
🎯 TARGET EMAIL TEST
Test sending to slakshanand1105@gmail.com using API
"""

import requests

def target_email_test():
    base_url = "http://localhost:8002"
    
    # Login
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "email": "aitest@example.com", 
        "password": "testpass123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    session_token = login_response.json().get("session_token")
    headers = {"Cookie": f"session_token={session_token}"}
    
    print("🎯 TARGET EMAIL TEST")
    print("=" * 40)
    
    payload = {"message": "Send an email to slakshanand1105@gmail.com about our TechCorp protein noodles"}
    
    response = requests.post(f"{base_url}/api/chat/mcpai", 
        json=payload, headers=headers, timeout=30)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        message = result.get('message', '')
        email_sent = result.get('email_sent', False)
        
        print(f"Message: {message}")
        print(f"Email sent: {email_sent}")
        
        if email_sent:
            print("✅ EMAIL SENT!")
        elif 'executed' in message:
            print("✅ EXECUTION ATTEMPTED")
        else:
            print("⚠️ STATUS UNCLEAR")
    else:
        print(f"❌ Failed: {response.status_code}")

if __name__ == "__main__":
    target_email_test()
