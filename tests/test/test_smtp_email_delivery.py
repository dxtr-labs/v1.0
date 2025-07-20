#!/usr/bin/env python3
"""
Test actual email delivery with SMTP
"""

import requests
import json
import time

def test_real_email_delivery():
    """Test that emails are actually being sent via SMTP"""
    print("🔍 TESTING REAL EMAIL DELIVERY VIA SMTP")
    print("=" * 60)
    
    base_url = "http://localhost:8002"
    
    # Login
    print("🔐 Authenticating...")
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "email": "aitest@example.com",
        "password": "testpass123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return False
    
    session_token = login_response.json().get("session_token")
    headers = {"Cookie": f"session_token={session_token}"}
    print("✅ Authentication successful")
    
    # Get the user's agent
    agents_response = requests.get(f"{base_url}/api/agents", headers=headers)
    if agents_response.status_code != 200:
        print("❌ Failed to get agents")
        return False
    
    agents = agents_response.json().get('agents', [])
    if not agents:
        print("❌ No agents found")
        return False
    
    agent = agents[0]
    agent_id = agent.get('id')
    print(f"🤖 Using agent: {agent.get('name')} (ID: {agent_id})")
    
    # Test with a clear test email message
    print(f"\n📧 Step 1: Requesting email generation...")
    test_message = """Send a test email to slakshanand1105@gmail.com

Subject: Email System Test - ProteinRamen INC
Message: 
Hello! This is a test email from the ProteinRamen INC automation system. 

Company: ProteinRamen INC
CEO: Lakshanand Sugumar
Product: High protein ramen noodles (healthy food option)

If you receive this email, it means the email delivery system is working correctly!

Best regards,
Lakshanand Sugumar
CEO, ProteinRamen INC"""
    
    try:
        # Step 1: Generate email
        response1 = requests.post(f"{base_url}/api/agents/{agent_id}/chat",
            json={"message": test_message},
            headers=headers,
            timeout=30
        )
        
        if response1.status_code == 200:
            result1 = response1.json()
            email_response = result1.get('response', '')
            
            print(f"📝 Email Generation Response:")
            print(f"   Length: {len(email_response)} characters")
            print(f"   Contains 'Email Ready': {'YES' if 'Email Ready' in email_response else 'NO'}")
            print(f"   Contains recipient: {'YES' if 'slakshanand1105@gmail.com' in email_response else 'NO'}")
            print(f"   Contains confirmation prompt: {'YES' if any(phrase in email_response.lower() for phrase in ['yes to send', 'confirm', 'would you like']) else 'NO'}")
            
            if 'Email Ready' not in email_response:
                print("❌ Email generation may have failed")
                print(f"Response preview: {email_response[:200]}...")
                return False
                
        else:
            print(f"❌ Email generation failed: {response1.status_code}")
            return False
    
        # Step 2: Confirm sending
        print(f"\n✅ Step 2: Confirming email send...")
        
        response2 = requests.post(f"{base_url}/api/agents/{agent_id}/chat",
            json={"message": "yes"},
            headers=headers,
            timeout=30
        )
        
        if response2.status_code == 200:
            result2 = response2.json()
            confirmation_response = result2.get('response', '')
            
            print(f"📧 Confirmation Response Analysis:")
            print(f"   Length: {len(confirmation_response)} characters")
            
            # Check for actual sending indicators
            smtp_indicators = [
                'sent from:', 'automation-engine@dxtr-labs.com', 
                'delivered to the recipient', 'email sent successfully'
            ]
            
            found_smtp_indicators = [ind for ind in smtp_indicators if ind in confirmation_response.lower()]
            
            # Check for error indicators
            error_indicators = [
                'missing recipient', 'missing email content', 'authentication failed',
                'could not connect', 'smtp', 'failed to send'
            ]
            
            found_errors = [err for err in error_indicators if err in confirmation_response.lower()]
            
            print(f"   SMTP delivery indicators: {found_smtp_indicators}")
            print(f"   Error indicators: {found_errors}")
            print(f"   Response preview: {confirmation_response[:300]}...")
            
            # Determine if email was actually sent
            if found_smtp_indicators and not found_errors:
                print(f"\n🎉 SUCCESS: Email appears to have been sent via SMTP!")
                print(f"✅ Delivery indicators found: {len(found_smtp_indicators)}")
                print(f"❌ No error indicators found")
                
                print(f"\n📬 Please check slakshanand1105@gmail.com for the test email.")
                print(f"🕐 Email may take a few minutes to arrive.")
                
                return True
            elif found_errors:
                print(f"\n❌ EMAIL SENDING FAILED: {found_errors}")
                return False
            else:
                print(f"\n⚠️ UNCLEAR: Email may or may not have been sent")
                return False
                
        else:
            print(f"❌ Confirmation failed: {response2.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error in email delivery test: {e}")
        return False

if __name__ == "__main__":
    print("🎯 REAL EMAIL DELIVERY TEST")
    print("=" * 50)
    
    success = test_real_email_delivery()
    
    print(f"\n🏁 FINAL RESULT:")
    print(f"Real email delivery: {'✅ WORKING' if success else '❌ NEEDS FIX'}")
    
    if success:
        print(f"\n🚀 Email delivery system is working!")
        print(f"📧 Check slakshanand1105@gmail.com for the test email")
        print(f"📨 Emails are being sent from: automation-engine@dxtr-labs.com")
    else:
        print(f"\n🔧 Email delivery needs debugging")
        print(f"Check SMTP configuration and credentials")
