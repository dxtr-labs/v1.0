#!/usr/bin/env python3
"""
Test Actual Email Delivery - Check if emails are being sent to the specified address
"""

import requests
import json
import time

def test_email_delivery():
    """Test if the email automation actually sends emails"""
    url = "http://localhost:8002/api/chat/mcpai"
    
    # Use valid session token for authentication
    session_token = 'XgThOdqavjspglvAqVO2vA4URIizlay9T8-2JzJnS3U'
    headers = {
        'Content-Type': 'application/json',
        'Cookie': f'session_token={session_token}'
    }
    
    payload = {
        "message": "Send a test email to slakshanand1105@gmail.com with subject 'Test Email from Automation System' and message 'This is a test email to verify the automation system is working properly.'",
        "agentConfig": {
            "agent_id": "sales_assistant",
            "name": "Sales AI Assistant", 
            "role": "Professional Sales Agent"
        },
        "session_id": "test_session_123"
    }
    
    print("🧪 Testing Actual Email Delivery")
    print("=" * 50)
    print(f"URL: {url}")
    print(f"Target Email: slakshanand1105@gmail.com")
    print(f"Test Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    try:
        print("📤 Sending request...")
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print("✅ API Response:")
            print(json.dumps(response_data, indent=2))
            
            # Extract key information
            automation_type = response_data.get('automation_type', 'NOT_FOUND')
            email_sent = response_data.get('email_sent', 'NOT_FOUND') 
            execution_status = response_data.get('execution_status', 'NOT_FOUND')
            workflow_id = response_data.get('workflow_id', 'NOT_FOUND')
            
            print(f"\n🔍 Email Delivery Analysis:")
            print(f"  - Automation Type: {automation_type}")
            print(f"  - Email Sent: {email_sent}")
            print(f"  - Execution Status: {execution_status}")
            print(f"  - Workflow ID: {workflow_id}")
            
            # Analyze the results
            if automation_type == "completed_workflow":
                print(f"\n✅ SUCCESS: Automation workflow was properly triggered!")
                
                if email_sent is True:
                    print(f"✅ EMAIL CONFIRMED: Email was successfully sent!")
                    print(f"📧 Check slakshanand1105@gmail.com for the test email")
                elif email_sent is False:
                    print(f"❌ EMAIL FAILED: Workflow executed but email was not sent")
                    print(f"💡 Issue: Email delivery mechanism might have failed")
                elif email_sent is None or email_sent == 'NOT_FOUND':
                    print(f"⚠️ EMAIL UNKNOWN: Email status not reported in response")
                    print(f"💡 Issue: Email execution status not being tracked properly")
                
                if execution_status == "completed":
                    print(f"✅ EXECUTION: Workflow execution completed successfully")
                else:
                    print(f"❌ EXECUTION: Workflow execution status: {execution_status}")
                    
            elif automation_type == "conversational":
                print(f"❌ FAILED: Request was treated as conversation, not automation")
                print(f"💡 Issue: Automation detection is not working properly")
            else:
                print(f"⚠️ UNKNOWN: Unexpected automation type: {automation_type}")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

    print("\n" + "=" * 50)
    print("📋 Next Steps:")
    print("1. Check your email inbox at slakshanand1105@gmail.com")
    print("2. Look for emails with subject 'Test Email from Automation System'")
    print("3. If no email arrives, there's likely an SMTP delivery issue")
    print("4. Check backend logs for detailed error messages")

if __name__ == "__main__":
    test_email_delivery()
