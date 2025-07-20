#!/usr/bin/env python3
"""
Quick test to verify agent chat fix
"""

import requests
import json

def test_agent_chat():
    """Test agent chat functionality"""
    
    print("🧪 Testing Agent Chat Fix")
    print("=" * 40)
    
    # First, get list of agents
    try:
        agents_response = requests.get("http://localhost:8002/api/agents")
        if agents_response.status_code == 200:
            agents = agents_response.json()
            print(f"✅ Found {len(agents)} agents")
            
            if agents:
                # Test with first agent
                agent_id = agents[0]['agent_id']
                agent_name = agents[0].get('agent_name', 'Unknown')
                
                print(f"📱 Testing chat with agent: {agent_name} (ID: {agent_id})")
                
                # Test chat message
                chat_response = requests.post(
                    f"http://localhost:8002/api/agents/{agent_id}/chat",
                    json={"message": "Hello! Can you help me?"},
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"Status Code: {chat_response.status_code}")
                
                if chat_response.status_code == 200:
                    result = chat_response.json()
                    print("✅ Agent chat working!")
                    print(f"Response: {result.get('response', 'No response')[:100]}...")
                    return True
                else:
                    print(f"❌ Chat failed: {chat_response.text}")
                    return False
            else:
                print("❌ No agents found")
                return False
        else:
            print(f"❌ Failed to get agents: {agents_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_agent_chat()
    if success:
        print("\n🎉 AGENT CHAT FIX SUCCESSFUL!")
    else:
        print("\n❌ Agent chat still has issues")
