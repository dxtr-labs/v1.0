#!/usr/bin/env python3
"""
Test Complete Frontend-Backend Flow
Simulate the exact flow the user will experience
"""

import requests
import json
import time

BASE_URL = "http://localhost:8002"
FRONTEND_URL = "http://localhost:3000"

def test_complete_workflow():
    """Test the complete AI + Email workflow through frontend"""
    print("🧪 Testing Complete Frontend Workflow")
    print("=" * 50)
    
    # Step 1: Login via frontend
    print("🔐 Step 1: Logging in...")
    login_response = requests.post(
        f"{FRONTEND_URL}/api/auth/login",
        json={"email": "aitest@example.com", "password": "testpass123"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    cookies = login_response.cookies
    print("✅ Login successful")
    
    # Step 2: Send initial message that should trigger AI service selection
    print("\n🤖 Step 2: Sending AI + Email request...")
    
    message_payload = {
        "message": "Use AI to generate a sale pitch for our healthy ice cream and send email to slakshanand1105@gmail.com",
        "agentId": "test-agent",
        "agentConfig": {
            "name": "Sam",
            "role": "Personal Assistant"
        }
    }
    
    chat_response = requests.post(
        f"{FRONTEND_URL}/api/chat/mcpai",
        json=message_payload,
        cookies=cookies
    )
    
    if chat_response.status_code != 200:
        print(f"❌ Chat request failed: {chat_response.status_code}")
        print(f"Error: {chat_response.text}")
        return False
    
    chat_result = chat_response.json()
    print("✅ Initial message sent")
    print(f"Response status: {chat_result.get('status', 'unknown')}")
    print(f"Action required: {chat_result.get('action_required', 'none')}")
    
    # Check if AI service selection was triggered
    if chat_result.get('action_required') == 'select_ai_service':
        print("✅ AI service selection triggered correctly")
        ai_services = chat_result.get('ai_service_options', [])
        print(f"Available services: {[s.get('name') for s in ai_services]}")
        
        # Step 3: Select AI service (simulate clicking "Inhouse")
        print("\n⚙️ Step 3: Selecting AI service...")
        service_message = {
            "message": "service:inhouse Use AI to generate a sale pitch for our healthy ice cream and send email to slakshanand1105@gmail.com",
            "agentId": "test-agent",
            "agentConfig": {
                "name": "Sam",
                "role": "Personal Assistant"
            }
        }
        
        service_response = requests.post(
            f"{FRONTEND_URL}/api/chat/mcpai",
            json=service_message,
            cookies=cookies
        )
        
        if service_response.status_code != 200:
            print(f"❌ Service selection failed: {service_response.status_code}")
            return False
        
        service_result = service_response.json()
        print("✅ AI service selected")
        print(f"Response status: {service_result.get('status', 'unknown')}")
        print(f"Action required: {service_result.get('action_required', 'none')}")
        
        # Check if workflow confirmation is needed
        if 'workflow' in str(service_result) or service_result.get('action_required') == 'confirm_workflow':
            print("✅ Workflow generated and ready for confirmation")
            
            # Step 4: Confirm workflow execution
            print("\n✅ Step 4: Confirming workflow...")
            confirm_payload = {
                "agentId": "test-agent",
                "confirmed": True,
                "workflow_json": service_result.get('workflow_json', {})
            }
            
            confirm_response = requests.post(
                f"{FRONTEND_URL}/api/chat/mcpai/confirm",
                json=confirm_payload,
                cookies=cookies
            )
            
            if confirm_response.status_code != 200:
                print(f"❌ Workflow confirmation failed: {confirm_response.status_code}")
                print(f"Error: {confirm_response.text}")
                return False
            
            confirm_result = confirm_response.json()
            print("✅ Workflow confirmed and executed")
            print(f"Success: {confirm_result.get('success')}")
            print(f"Response: {confirm_result.get('response', 'No response')[:100]}...")
            
            return True
        else:
            print(f"⚠️ Expected workflow confirmation but got: {service_result}")
            return False
    else:
        print(f"⚠️ Expected AI service selection but got: {chat_result}")
        return False

if __name__ == "__main__":
    success = test_complete_workflow()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 COMPLETE WORKFLOW TEST PASSED!")
        print("✅ Frontend → Backend → AI Selection → Workflow → Email")
    else:
        print("❌ Workflow test failed - see details above")
