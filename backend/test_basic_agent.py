#!/usr/bin/env python3
"""
Simple test to verify agent chat functionality works
"""

import requests
import json

def test_simple_agent_chat():
    """Test basic agent chat without complex automation"""
    
    base_url = "http://localhost:8002"
    
    # Simple test message
    test_message = "Hello, can you help me?"
    
    try:
        # Test the basic mcpai endpoint first
        response = requests.post(
            f"{base_url}/api/chat/mcpai",
            json={"message": test_message},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ MCPAI endpoint working:")
            print(f"   Response: {result.get('response', 'No response')[:100]}...")
            return True
        else:
            print(f"❌ MCPAI endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing basic agent functionality...")
    if test_simple_agent_chat():
        print("✅ Basic functionality confirmed")
    else:
        print("❌ Basic functionality broken")
