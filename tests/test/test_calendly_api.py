#!/usr/bin/env python3
"""
Simple test to verify Calendly functionality using HTTP requests
"""

import requests
import json

def test_calendly_via_api():
    """Test Calendly functionality via API"""
    
    print("🧪 Testing Calendly functionality via HTTP API...")
    
    # Use the Sam agent from the database
    agent_id = "467782cf-739d-4976-ad45-cb701548cc0f"
    test_request = "create a calendly link and send to slakshanand1105@gmail.com"
    
    url = f"http://localhost:8002/api/agents/{agent_id}/chat"
    headers = {"Content-Type": "application/json"}
    data = {"message": test_request}
    
    print(f"📝 Testing request: {test_request}")
    print(f"🎯 Agent ID: {agent_id}")
    print("=" * 60)
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ API RESPONSE SUCCESS:")
            print(f"Status: {result.get('status')}")
            print(f"Success: {result.get('success')}")
            
            response_text = result.get('message', '') or result.get('response', '')
            
            print("\n🔍 ANALYZING RESPONSE:")
            print(f"Contains 'calendly': {'calendly' in response_text.lower()}")
            print(f"Contains email address: {'slakshanand1105@gmail.com' in response_text}")
            print(f"Contains 'meeting': {'meeting' in response_text.lower()}")
            print(f"Contains 'schedule': {'schedule' in response_text.lower()}")
            
            print("\n📄 RESPONSE PREVIEW:")
            print(response_text[:300] + "..." if len(response_text) > 300 else response_text)
            
            # Check if this looks like a Calendly response
            calendly_indicators = [
                'calendly' in response_text.lower(),
                'meeting' in response_text.lower() or 'schedule' in response_text.lower(),
                'slakshanand1105@gmail.com' in response_text
            ]
            
            if all(calendly_indicators):
                print("\n🎉 SUCCESS: Calendly functionality is working!")
                print("✅ The system now generates proper meeting invitations instead of generic emails.")
                return True
            elif any(calendly_indicators):
                print("\n⚠️ PARTIAL SUCCESS: Some Calendly elements detected, but not complete.")
                return False
            else:
                print("\n❌ ISSUE: Response doesn't appear to be Calendly-specific")
                print("This looks like the old generic email behavior.")
                return False
        
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR during API test: {e}")
        return False

if __name__ == "__main__":
    success = test_calendly_via_api()
    if success:
        print("\n✅ CALENDLY FIX VERIFICATION: PASSED")
    else:
        print("\n❌ CALENDLY FIX VERIFICATION: FAILED")
        print("The custom MCP LLM is still generating generic emails instead of Calendly invitations.")
