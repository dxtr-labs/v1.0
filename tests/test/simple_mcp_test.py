#!/usr/bin/env python3
"""
Simple test for the backend MCP API
"""

import requests
import json

def test_mcp_api():
    """Test the MCP API directly"""
    
    base_url = "http://localhost:8002"
    
    try:
        # Test workflow creation
        print("🧪 Testing MCP workflow creation...")
        create_payload = {
            "user_input": "Create an AI email automation to send a sales pitch to test@example.com",
            "conversation_history": []
        }
        
        response = requests.post(f"{base_url}/api/chat/mcpai", json=create_payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Workflow creation response:")
            print(f"   Status: {result.get('status', 'undefined')}")
            print(f"   Has workflow JSON: {result.get('hasWorkflowJson', False)}")
            print(f"   Has workflow preview: {result.get('hasWorkflowPreview', False)}")
            print(f"   Message: {result.get('message', 'No message')}")
            
            # Check response format
            required_fields = ['status', 'hasWorkflowJson', 'hasWorkflowPreview', 'workflowPreviewContent']
            missing_fields = [field for field in required_fields if field not in result]
            
            if missing_fields:
                print(f"⚠️  Missing fields: {missing_fields}")
            else:
                print("✅ All required fields present in response")
                
            # Print full response for debugging
            print(f"\n📋 Full response:")
            print(json.dumps(result, indent=2))
            
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Error: {response.text}")
                    
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")

if __name__ == "__main__":
    test_mcp_api()
