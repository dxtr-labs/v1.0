#!/usr/bin/env python3
"""
Debug the full agent manager flow
"""

import sys
import os
import asyncio

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_agent_manager():
    print("🧪 Testing agent manager flow")
    
    try:
        from mcp.agent_manager import agent_manager
        
        # Test the exact same message and agent
        agent_id = "16df81d1"
        user_id = "default_user"
        message = "generate cold email to sell architecture services and send to slakshanand1105@gmail.com"
        
        print(f"Agent ID: {agent_id}")
        print(f"User ID: {user_id}")
        print(f"Message: {message}")
        
        # Get the agent
        agent = agent_manager.get_agent(agent_id, user_id)
        if not agent:
            print(f"❌ Agent {agent_id} not found")
            return
        
        print(f"✅ Found agent: {agent.name} ({agent.role})")
        print(f"Agent capabilities: {agent.capabilities}")
        
        # Call the chat method
        response = await agent_manager.chat_with_agent(agent_id, message, user_id)
        
        print(f"Agent manager response: {response}")
        
        if response.get('success'):
            metadata = response.get('metadata', {})
            print(f"Metadata: {metadata}")
            if metadata.get('needs_confirmation'):
                print("✅ AI confirmation detected in metadata!")
            else:
                print("❌ No AI confirmation in metadata")
        else:
            print(f"❌ Agent manager failed: {response.get('error')}")
        
    except Exception as e:
        print(f"❌ Error testing agent manager: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent_manager())
