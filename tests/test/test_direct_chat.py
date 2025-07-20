#!/usr/bin/env python3
"""
Direct test of the test agent chat endpoint
"""

import requests
import json

def test_direct_agent_chat():
    """Test agent chat endpoint directly"""
    
    base_url = "http://localhost:8002"
    agent_id = "550e8400-e29b-41d4-a716-446655440000"  # Valid UUID format
    
    print("🧪 Testing Direct Agent Chat")
    print("=" * 30)
    
    # Test the agent chat endpoint
    draft_request = {
        "message": "draft a sales pitch email for DXTR Labs and send to slakshanand1105@gmail.com"
    }
    
    try:
        print(f"📤 Testing: POST {base_url}/api/test/agents/{agent_id}/chat")
        
        response = requests.post(
            f"{base_url}/api/test/agents/{agent_id}/chat",
            json=draft_request,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📤 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response Status: {data.get('status')}")
            print(f"🔍 Response Keys: {list(data.keys())}")
            
            if 'workflow_preview' in data:
                print("🎉 Workflow preview found!")
                email_preview = data['workflow_preview'].get('email_preview', {})
                print(f"📧 Subject: {email_preview.get('subject', 'No subject')}")
                print(f"📧 Content: {email_preview.get('content', 'No content')[:100]}...")
            else:
                print(f"📝 Response: {data.get('response', 'No response')}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_direct_agent_chat()
