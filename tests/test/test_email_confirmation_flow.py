#!/usr/bin/env python3
"""
📧 EMAIL CONFIRMATION FLOW TEST
Test the new preview-then-confirm email workflow
"""

import requests
import json
import time

def test_email_confirmation_flow():
    """Test the complete email confirmation workflow"""
    base_url = "http://localhost:8002"
    
    # Login first
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "email": "aitest@example.com",
        "password": "testpass123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return False
    
    session_token = login_response.json().get("session_token")
    headers = {"Cookie": f"session_token={session_token}"}
    
    print("🧪 EMAIL CONFIRMATION FLOW TEST")
    print("=" * 60)
    
    # Step 1: Request an email (should show preview)
    print("\n📧 STEP 1: Requesting email automation...")
    print("-" * 40)
    
    email_request = {
        "message": "Send an email to slakshanand1105@gmail.com about our TechCorp protein noodles and FastMCP automation services"
    }
    
    try:
        response = requests.post(f"{base_url}/api/chat/mcpai", 
            json=email_request,
            headers=headers,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Check if we got a preview (not immediate execution)
            if result.get('status') == 'preview_ready':
                print("✅ PREVIEW MODE: Email preview generated (no automatic sending)")
                print(f"📧 Action Required: {result.get('action_required')}")
                print(f"⏳ Done Status: {result.get('done')}")
                print(f"📝 Message Preview:")
                print(result.get('message', '')[:300] + "...")
                
                # Step 2: Confirm the email
                print(f"\n✅ STEP 2: Confirming email send...")
                print("-" * 40)
                
                time.sleep(2)  # Brief pause
                
                confirm_request = {
                    "message": "yes, send it"
                }
                
                confirm_response = requests.post(f"{base_url}/api/chat/mcpai", 
                    json=confirm_request,
                    headers=headers,
                    timeout=30
                )
                
                print(f"Confirmation Status: {confirm_response.status_code}")
                
                if confirm_response.status_code == 200:
                    confirm_result = confirm_response.json()
                    
                    if confirm_result.get('email_sent'):
                        print("🎉 SUCCESS: Email sent after confirmation!")
                        print(f"✅ Email Status: {confirm_result.get('email_sent')}")
                        print(f"✅ Workflow Status: {confirm_result.get('workflow_status')}")
                        print(f"📧 Final Message: {confirm_result.get('message')}")
                        return True
                    else:
                        print("⚠️ PARTIAL: Confirmation processed but email status unclear")
                        print(f"📝 Response: {confirm_result.get('message')}")
                        return False
                else:
                    print(f"❌ Confirmation failed: {confirm_response.text}")
                    return False
                    
            elif result.get('status') == 'automation_ready' or 'executed' in result.get('message', ''):
                print("⚠️ ISSUE: Email was executed immediately (no preview shown)")
                print("❌ CONFIRMATION FLOW NOT WORKING - emails still auto-executing")
                print(f"📝 Response: {result.get('message')}")
                return False
            else:
                print("💬 CONVERSATIONAL: No automation detected")
                print(f"📝 Response: {result.get('message')}")
                return False
                
        else:
            print(f"❌ Initial request failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    """Run the email confirmation flow test"""
    
    print("🚀 TESTING EMAIL CONFIRMATION WORKFLOW")
    print("Testing whether emails show preview before sending")
    print()
    
    success = test_email_confirmation_flow()
    
    print(f"\n🎯 TEST RESULT")
    print("=" * 40)
    
    if success:
        print("✅ EMAIL CONFIRMATION FLOW: WORKING!")
        print("✅ Preview shown before sending")
        print("✅ User confirmation required")
        print("✅ Email sent after confirmation")
        print()
        print("🎉 The confirmation dialog is now working properly!")
        print("📧 Users will see email previews before sending")
    else:
        print("❌ EMAIL CONFIRMATION FLOW: NOT WORKING")
        print("⚠️ Emails may still be auto-executing")
        print("🔧 Check the backend configuration")
    
    print()
    print("📝 Next Steps:")
    print("   1. Test in the browser interface")
    print("   2. Verify confirmation buttons appear")
    print("   3. Check that 'yes' confirms and sends")

if __name__ == "__main__":
    main()
