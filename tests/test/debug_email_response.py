#!/usr/bin/env python3
"""
Debug the email workflow response structure
"""

import requests
import json

def debug_email_response():
    """Debug the email workflow response"""
    
    base_url = "http://localhost:8002"
    agent_id = "26cdf155-efb6-4f1a-b6ee-eef449888424"  # From previous test
    
    print("🔍 Debugging Email Workflow Response")
    print("=" * 40)
    
    draft_request = {
        "message": "draft a sales pitch email for DXTR Labs highlighting our AI automation capabilities and send to slakshanand1105@gmail.com"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/test/agents/{agent_id}/chat",
            json=draft_request,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📤 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"🔍 Full Response Structure:")
            print(json.dumps(data, indent=2))
            
            print(f"\n📊 Response Analysis:")
            print(f"  Status: {data.get('status')}")
            print(f"  Response: {data.get('response', 'No response')}")
            print(f"  Success: {data.get('success')}")
            print(f"  Done: {data.get('done')}")
            
            print(f"\n🔎 All Keys: {list(data.keys())}")
            
            # Check if there's any email-related data
            for key, value in data.items():
                if 'email' in key.lower() or 'workflow' in key.lower():
                    print(f"  📧 {key}: {value}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    debug_email_response()
