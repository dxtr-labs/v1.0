#!/usr/bin/env python3
"""
Direct test using an agent from the database to verify email_configured fix
"""

import requests
import json

def test_agent_response():
    """Test agent chat without creating new agent"""
    
    base_url = "http://localhost:8002"
    
    # Test with a simple HR message that should trigger MCP
    test_message = {
        "message": "Hello! I'm Sam, your HR Manager. Can you help me send a recruitment email to a candidate at test@example.com about joining DXTR Labs?"
    }
    
    print("🧪 Testing Agent Response with MCP Fix")
    print("=" * 50)
    print(f"📝 Message: {test_message['message']}")
    
    try:
        # Use the simple test chat endpoint
        response = requests.post(
            f"{base_url}/api/test/chat",
            json=test_message,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📤 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('success', False)}")
            print(f"📝 Status: {data.get('status', 'unknown')}")
            print(f"💬 Response: {data.get('response', 'No response')}")
            
            # Check for specific signs that our fix worked
            response_text = str(data)
            if 'email_configured' in response_text.lower():
                print("❌ Still contains email_configured references")
            else:
                print("✅ No email_configured errors detected!")
                
            if data.get('success'):
                print("🎉 MCP engine is responding without errors!")
                
        else:
            print(f"❌ Request failed: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - check backend processing")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_agent_response()
