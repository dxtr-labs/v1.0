#!/usr/bin/env python3
"""Test the API response format after fixing backend response mapping"""

import requests
import json
import sys

def test_api_response():
    """Test the fixed API response format"""
    
    # Test with the user's exact request
    url = 'http://localhost:8002/api/chat/mcpai'
    data = {
        'user_input': 'draft a sales pitch email for selling the harmless antibiotics for animals and send email to slakshanand1105@gmail.com',
        'agentConfig': {
            'agent_id': 'sales_assistant',
            'name': 'Sales AI Assistant',
            'role': 'Professional Sales Agent'
        },
        'session_id': 'test_session_123'
    }
    
    try:
        print("🧪 Testing API Response Format...")
        print("📡 Sending request to backend...")
        
        response = requests.post(url, json=data, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n✅ API RESPONSE RECEIVED:")
            print("📋 Response Fields Analysis:")
            
            # Check for key fields that frontend expects
            expected_fields = [
                'status', 'hasWorkflowJson', 'hasWorkflowPreview', 
                'done', 'message', 'response', 'workflow_id',
                'automation_type', 'action_required'
            ]
            
            print(f"\n🔍 Checking for expected fields:")
            for field in expected_fields:
                value = result.get(field)
                status = "✅" if value is not None else "❌"
                print(f"  {status} {field}: {value}")
            
            print(f"\n📄 Full Response Structure:")
            for key, value in result.items():
                if key == 'response' and len(str(value)) > 100:
                    print(f"  {key}: {str(value)[:100]}...")
                else:
                    print(f"  {key}: {value}")
            
            # Test if this would trigger frontend automation
            has_workflow = result.get('hasWorkflowJson', False)
            has_preview = result.get('hasWorkflowPreview', False)
            status_ok = result.get('status') in ['completed', 'needs_parameters']
            
            print(f"\n🎯 Frontend Automation Trigger Analysis:")
            print(f"  hasWorkflowJson: {has_workflow}")
            print(f"  hasWorkflowPreview: {has_preview}")
            print(f"  status: {result.get('status')}")
            print(f"  Would trigger automation: {has_workflow or has_preview or status_ok}")
            
            if result.get('email_sent'):
                print(f"\n📧 Email Status: SENT ✅")
            
            return result
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"💥 Test Error: {e}")
        return None

if __name__ == "__main__":
    test_api_response()
