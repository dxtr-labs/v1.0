#!/usr/bin/env python3
"""
Debug API Request - Test what's actually being sent to the backend
"""

import requests
import json

def test_api_request():
    url = "http://localhost:8002/api/chat/mcpai"
    
    # Use valid session token for authentication
    session_token = 'XgThOdqavjspglvAqVO2vA4URIizlay9T8-2JzJnS3U'
    headers = {
        'Content-Type': 'application/json',
        'Cookie': f'session_token={session_token}'
    }
    
    payload = {
        "message": "Send a sales pitch email to slakshanand1105@gmail.com about animal antibiotics, focusing on quality and trust",
        "agentConfig": {
            "agent_id": "sales_assistant",
            "name": "Sales AI Assistant", 
            "role": "Professional Sales Agent"
        },
        "session_id": "test_session_123"
    }
    
    print("🔍 Testing API Request Debug")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print("-" * 50)
        
        if response.status_code == 200:
            response_data = response.json()
            print("✅ Response received:")
            print(json.dumps(response_data, indent=2))
            
            # Check what automation type is being returned
            automation_type = response_data.get('automation_type', 'NOT_FOUND')
            email_sent = response_data.get('email_sent', 'NOT_FOUND')
            status = response_data.get('status', 'NOT_FOUND')
            
            print(f"\n🔍 Key Fields Analysis:")
            print(f"  - automation_type: {automation_type}")
            print(f"  - email_sent: {email_sent}")
            print(f"  - status: {status}")
            
            if automation_type == "conversational":
                print("\n❌ ISSUE: Request is being processed as 'conversational' instead of 'ai_email'")
                print("   This means the email automation workflow is not being triggered")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_api_request()
