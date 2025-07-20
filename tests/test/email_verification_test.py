#!/usr/bin/env python3
"""
🎯 EMAIL VERIFICATION TEST
Check if email is actually being sent to slakshanand1105@gmail.com
"""

import requests
import time

def email_verification_test():
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
    
    print("🎯 EMAIL VERIFICATION TEST")
    print("=" * 50)
    print(f"⏰ Test Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test the specific email automation
    payload = {
        "message": "Send an urgent test email to slakshanand1105@gmail.com with subject 'URGENT: Test Email Verification from DXTR Labs' and tell them this is to verify the automation system is working. Include the current timestamp and ask them to reply to confirm receipt."
    }
    
    print(f"📤 Sending automation request...")
    
    response = requests.post(f"{base_url}/api/chat/mcpai", 
        json=payload, headers=headers, timeout=30)
    
    print(f"📊 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        message = result.get('message', '')
        email_sent = result.get('email_sent', False)
        automation_type = result.get('automation_type', 'unknown')
        
        print(f"\n📋 RESULT ANALYSIS:")
        print(f"   automation_type: {automation_type}")
        print(f"   email_sent: {email_sent}")
        print(f"   Message: {message}")
        
        # Check message content for execution indicators
        if 'executed' in message.lower():
            print(f"\n✅ EXECUTION CONFIRMED")
            if email_sent:
                print(f"✅ EMAIL_SENT FLAG: TRUE")
                print(f"🎉 EMAIL SUCCESSFULLY SENT TO slakshanand1105@gmail.com!")
            else:
                print(f"⚠️ EMAIL_SENT FLAG: FALSE")
                print(f"❓ Email execution attempted but flag not set")
        elif 'queued' in message.lower():
            print(f"\n⏳ EMAIL QUEUED - execution may have failed")
        else:
            print(f"\n❌ NO EXECUTION DETECTED")
        
        # Also test the direct email API endpoint
        print(f"\n🧪 Testing direct email API...")
        direct_email_payload = {
            "to": "slakshanand1105@gmail.com",
            "subject": "Direct API Test - DXTR Labs",
            "content": f"This is a direct API test email sent at {time.strftime('%Y-%m-%d %H:%M:%S')}. If you receive this, the direct email API is working.",
            "from_name": "DXTR Labs Automation System"
        }
        
        try:
            email_response = requests.post(f"{base_url}/api/email/send", 
                json=direct_email_payload, headers=headers, timeout=30)
            
            print(f"   Direct email API status: {email_response.status_code}")
            
            if email_response.status_code == 200:
                email_result = email_response.json()
                print(f"   Direct email result: {email_result}")
                if email_result.get('success'):
                    print(f"   ✅ DIRECT EMAIL API WORKING!")
                else:
                    print(f"   ❌ Direct email API failed")
            else:
                print(f"   ❌ Direct email API error: {email_response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Direct email API exception: {e}")
    
    else:
        print(f"❌ Automation request failed: {response.status_code}")
        print(response.text[:200])

if __name__ == "__main__":
    email_verification_test()
