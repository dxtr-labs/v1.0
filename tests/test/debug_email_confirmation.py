#!/usr/bin/env python3
"""
🔍 EMAIL CONFIRMATION DEBUG TEST
Debug why the confirmation flow isn't working properly
"""

import requests
import json
import time

def debug_email_confirmation():
    """Debug the email confirmation workflow step by step"""
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
    
    print("🔍 EMAIL CONFIRMATION DEBUG")
    print("=" * 60)
    
    # Step 1: Request an email
    print("\n📧 STEP 1: Initial email request...")
    print("-" * 40)
    
    email_request = {
        "message": "Draft an email to slakshanand1105@gmail.com about our TechCorp protein noodles"
    }
    
    try:
        response = requests.post(f"{base_url}/api/chat/mcpai", 
            json=email_request,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Step 1 Response Analysis:")
            print(f"   Status: {result.get('status')}")
            print(f"   Has Workflow JSON: {result.get('hasWorkflowJson')}")
            print(f"   Action Required: {result.get('action_required')}")
            print(f"   Done: {result.get('done')}")
            print(f"   Email Sent: {result.get('email_sent')}")
            print(f"   Workflow Status: {result.get('workflow_status')}")
            
            # Check the message content
            message = result.get('message', '')
            if 'email ready for review' in message.lower():
                print(f"   ✅ Preview message detected")
            if 'type \'yes\'' in message.lower() or 'would you like me to send' in message.lower():
                print(f"   ✅ Confirmation request detected")
            
            print(f"\n📝 Full Response Keys: {list(result.keys())}")
            
            # Now test different confirmation messages
            confirmation_tests = [
                "yes",
                "yes, send it", 
                "send the email",
                "go ahead and send",
                "confirm"
            ]
            
            for i, confirm_msg in enumerate(confirmation_tests, 1):
                print(f"\n🧪 STEP 2.{i}: Testing confirmation: '{confirm_msg}'")
                print("-" * 40)
                
                time.sleep(1)  # Brief pause
                
                confirm_request = {"message": confirm_msg}
                
                confirm_response = requests.post(f"{base_url}/api/chat/mcpai", 
                    json=confirm_request,
                    headers=headers,
                    timeout=30
                )
                
                if confirm_response.status_code == 200:
                    confirm_result = confirm_response.json()
                    
                    print(f"   Response Status: {confirm_result.get('status')}")
                    print(f"   Email Sent: {confirm_result.get('email_sent')}")
                    print(f"   Done: {confirm_result.get('done')}")
                    print(f"   Workflow Status: {confirm_result.get('workflow_status')}")
                    
                    # Check if it's actually confirming or creating new preview
                    message = confirm_result.get('message', '')
                    if 'sent' in message.lower() and 'successfully' in message.lower():
                        print(f"   ✅ SUCCESS: Email confirmation worked!")
                        print(f"   📧 Success Message: {message[:100]}...")
                        return True
                    elif 'email ready for review' in message.lower():
                        print(f"   ❌ ISSUE: Generated new preview instead of confirming")
                        print(f"   📝 Message: {message[:100]}...")
                    else:
                        print(f"   ⚠️ UNCLEAR: Unexpected response")
                        print(f"   📝 Message: {message[:100]}...")
                else:
                    print(f"   ❌ Confirmation request failed: {confirm_response.status_code}")
                
                # If first confirmation worked, don't test others
                if confirm_result.get('email_sent') and confirm_result.get('status') == 'completed':
                    return True
            
            return False
        else:
            print(f"❌ Initial request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Debug error: {e}")
        return False

def main():
    """Run the debug test"""
    
    print("🔍 DEBUGGING EMAIL CONFIRMATION WORKFLOW")
    print("Analyzing why confirmation isn't working properly")
    print()
    
    success = debug_email_confirmation()
    
    print(f"\n🎯 DEBUG RESULTS")
    print("=" * 40)
    
    if success:
        print("✅ Email confirmation is working!")
    else:
        print("❌ Email confirmation needs fixing")
        print()
        print("🔧 Possible Issues:")
        print("   1. Confirmation detection not working")
        print("   2. Workflow storage/retrieval failing")
        print("   3. Session state not maintained")
        print("   4. Logic flow incorrect")

if __name__ == "__main__":
    main()
