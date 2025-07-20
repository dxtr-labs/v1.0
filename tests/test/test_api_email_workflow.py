#!/usr/bin/env python3
"""
Test the complete email workflow via API: 
1. Request email draft 
2. Get editable preview
3. Confirm and send email
"""

import requests
import json
import time

def test_api_email_workflow():
    """Test the complete email automation workflow via API"""
    
    base_url = "http://localhost:8002"
    agent_id = "550e8400-e29b-41d4-a716-446655440000"  # Default agent ID
    
    print("🧪 Testing Complete Email Workflow via API")
    print("=" * 50)
    
    # Step 1: Request email draft with DXTR Labs company info
    print("📝 Step 1: Requesting email draft...")
    
    draft_request = {
        "message": "draft a sales pitch email highlighting key points of our company and send email to slakshanand1105@gmail.com"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/agents/{agent_id}/chat",
            json=draft_request,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📤 Draft Request Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response Status: {data.get('status')}")
            print(f"🔄 Workflow Preview: {bool(data.get('workflow_preview'))}")
            
            if data.get('workflow_preview'):
                email_preview = data['workflow_preview'].get('email_preview', {})
                subject = email_preview.get('subject', 'No Subject')
                content = email_preview.get('content', 'No Content')
                
                print(f"📧 Email Subject: {subject}")
                print(f"📧 Email Content Preview: {content[:100]}...")
                
                # Step 2: Confirm and send the email
                print("\n📮 Step 2: Confirming and sending email...")
                
                confirm_request = {
                    "message": f"SEND_APPROVED_EMAIL:workflow_123:slakshanand1105@gmail.com:{subject}",
                    "email_content": content
                }
                
                confirm_response = requests.post(
                    f"{base_url}/api/agents/{agent_id}/chat",
                    json=confirm_request,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"📤 Confirm Request Status: {confirm_response.status_code}")
                
                if confirm_response.status_code == 200:
                    confirm_data = confirm_response.json()
                    print(f"✅ Final Status: {confirm_data.get('status')}")
                    print(f"📧 Email Sent: {confirm_data.get('email_sent', False)}")
                    print(f"🎯 Message: {confirm_data.get('message', 'No message')}")
                    
                    if confirm_data.get('email_sent'):
                        print("🎉 SUCCESS: Email automation workflow completed!")
                        print(f"📬 Recipient: {confirm_data.get('recipient')}")
                        print(f"📝 Subject: {confirm_data.get('subject')}")
                    else:
                        print("❌ FAILURE: Email was not sent")
                        print(f"📝 Response: {confirm_data.get('response')}")
                else:
                    print(f"❌ Confirm Request Failed: {confirm_response.text}")
            else:
                print("❌ No workflow preview found in response")
                print(f"📝 Response: {data.get('response', 'No response')}")
        else:
            print(f"❌ Draft Request Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Test Error: {e}")

if __name__ == "__main__":
    test_api_email_workflow()
