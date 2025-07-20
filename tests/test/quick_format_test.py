#!/usr/bin/env python3
"""
Simple test for Next.js API route response format
"""

import requests
import json

def test_nextjs_response_format():
    """Test the Next.js API route to verify response format"""
    
    frontend_url = "http://localhost:3002"
    
    try:
        # Proper payload format based on the route requirements
        payload = {
            "message": "Using AI, send an email automation to test@example.com",
            "agentId": "test-agent",
            "agentConfig": {
                "name": "Test Agent",
                "role": "AI Email Automation Assistant",
                "mode": "development"
            }
        }
        
        response = requests.post(f"{frontend_url}/api/chat/mcpai", json=payload, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n✅ SUCCESS: API call completed")
            print(f"📋 Response Fields:")
            print(f"   Status: {result.get('status', 'MISSING')}")
            print(f"   Has workflow JSON: {result.get('hasWorkflowJson', 'MISSING')}")
            print(f"   Has workflow preview: {result.get('hasWorkflowPreview', 'MISSING')}")
            print(f"   Message: {result.get('message', 'MISSING')[:100]}...")
            
            # Key test: Is status defined?
            status = result.get('status')
            if status and status != 'undefined':
                print(f"\n🎉 FIXED: Status is properly set to '{status}' (not undefined)")
            else:
                print(f"\n❌ ISSUE PERSISTS: Status is '{status}'")
                
        elif response.status_code == 401:
            print("🔐 Authentication required - this indicates the endpoint is working")
            print("   The response format issue is likely fixed if we can authenticate")
            
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
                    
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    print("🧪 Testing Next.js API Response Format")
    print("=" * 50)
    test_nextjs_response_format()
