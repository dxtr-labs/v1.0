#!/usr/bin/env python3
"""
Test frontend email preview dialog trigger
"""

import requests
import json

def test_email_preview_dialog_trigger():
    """Test if the response format triggers the frontend email preview dialog"""
    print("🔍 TESTING EMAIL PREVIEW DIALOG TRIGGER")
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
    
    # Test the exact message from the screenshot
    test_message = """I am ceo and my name is Lakshanand Sugumar. We are proteinramen INC and we sell high protein ramen noodles. this is healthy.
Draft a sales pitch email about our company and send to slakshanand1105@gmail.com"""
    
    print(f"\n📧 Testing email preview dialog trigger...")
    print(f"Request: {test_message[:80]}...")
    
    try:
        response = requests.post(f"{base_url}/api/chat/mcpai",
            json={"message": test_message},
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n📋 Frontend Preview Dialog Check:")
            print(f"   Status: {response.status_code}")
            
            # Check the specific fields frontend looks for
            status = result.get('status')
            action_required = result.get('action_required')
            email_content = result.get('email_content')
            recipient = result.get('recipient')
            email_preview = result.get('email_preview')
            
            print(f"   status: {status}")
            print(f"   action_required: {action_required}")
            print(f"   email_content exists: {'YES' if email_content else 'NO'}")
            print(f"   recipient: {recipient}")
            print(f"   email_preview exists: {'YES' if email_preview else 'NO'}")
            
            # Check frontend conditions
            condition1 = status == 'preview_ready' and action_required == 'approve_email'
            condition2 = email_content and recipient
            condition3 = 'Email Preview' in result.get('message', '')
            
            print(f"\n🔍 Frontend Condition Analysis:")
            print(f"   Condition 1 (status + action): {'✅' if condition1 else '❌'}")
            print(f"     - status === 'preview_ready': {'YES' if status == 'preview_ready' else 'NO'}")
            print(f"     - action_required === 'approve_email': {'YES' if action_required == 'approve_email' else 'NO'}")
            
            print(f"   Condition 2 (email_content + recipient): {'✅' if condition2 else '❌'}")
            print(f"     - email_content exists: {'YES' if email_content else 'NO'}")
            print(f"     - recipient exists: {'YES' if recipient else 'NO'}")
            
            print(f"   Condition 3 (message contains 'Email Preview'): {'✅' if condition3 else '❌'}")
            
            # Check if any condition passes
            will_trigger_dialog = condition1 or condition2 or condition3
            
            print(f"\n🎯 DIALOG TRIGGER PREDICTION:")
            print(f"   Will trigger email preview dialog: {'✅ YES' if will_trigger_dialog else '❌ NO'}")
            
            if will_trigger_dialog:
                print(f"   ✅ Response format should trigger frontend email preview dialog!")
                
                # Show email preview structure if it exists
                if email_preview:
                    print(f"\n📧 Email Preview Structure:")
                    print(f"   to: {email_preview.get('to', 'N/A')}")
                    print(f"   subject: {email_preview.get('subject', 'N/A')}")
                    print(f"   content length: {len(email_preview.get('content', ''))}")
                    print(f"   preview_content length: {len(email_preview.get('preview_content', ''))}")
                
                return True
            else:
                print(f"   ❌ Response format will NOT trigger email preview dialog")
                print(f"   💡 Frontend expects one of:")
                print(f"      1. status='preview_ready' AND action_required='approve_email'")
                print(f"      2. email_content AND recipient fields")
                print(f"      3. message containing 'Email Preview'")
                return False
                
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 EMAIL PREVIEW DIALOG TRIGGER TEST")
    print("=" * 50)
    
    success = test_email_preview_dialog_trigger()
    
    print(f"\n🏁 FINAL RESULT:")
    print(f"Email preview dialog trigger: {'✅ WORKING' if success else '❌ NEEDS FIX'}")
    
    if success:
        print(f"\n🎉 The response format should trigger the frontend email preview dialog!")
        print(f"📱 You should see an editable preview box in the frontend interface.")
    else:
        print(f"\n🔧 The response format needs adjustment to trigger the preview dialog.")
        print(f"🔍 Check the frontend conditions and ensure backend response matches.")
