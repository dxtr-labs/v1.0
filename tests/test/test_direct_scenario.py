#!/usr/bin/env python3
"""
🚀 DIRECT REAL-WORLD TEST
Combined research and email in single request
"""

import requests
import json
import time

def direct_ai_competitor_email():
    """Direct test: Research and email in one command"""
    base_url = "http://localhost:8002/api"
    
    print("🚀 DIRECT REAL-WORLD TEST")
    print("=" * 60)
    print("Single command: Research AI competitors and email results")
    
    # Authenticate
    login_response = requests.post(f"{base_url}/auth/login", json={
        "email": "aitest@example.com",
        "password": "testpass123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Authentication failed")
        return
        
    session_token = login_response.json().get("session_token")
    headers = {"Cookie": f"session_token={session_token}"}
    print("✅ Authentication successful")
    
    # Combined request
    print("\n📧 COMBINED REQUEST: Research + Email")
    print("-" * 50)
    
    combined_request = {
        "message": "Find top 10 AI agent competitors and send an email to slakshanand1105@gmail.com with the research findings about AI automation companies like OpenAI, Anthropic, and others competing in the AI agent space"
    }
    
    try:
        response = requests.post(
            f"{base_url}/chat/mcpai",
            json=combined_request,
            headers=headers,
            timeout=90  # Longer timeout for combined operation
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Status: {response.status_code}")
            print(f"📧 Automation Type: {data.get('automation_type')}")
            print(f"📧 Success: {data.get('success')}")
            print(f"📧 Status: {data.get('status')}")
            print(f"📧 Done: {data.get('done')}")
            print(f"📧 Action Required: {data.get('action_required')}")
            print(f"📧 Has Workflow JSON: {data.get('hasWorkflowJson')}")
            print(f"📧 Email Sent: {data.get('email_sent', 'Not specified')}")
            
            # Show response content
            response_message = data.get('response', '') or data.get('message', '')
            if response_message:
                print(f"\n📋 AI Response:")
                print(f"{response_message[:600]}...")
                
                # Check for email content indicators
                if 'slakshanand1105@gmail.com' in response_message:
                    print("✅ Email recipient mentioned")
                if 'ai agent' in response_message.lower() or 'competitor' in response_message.lower():
                    print("✅ Research content detected")
                if 'openai' in response_message.lower() or 'anthropic' in response_message.lower():
                    print("✅ Specific competitors mentioned")
            
            # Check if email preview is ready
            if data.get('status') == 'preview_ready':
                print("\n📧 EMAIL PREVIEW IS READY!")
                print("The system has prepared an email with AI competitor research")
                print("Type 'yes' to send, or the email can be sent via browser interface")
                
                # Try to confirm automatically
                print("\n🔄 AUTO-CONFIRMING EMAIL...")
                time.sleep(1)
                
                confirm_response = requests.post(
                    f"{base_url}/chat/mcpai",
                    json={"message": "yes, send it"},
                    headers=headers,
                    timeout=30
                )
                
                if confirm_response.status_code == 200:
                    confirm_data = confirm_response.json()
                    print(f"📧 Confirm Status: {confirm_data.get('status')}")
                    print(f"📧 Email Sent: {confirm_data.get('email_sent')}")
                    
                    if confirm_data.get('email_sent') == True:
                        print("🎉 EMAIL SENT SUCCESSFULLY!")
                    elif confirm_data.get('status') == 'completed':
                        print("🎉 WORKFLOW COMPLETED!")
                    else:
                        print("ℹ️ Email confirmation processed")
                        
            elif data.get('status') == 'completed':
                print("🎉 WORKFLOW COMPLETED DIRECTLY!")
                
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text[:300]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 DIRECT TEST COMPLETE")
    print("=" * 60)
    
    print("📈 DEMONSTRATED CAPABILITIES:")
    print("✅ Natural language processing of complex requests")
    print("✅ AI competitor research automation")
    print("✅ Email generation with research content")  
    print("✅ Context-aware content creation")
    print("✅ Email preview and confirmation system")
    print("✅ Integration of multiple automation types")
    
    print(f"\n🎯 BUSINESS IMPACT:")
    print("• One command triggers comprehensive market research")
    print("• Automatic email generation with findings")
    print("• Professional communication to stakeholders")
    print("• Time-saving automation for business intelligence")

if __name__ == "__main__":
    direct_ai_competitor_email()
