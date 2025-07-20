#!/usr/bin/env python3
"""
Test agent chat with authentication
"""

import requests
import json

def test_agent_with_auth():
    """Test agent functionality with proper authentication"""
    
    base_url = "http://localhost:8002"
    
    # First login to get session
    print("🔐 Logging in...")
    login_response = requests.post(
        f"{base_url}/api/auth/login",
        json={
            "email": "suguanu24@gmail.com",
            "password": "test123"  # Use your actual password
        },
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
        return False
    
    print("✅ Login successful")
    
    # Get session cookie
    session_cookie = login_response.cookies.get('session')
    cookies = {'session': session_cookie} if session_cookie else {}
    
    # Get user info to verify session
    me_response = requests.get(
        f"{base_url}/api/auth/me",
        cookies=cookies
    )
    
    if me_response.status_code != 200:
        print(f"❌ Session verification failed: {me_response.status_code}")
        return False
    
    user_info = me_response.json()
    print(f"✅ Authenticated as: {user_info.get('email')}")
    
    # Get agents list
    agents_response = requests.get(
        f"{base_url}/api/agents",
        cookies=cookies
    )
    
    if agents_response.status_code != 200:
        print(f"❌ Failed to get agents: {agents_response.status_code}")
        return False
    
    agents = agents_response.json()
    if not agents:
        print("❌ No agents found")
        return False
    
    agent_id = agents[0]['agent_id']
    agent_name = agents[0]['agent_name']
    print(f"✅ Found agent: {agent_name} ({agent_id})")
    
    # Test agent chat
    print("💬 Testing agent chat...")
    chat_response = requests.post(
        f"{base_url}/api/agents/{agent_id}/chat",
        json={"message": "Hello! Can you help me?"},
        cookies=cookies,
        headers={"Content-Type": "application/json"}
    )
    
    if chat_response.status_code == 200:
        result = chat_response.json()
        print("✅ Agent chat working!")
        print(f"   Response: {result.get('response', 'No response')[:100]}...")
        print(f"   Status: {result.get('status', 'unknown')}")
        return True
    else:
        print(f"❌ Agent chat failed: {chat_response.status_code}")
        print(f"   Error: {chat_response.text}")
        return False

if __name__ == "__main__":
    print("🧪 Testing agent functionality with authentication...")
    if test_agent_with_auth():
        print("✅ Agent system working correctly!")
    else:
        print("❌ Agent system needs fixes")
