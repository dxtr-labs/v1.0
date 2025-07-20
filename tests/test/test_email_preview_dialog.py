#!/usr/bin/env python3
"""
Test if the email preview dialog functionality is working correctly
"""

import requests
import json

def test_email_preview_dialog():
    """Test the email preview dialog trigger with current backend response"""
    print("🎯 TESTING EMAIL PREVIEW DIALOG FUNCTIONALITY")
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
    
    # Test email request
    test_message = """I am ceo and my name is Lakshanand Sugumar. We are proteinramen INC and we sell high protein ramen noodles. this is healthy.
Draft a sales pitch email about our company and send to slakshanand1105@gmail.com"""
    
    print(f"\n📧 Testing email request...")
    
    try:
        response = requests.post(f"{base_url}/api/chat/mcpai",
            json={"message": test_message},
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n📋 BACKEND RESPONSE ANALYSIS:")
            print("=" * 50)
            
            # Check all fields needed for email preview dialog
            has_email_content = result.get('email_content') is not None
            has_recipient = result.get('recipient') is not None
            has_email_subject = result.get('email_subject') is not None
            has_email_preview = result.get('email_preview') is not None
            status = result.get('status')
            action_required = result.get('action_required')
            
            print(f"✅ email_content: {'YES' if has_email_content else 'NO'}")
            print(f"✅ recipient: {'YES' if has_recipient else 'NO'}")
            print(f"✅ email_subject: {'YES' if has_email_subject else 'NO'}")
            print(f"✅ email_preview: {'YES' if has_email_preview else 'NO'}")
            print(f"✅ status: {status}")
            print(f"✅ action_required: {action_required}")
            
            print(f"\n🎯 FRONTEND DIALOG TRIGGER CONDITIONS:")
            print("=" * 50)
            
            # Check the conditions that should trigger the dialog
            condition1 = status == 'preview_ready' and action_required == 'approve_email'
            condition2 = has_email_content and has_recipient
            condition3 = has_email_preview and has_recipient
            
            print(f"Condition 1 (status + action): {'✅ YES' if condition1 else '❌ NO'}")
            print(f"Condition 2 (email_content + recipient): {'✅ YES' if condition2 else '❌ NO'}")
            print(f"Condition 3 (email_preview + recipient): {'✅ YES' if condition3 else '❌ NO'}")
            
            will_trigger = condition1 or condition2 or condition3
            print(f"\n🎉 DIALOG WILL TRIGGER: {'✅ YES' if will_trigger else '❌ NO'}")
            
            if will_trigger:
                print(f"\n📧 EMAIL PREVIEW DATA:")
                print("=" * 30)
                if has_email_preview:
                    preview = result.get('email_preview', {})
                    print(f"To: {preview.get('to', 'N/A')}")
                    print(f"Subject: {preview.get('subject', 'N/A')}")
                    print(f"Content Preview: {preview.get('content', 'N/A')[:100]}...")
                else:
                    print(f"To: {result.get('recipient', 'N/A')}")
                    print(f"Subject: {result.get('email_subject', 'N/A')}")
                    print(f"Content Preview: {result.get('email_content', 'N/A')[:100]}...")
                
                print(f"\n💡 INSTRUCTIONS FOR USER:")
                print("=" * 30)
                print("1. ✅ Backend is working correctly")
                print("2. ✅ Email preview dialog should trigger")
                print("3. 📱 Open mcp-enhanced-chat.html in your browser")
                print("4. 🔄 Make sure to refresh the page after our frontend fix")
                print("5. 📧 Send the email request in the chat interface")
                print("6. 🎯 The editable email preview dialog should appear!")
                
                return True
            else:
                print(f"\n❌ ISSUE: Dialog won't trigger with current response format")
                print(f"🔧 Need to update frontend detection logic")
                return False
            
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_email_preview_dialog()
    
    if success:
        print(f"\n🎉 EMAIL PREVIEW DIALOG TEST: ✅ PASSED")
        print(f"📱 Try it now in your browser!")
    else:
        print(f"\n❌ EMAIL PREVIEW DIALOG TEST: ❌ FAILED")
        print(f"🔧 Need to fix frontend/backend integration")
