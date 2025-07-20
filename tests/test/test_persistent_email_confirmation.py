#!/usr/bin/env python3
"""
Test email confirmation with persistent storage in agent memory
"""
import requests
import json
import time

def test_persistent_email_confirmation():
    base_url = "http://localhost:8002/api"
    
    print("🧪 TESTING PERSISTENT EMAIL CONFIRMATION FLOW")
    print("=" * 60)
    
    # First, authenticate
    print("\n🔐 AUTHENTICATION")
    login_response = requests.post(f"{base_url}/auth/login", json={
        "email": "aitest@example.com",
        "password": "testpass123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Authentication failed: {login_response.status_code}")
        print(f"   Response: {login_response.text}")
        return
        
    session_token = login_response.json().get("session_token")
    headers = {"Cookie": f"session_token={session_token}"}
    print("✅ Authentication successful")
    
    # Step 1: Create email request - should show preview with confirmation required
    print("\n1️⃣ STEP 1: Create email request with preview")
    email_request = {
        "message": "Send a motivational Monday email to slakshanand1105@gmail.com about staying productive this week"
    }
    
    response1 = requests.post(f"{base_url}/chat/mcpai", json=email_request, headers=headers)
    
    if response1.status_code == 200:
        data1 = response1.json()
        print(f"✅ Status: {data1.get('status')}")
        print(f"✅ Done: {data1.get('done')}")
        print(f"✅ Action Required: {data1.get('action_required')}")
        print(f"✅ Response Preview: {data1.get('response', '')[:200]}...")
        
        # Check if preview is ready
        if (data1.get('status') == 'preview_ready' and 
            data1.get('done') == False and 
            data1.get('action_required') == 'confirm_send'):
            print("✅ EMAIL PREVIEW READY - Confirmation required")
        else:
            print(f"❌ Expected preview_ready status, got: {data1.get('status')}")
            return
    else:
        print(f"❌ Request failed: {response1.status_code}")
        return
    
    print("\n" + "="*50)
    time.sleep(2)  # Brief pause between requests
    
    # Step 2: Confirm email sending - should execute the email
    print("\n2️⃣ STEP 2: Confirm email sending")
    confirm_request = {
        "message": "yes, send it"
    }
    
    response2 = requests.post(f"{base_url}/chat/mcpai", json=confirm_request, headers=headers)
    
    if response2.status_code == 200:
        data2 = response2.json()
        print(f"📋 Status: {data2.get('status')}")
        print(f"📋 Done: {data2.get('done')}")
        print(f"📋 Email Sent: {data2.get('email_sent', 'Not specified')}")
        print(f"📋 Response: {data2.get('response', '')[:300]}...")
        
        # Check if email was actually sent
        if (data2.get('status') == 'completed' and 
            data2.get('done') == True and
            data2.get('email_sent') == True):
            print("✅ EMAIL CONFIRMATION FLOW: SUCCESS! Email sent successfully")
        elif data2.get('status') == 'preview_ready':
            print("❌ EMAIL CONFIRMATION FLOW: FAILED - Still showing preview instead of sending")
            print("   This indicates the confirmation was not detected or processed correctly")
        else:
            print(f"⚠️ Unexpected result: {data2.get('status')}")
    else:
        print(f"❌ Confirmation request failed: {response2.status_code}")
    
    print("\n" + "="*60)
    print("🏁 TEST COMPLETE")

if __name__ == "__main__":
    test_persistent_email_confirmation()
