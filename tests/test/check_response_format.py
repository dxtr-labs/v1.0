#!/usr/bin/env python3
"""
Check the exact response format from the backend to update frontend logic
"""

import requests
import json

def check_backend_response_format():
    """Get the exact response format to update frontend detection"""
    print("🔍 CHECKING EXACT BACKEND RESPONSE FORMAT")
    print("=" * 60)
    
    # Login
    print("🔐 Authenticating...")
    login_response = requests.post("http://localhost:8002/api/auth/login", json={
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
    
    print(f"\n📤 Sending email request...")
    
    try:
        response = requests.post("http://localhost:8002/api/chat/mcpai",
            json={"message": test_message},
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n📋 COMPLETE RESPONSE STRUCTURE:")
            print("=" * 50)
            print(json.dumps(result, indent=2))
            
            print(f"\n🎯 FRONTEND DETECTION CONDITIONS:")
            print("=" * 50)
            
            # Check all the conditions the frontend is looking for
            conditions = [
                ("data.type === 'email_preview'", result.get('type') == 'email_preview'),
                ("data.execution.execution.preview_data", 
                 result.get('execution', {}).get('execution', {}).get('preview_data') is not None),
                ("data.preview_data + action_required", 
                 result.get('preview_data') is not None and result.get('action_required') == 'email_preview_confirmation'),
                ("data.automation_result.execution.preview_data", 
                 result.get('automation_result', {}).get('execution', {}).get('preview_data') is not None),
                ("data.execution.preview_data", 
                 result.get('execution', {}).get('preview_data') is not None),
                ("Text indicators (Click 'Confirm & Send')", 
                 'Click \'Confirm & Send\'' in str(result.get('response', ''))),
                ("data.email_content + data.recipient", 
                 result.get('email_content') is not None and result.get('recipient') is not None),
            ]
            
            found_condition = False
            for condition_name, condition_result in conditions:
                status = "✅ YES" if condition_result else "❌ NO"
                print(f"   {condition_name}: {status}")
                if condition_result:
                    found_condition = True
            
            print(f"\n🏁 RESULT:")
            if found_condition:
                print("✅ At least one frontend detection condition is met!")
                print("📧 The email preview dialog should trigger")
            else:
                print("❌ No frontend detection conditions are met")
                print("🔧 Frontend logic needs to be updated")
                
                # Suggest a fix
                print(f"\n💡 SUGGESTED FIX:")
                print("Add this condition to the frontend checkForEmailPreview function:")
                print("if (data.email_content && data.recipient) {")
                print("    return {")
                print("        preview_data: {")
                print("            to_email: data.recipient,")
                print("            subject: data.email_subject || 'Generated Email',")
                print("            content: data.email_content")
                print("        },")
                print("        action_required: 'email_preview_confirmation',")
                print("        message: 'Email ready for review'")
                print("    };")
                print("}")
            
            return found_condition
            
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = check_backend_response_format()
    
    if success:
        print(f"\n✅ Backend response analysis complete!")
    else:
        print(f"\n❌ Failed to analyze backend response")
