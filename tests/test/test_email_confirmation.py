#!/usr/bin/env python3
"""
Test the email confirmation flow
"""

import requests
import json
import time

def test_email_confirmation_flow():
    """Test the complete email generation + confirmation flow"""
    print("🔍 TESTING EMAIL CONFIRMATION FLOW")
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
    
    # Step 1: Send email generation request
    print(f"\n📧 Step 1: Requesting email generation...")
    test_message = """I am CEO and my name is Lakshanand Sugumar. We are proteinramen INC and we sell high protein ramen noodles. This is healthy.
Draft a sales pitch email about our company and send to slakshanand1105@gmail.com"""
    
    try:
        response1 = requests.post(f"{base_url}/api/agents/{agent_id}/chat",
            json={"message": test_message},
            headers=headers,
            timeout=30
        )
        
        if response1.status_code == 200:
            result1 = response1.json()
            email_response = result1.get('response', '')
            
            print(f"📝 Email Generation Response:")
            print("-" * 40)
            print(email_response[:400])
            print("..." if len(email_response) > 400 else "")
            print("-" * 40)
            
            # Check if it asks for confirmation
            needs_confirmation = any(phrase in email_response.lower() for phrase in [
                'would you like me to send', 'type yes to send', 'confirm', 'send this email'
            ])
            
            print(f"✅ Email preview generated: {'YES' if email_response else 'NO'}")
            print(f"✅ Asks for confirmation: {'YES' if needs_confirmation else 'NO'}")
            
            if not needs_confirmation:
                print("⚠️ Email doesn't seem to ask for confirmation")
                return False
                
        else:
            print(f"❌ Email generation failed: {response1.status_code}")
            print(f"Response: {response1.text}")
            return False
    
        # Step 2: Send confirmation
        print(f"\n✅ Step 2: Sending confirmation...")
        
        response2 = requests.post(f"{base_url}/api/agents/{agent_id}/chat",
            json={"message": "yes"},
            headers=headers,
            timeout=30
        )
        
        if response2.status_code == 200:
            result2 = response2.json()
            confirmation_response = result2.get('response', '')
            
            print(f"📧 Confirmation Response:")
            print("-" * 40)
            print(confirmation_response[:400])
            print("..." if len(confirmation_response) > 400 else "")
            print("-" * 40)
            
            # Check if email was sent successfully
            email_sent = any(phrase in confirmation_response.lower() for phrase in [
                'email sent successfully', 'delivered to the recipient', 'sent to', 'successfully sent'
            ])
            
            has_error = any(phrase in confirmation_response.lower() for phrase in [
                'missing recipient', 'missing email content', 'error', 'failed'
            ])
            
            print(f"✅ Email sent successfully: {'YES' if email_sent else 'NO'}")
            print(f"❌ Has error message: {'YES' if has_error else 'NO'}")
            
            if has_error:
                print(f"⚠️ Error detected in confirmation response")
                return False
            elif email_sent:
                print(f"🎉 Email confirmation flow working correctly!")
                return True
            else:
                print(f"⚠️ Unclear confirmation response")
                return False
                
        else:
            print(f"❌ Confirmation failed: {response2.status_code}")
            print(f"Response: {response2.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error in confirmation flow: {e}")
        return False

if __name__ == "__main__":
    print("🎯 EMAIL CONFIRMATION FLOW TEST")
    print("=" * 50)
    
    # Wait for server to be ready
    time.sleep(2)
    
    success = test_email_confirmation_flow()
    
    print(f"\n🏁 FINAL RESULT:")
    print(f"Email confirmation flow: {'✅ WORKING' if success else '❌ NEEDS FIX'}")
    
    if success:
        print(f"\n✅ Email generation and confirmation is working correctly!")
        print(f"The system can now:")
        print(f"1. Generate professional sales pitch emails")
        print(f"2. Show email preview for review")
        print(f"3. Send email after user confirmation")
    else:
        print(f"\n❌ Email confirmation flow needs more debugging")
