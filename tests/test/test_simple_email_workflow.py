#!/usr/bin/env python3
"""
Simple test to create an agent and then test email workflow
"""

import requests
import json
import time

def test_with_agent_creation():
    """Create an agent and test email workflow"""
    
    base_url = "http://localhost:8002"
    
    print("🧪 Testing Email Workflow with Agent Creation")
    print("=" * 50)
    
    # Step 1: Create a test agent
    print("👤 Step 1: Creating test agent...")
    
    agent_data = {
        "agent_name": "Email Test Agent",
        "agent_role": "Sales Specialist",
        "agent_personality": "Professional and knowledgeable about DXTR Labs",
        "agent_expectations": "Create compelling sales emails with company information"
    }
    
    try:
        # Try to create agent without authentication first
        create_response = requests.post(
            f"{base_url}/agents",
            json=agent_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📤 Create Agent Status: {create_response.status_code}")
        
        if create_response.status_code == 401:
            print("🔐 Authentication required - trying different endpoint...")
            
            # Try a test endpoint that might not require auth
            test_response = requests.get(f"{base_url}/api/test/health")
            print(f"🔍 Health Check Status: {test_response.status_code}")
            
            # Try the test agent chat endpoint directly
            print("📝 Testing direct agent chat with default agent...")
            
            # Use a common default agent ID pattern
            test_agent_id = "test_agent_123"
            
            draft_request = {
                "message": "draft a sales pitch email for DXTR Labs and send to slakshanand1105@gmail.com"
            }
            
            response = requests.post(
                f"{base_url}/api/test/agents/{test_agent_id}/chat",
                json=draft_request,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"📤 Test Chat Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response Status: {data.get('status')}")
                print(f"🔄 Response Keys: {list(data.keys())}")
                print(f"📝 Response: {data.get('response', 'No response')[:200]}...")
                
                if data.get('workflow_preview'):
                    print("🎉 Found workflow preview - testing email confirmation...")
                    email_preview = data['workflow_preview'].get('email_preview', {})
                    subject = email_preview.get('subject', 'Test Subject')
                    content = email_preview.get('content', 'Test Content')
                    
                    # Test email confirmation
                    confirm_request = {
                        "message": f"SEND_APPROVED_EMAIL:workflow_123:slakshanand1105@gmail.com:{subject}",
                        "email_content": content
                    }
                    
                    confirm_response = requests.post(
                        f"{base_url}/api/test/agents/{test_agent_id}/chat",
                        json=confirm_request,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    print(f"📮 Confirm Status: {confirm_response.status_code}")
                    if confirm_response.status_code == 200:
                        confirm_data = confirm_response.json()
                        print(f"✅ Email Sent: {confirm_data.get('email_sent', False)}")
                        print(f"📝 Final Response: {confirm_data.get('response', 'No response')}")
                    else:
                        print(f"❌ Confirm Failed: {confirm_response.text}")
            else:
                print(f"❌ Test Chat Failed: {response.text}")
                
        else:
            print(f"Agent creation response: {create_response.text}")
            
    except Exception as e:
        print(f"❌ Test Error: {e}")

if __name__ == "__main__":
    test_with_agent_creation()
