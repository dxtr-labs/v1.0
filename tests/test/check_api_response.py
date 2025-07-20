#!/usr/bin/env python3
"""
🔍 CHECK ACTUAL API RESPONSE STRUCTURE
Debug what the actual API returns for automation requests
"""

import requests
import json

def test_actual_response():
    """Test the actual API response structure"""
    
    base_url = "http://localhost:8002"
    
    # Login first
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "email": "aitest@example.com",
        "password": "testpass123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    session_token = login_response.json().get("session_token")
    headers = {"Cookie": f"session_token={session_token}"}
    
    # Test automation request
    payload = {"message": "Send an email to slakshanand1105@gmail.com about our TechCorp protein noodles"}
    
    print("🧪 TESTING AUTOMATION REQUEST")
    print("=" * 50)
    print(f"Message: {payload['message']}")
    
    response = requests.post(f"{base_url}/api/chat/mcpai", 
        json=payload,
        headers=headers,
        timeout=30
    )
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n📋 FULL RESPONSE STRUCTURE:")
        print(json.dumps(result, indent=2))
        
        print(f"\n🔍 KEY ANALYSIS:")
        print(f"   Keys present: {list(result.keys())}")
        
        # Check for workflow indicators
        workflow_indicators = []
        if 'workflow' in result:
            workflow_indicators.append(f"workflow: {type(result['workflow'])}")
        if 'hasWorkflowJson' in result:
            workflow_indicators.append(f"hasWorkflowJson: {result['hasWorkflowJson']}")
        if 'workflow_json' in result:
            workflow_indicators.append(f"workflow_json: {type(result['workflow_json'])}")
        if 'automation_type' in result:
            workflow_indicators.append(f"automation_type: {result['automation_type']}")
        if 'status' in result:
            workflow_indicators.append(f"status: {result['status']}")
            
        if workflow_indicators:
            print(f"   Workflow indicators: {workflow_indicators}")
        else:
            print(f"   ❌ No workflow indicators found")
            
        # Check message content for automation indicators
        message = result.get('message', '')
        if 'automation created' in message.lower():
            print(f"   ✅ Message contains 'automation created'")
        if 'workflow' in message.lower():
            print(f"   ✅ Message contains 'workflow'")
        if 'email' in message.lower():
            print(f"   ✅ Message contains 'email'")
            
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_actual_response()
