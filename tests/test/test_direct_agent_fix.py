#!/usr/bin/env python3
"""
Direct test of specific agent chat with the ID from the error
"""

import requests
import json

def test_specific_agent():
    """Test specific agent chat"""
    
    print("🧪 Testing Specific Agent Chat")
    print("=" * 40)
    
    # Use the agent ID from the error message
    agent_id = "a99f903c-1fa5-4dc5-b15a-ec716b9a161a"
    
    try:
        # Test chat message directly
        chat_response = requests.post(
            f"http://localhost:8002/api/agents/{agent_id}/chat",
            json={"message": "Hello! Can you help me test this?"},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {chat_response.status_code}")
        
        if chat_response.status_code == 200:
            result = chat_response.json()
            print("✅ Agent chat working!")
            print(f"Response: {result.get('response', 'No response')[:200]}...")
            print(f"Status: {result.get('status', 'Unknown')}")
            return True
        elif chat_response.status_code == 404:
            print(f"❌ Agent not found (404) - Agent ID may not exist")
            return False
        elif chat_response.status_code == 500:
            print(f"❌ Server error (500): {chat_response.text}")
            return False
        else:
            print(f"❌ Chat failed with status {chat_response.status_code}: {chat_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_mcpai_endpoint():
    """Test MCPAI endpoint as fallback"""
    
    print("\n🧪 Testing MCPAI Endpoint")
    print("=" * 40)
    
    try:
        response = requests.post(
            "http://localhost:8002/api/chat/mcpai",
            json={"message": "Hello! Test message"},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ MCPAI endpoint working!")
            print(f"Response: {result.get('response', 'No response')[:200]}...")
            return True
        else:
            print(f"❌ MCPAI failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ MCPAI test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing CustomMCPLLMIterationEngine parameter fix...")
    
    agent_success = test_specific_agent()
    mcpai_success = test_mcpai_endpoint()
    
    if agent_success:
        print("\n🎉 AGENT CHAT FIX SUCCESSFUL!")
    elif mcpai_success:
        print("\n✅ MCPAI working, agent endpoint may need specific agent")
    else:
        print("\n❌ Both endpoints still have issues")
