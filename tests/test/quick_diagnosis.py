#!/usr/bin/env python3
"""
QUICK SYSTEM DIAGNOSIS - CHECK WHAT'S MISSING
"""

import requests
import json
import uuid

def diagnose_system():
    """Diagnose what's wrong with the system"""
    base_url = "http://localhost:8002"
    
    print("🔍 SYSTEM DIAGNOSIS")
    print("=" * 50)
    
    # Create user
    test_email = f"diaguser_{uuid.uuid4().hex[:6]}@example.com"
    signup_data = {"email": test_email, "password": "test123", "name": "Diag User"}
    
    signup_response = requests.post(f"{base_url}/api/auth/signup", json=signup_data)
    
    if signup_response.status_code == 200:
        user_data = signup_response.json()
        user_id = user_data.get("user", {}).get("user_id")
        headers = {"x-user-id": str(user_id)}
        
        print(f"✅ User created: {user_id}")
        
        # Test 1: Simple message
        print("\n📝 Test 1: Simple message")
        simple_response = requests.post(f"{base_url}/api/chat/mcpai", 
                                      json={"message": "Hello, how are you?"}, 
                                      headers=headers, timeout=30)
        
        print(f"Status: {simple_response.status_code}")
        if simple_response.status_code == 200:
            data = simple_response.json()
            print(f"Success: {data.get('success')}")
            print(f"Response: {data.get('response', 'No response')[:200]}...")
            print(f"Agent ID: {data.get('agentId', 'No agent ID')}")
            
            # Check for any error messages or review needed
            if data.get('status') == 'review_needed':
                print("⚠️ Review needed - this might indicate configuration issues")
            if data.get('error'):
                print(f"❌ Error: {data.get('error')}")
        else:
            print(f"❌ Failed: {simple_response.text}")
        
        # Test 2: Check agents
        print("\n👤 Test 2: Check agents")
        agents_response = requests.get(f"{base_url}/api/agents", headers=headers)
        print(f"Agents status: {agents_response.status_code}")
        if agents_response.status_code == 200:
            agents_data = agents_response.json()
            print(f"Agents count: {len(agents_data.get('agents', []))}")
            for agent in agents_data.get('agents', [])[:3]:  # Show first 3
                print(f"  - {agent.get('agent_name', 'No name')} (ID: {agent.get('agent_id', 'No ID')[:8]}...)")
        
        # Test 3: Check email parameters
        print("\n📧 Test 3: Check email API parameters")
        # Test with correct email parameters
        email_data = {
            "to": "slakshanand1105@gmail.com",
            "subject": "Test Email",
            "content": "This is a test email content."  # Changed from 'body' to 'content'
        }
        email_response = requests.post(f"{base_url}/api/email/send", json=email_data, headers=headers, timeout=30)
        print(f"Email status: {email_response.status_code}")
        print(f"Email response: {email_response.text[:300]}...")
        
        # Test 4: Check automation templates
        print("\n🔧 Test 4: Check automation templates")
        templates_response = requests.get(f"{base_url}/api/automation/templates", headers=headers)
        print(f"Templates status: {templates_response.status_code}")
        if templates_response.status_code == 200:
            templates_data = templates_response.json()
            print(f"Templates available: {len(templates_data.get('templates', []))}")
        
        # Test 5: Search with debug info
        print("\n🔍 Test 5: Search with more detailed check")
        search_message = "Search for information about AI companies"  # Simpler search
        search_response = requests.post(f"{base_url}/api/chat/mcpai", 
                                      json={"message": search_message}, 
                                      headers=headers, timeout=60)
        
        print(f"Search status: {search_response.status_code}")
        if search_response.status_code == 200:
            search_data = search_response.json()
            print(f"Search success: {search_data.get('success')}")
            print(f"Search status: {search_data.get('status', 'No status')}")
            print(f"Search response length: {len(search_data.get('response', ''))}")
            print(f"Search response: {search_data.get('response', 'No response')[:500]}...")
            
            # Check for workflow or agent info
            if search_data.get('workflowId'):
                print(f"Workflow ID: {search_data.get('workflowId')}")
            if search_data.get('agentId'):
                print(f"Agent ID: {search_data.get('agentId')}")
            if search_data.get('error'):
                print(f"Error: {search_data.get('error')}")
        else:
            print(f"❌ Search failed: {search_response.text}")
    
    else:
        print(f"❌ User creation failed: {signup_response.text}")

if __name__ == "__main__":
    diagnose_system()
