#!/usr/bin/env python3
"""
Debug which agent is being used and its configuration
"""

import requests
import json

def debug_agent_configuration():
    """Debug the current agent configuration"""
    print("🔍 DEBUGGING AGENT CONFIGURATION")
    print("=" * 60)
    
    base_url = "http://localhost:8002"
    
    # Login
    print("🔐 Authenticating...")
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "email": "aitest@example.com",
        "password": "testpass123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return False
    
    session_token = login_response.json().get("session_token")
    headers = {"Cookie": f"session_token={session_token}"}
    print("✅ Authentication successful")
    
    # Get available agents
    print(f"\n📋 Getting available agents...")
    try:
        agents_response = requests.get(f"{base_url}/api/agents", headers=headers)
        if agents_response.status_code == 200:
            agents = agents_response.json().get('agents', [])
            print(f"Found {len(agents)} agents:")
            
            for i, agent in enumerate(agents):
                print(f"\n🤖 Agent {i+1}:")
                print(f"   ID: {agent.get('id')}")
                print(f"   Name: {agent.get('name')}")
                print(f"   Role: {agent.get('role')}")
                print(f"   Description: {agent.get('description', '')[:100]}...")
                
                # Check if this agent has company/app context
                config = agent.get('config', {})
                system_prompt = config.get('system_prompt', '')
                
                has_roomify = 'roomify' in system_prompt.lower()
                has_pranay = 'pranay' in system_prompt.lower()
                print(f"   Has Roomify context: {'✅' if has_roomify else '❌'}")
                print(f"   Has Pranay context: {'✅' if has_pranay else '❌'}")
                
                if has_roomify or has_pranay:
                    print(f"   System Prompt: {system_prompt}")
            
            return agents
        else:
            print(f"❌ Failed to get agents: {agents_response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error getting agents: {e}")
        return []

def test_email_with_current_agent():
    """Test email generation with current agent"""
    print(f"\n📧 TESTING EMAIL WITH CURRENT AGENT")
    print("=" * 60)
    
    base_url = "http://localhost:8002"
    
    # Login
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "email": "aitest@example.com",
        "password": "testpass123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return False
    
    session_token = login_response.json().get("session_token")
    headers = {"Cookie": f"session_token={session_token}"}
    
    # Test the exact message that's failing
    test_message = """i am ceo pranay, draft a sales pitch email for our app roomify and send to slakshanand1105@gmail.com"""
    
    print(f"📤 Sending request: {test_message}")
    
    try:
        response = requests.post(f"{base_url}/api/chat/mcpai",
            json={"message": test_message},
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n📋 RESPONSE ANALYSIS:")
            print("=" * 50)
            
            message = result.get('message', '')
            email_content = result.get('email_content', '')
            
            print(f"Message contains 'roomify': {'✅' if 'roomify' in message.lower() else '❌'}")
            print(f"Message contains 'pranay': {'✅' if 'pranay' in message.lower() else '❌'}")
            print(f"Message contains 'app': {'✅' if 'app' in message.lower() else '❌'}")
            print(f"Message contains 'None': {'❌' if 'None' in message else '✅'}")
            
            print(f"\n📝 EMAIL CONTENT PREVIEW:")
            print("-" * 40)
            print(email_content[:300] if email_content else message[:300])
            print("-" * 40)
            
            # Check if it's using generic template
            is_generic = ('None' in message and 
                         'high-quality solutions for our clients' in message and
                         'quality, innovation, and customer satisfaction' in message)
            
            print(f"\n🎯 ISSUE IDENTIFICATION:")
            print(f"Generic template detected: {'❌ YES' if is_generic else '✅ NO'}")
            
            if is_generic:
                print(f"\n🔧 PROBLEM: Agent is using generic template instead of:")
                print(f"   - Company: Roomify (app)")
                print(f"   - CEO: Pranay")
                print(f"   - Context: App sales pitch")
                
                return False
            else:
                print(f"\n✅ Agent is using specific context correctly")
                return True
                
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 AGENT CONFIGURATION DEBUG SESSION")
    print("=" * 70)
    
    # Test 1: Check current agents
    agents = debug_agent_configuration()
    
    # Test 2: Test email generation
    email_result = test_email_with_current_agent()
    
    print(f"\n🏁 DIAGNOSIS:")
    print("=" * 30)
    
    if not email_result:
        print(f"❌ ISSUE: Agent is not using company context")
        print(f"🔧 SOLUTIONS:")
        print(f"   1. Create agent with Roomify context")
        print(f"   2. Add agent_notes field with company info")
        print(f"   3. Update system prompt to include Pranay/Roomify details")
    else:
        print(f"✅ Agent context working correctly!")
