#!/usr/bin/env python3
"""
Test both generic and agent-specific endpoints for email preview dialog trigger
"""

import requests
import json

def test_both_endpoints_preview_trigger():
    """Test both endpoints to see which one triggers the email preview dialog"""
    print("🔍 TESTING BOTH ENDPOINTS FOR EMAIL PREVIEW DIALOG")
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
    
    # Get agent ID
    agents_response = requests.get(f"{base_url}/api/agents", headers=headers)
    if agents_response.status_code != 200:
        print("❌ Failed to get agents")
        return False
    
    agents = agents_response.json().get('agents', [])
    if not agents:
        print("❌ No agents found")
        return False
    
    agent = agents[0]
    agent_id = agent.get('id')
    print(f"🤖 Found agent: {agent.get('name')} (ID: {agent_id})")
    
    test_message = """I am ceo and my name is Lakshanand Sugumar. We are proteinramen INC and we sell high protein ramen noodles. this is healthy.
Draft a sales pitch email about our company and send to slakshanand1105@gmail.com"""
    
    # Test 1: Generic endpoint
    print(f"\n🔗 TEST 1: Generic /api/chat/mcpai endpoint")
    print("-" * 50)
    
    try:
        response1 = requests.post(f"{base_url}/api/chat/mcpai",
            json={"message": test_message},
            headers=headers,
            timeout=30
        )
        
        if response1.status_code == 200:
            result1 = response1.json()
            
            status1 = result1.get('status')
            action1 = result1.get('action_required')
            email_content1 = result1.get('email_content')
            recipient1 = result1.get('recipient')
            
            print(f"   status: {status1}")
            print(f"   action_required: {action1}")
            print(f"   email_content: {'YES' if email_content1 else 'NO'}")
            print(f"   recipient: {recipient1}")
            
            # Check conditions
            condition1_1 = status1 == 'preview_ready' and action1 == 'approve_email'
            condition1_2 = email_content1 and recipient1
            
            will_trigger1 = condition1_1 or condition1_2
            print(f"   Will trigger dialog: {'✅ YES' if will_trigger1 else '❌ NO'}")
            
        else:
            print(f"   ❌ Failed: {response1.status_code}")
            will_trigger1 = False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        will_trigger1 = False
    
    # Test 2: Agent-specific endpoint
    print(f"\n🤖 TEST 2: Agent-specific /api/agents/{agent_id}/chat endpoint")
    print("-" * 50)
    
    try:
        response2 = requests.post(f"{base_url}/api/agents/{agent_id}/chat",
            json={"message": test_message},
            headers=headers,
            timeout=30
        )
        
        if response2.status_code == 200:
            result2 = response2.json()
            
            # Agent endpoint returns different format
            status2 = result2.get('workflow_status')
            automation_type2 = result2.get('automation_type')
            response_text = result2.get('response', '')
            
            print(f"   workflow_status: {status2}")
            print(f"   automation_type: {automation_type2}")
            print(f"   response length: {len(response_text)}")
            print(f"   contains 'Email Ready': {'YES' if 'Email Ready' in response_text else 'NO'}")
            print(f"   contains 'Type yes': {'YES' if 'yes' in response_text.lower() else 'NO'}")
            
            # For agent endpoint, it returns response text instead of structured format
            has_email_preview = 'Email Ready' in response_text and 'yes' in response_text.lower()
            print(f"   Will trigger dialog: {'⚠️ DIFFERENT FORMAT' if has_email_preview else '❌ NO'}")
            
            will_trigger2 = False  # Agent endpoint uses different response format
            
        else:
            print(f"   ❌ Failed: {response2.status_code}")
            will_trigger2 = False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        will_trigger2 = False
    
    print(f"\n🏁 COMPARISON RESULTS:")
    print(f"Generic endpoint triggers dialog: {'✅ YES' if will_trigger1 else '❌ NO'}")
    print(f"Agent endpoint triggers dialog: {'❌ NO (different format)' if not will_trigger2 else '✅ YES'}")
    
    print(f"\n💡 FRONTEND INTEGRATION:")
    if will_trigger1:
        print(f"✅ The generic /api/chat/mcpai endpoint should trigger the email preview dialog")
        print(f"📱 Make sure your frontend is using this endpoint for email requests")
    else:
        print(f"❌ Neither endpoint is properly configured for email preview dialog")
        print(f"🔧 The frontend expects structured response from the generic endpoint")
    
    return will_trigger1

if __name__ == "__main__":
    print("🎯 ENDPOINT COMPARISON FOR EMAIL PREVIEW DIALOG")
    print("=" * 60)
    
    success = test_both_endpoints_preview_trigger()
    
    if success:
        print(f"\n✅ Email preview dialog should work with the generic endpoint!")
    else:
        print(f"\n❌ Email preview dialog needs backend/frontend alignment")
