#!/usr/bin/env python3
"""
Debug email content generation issue with agent-specific endpoint
"""

import requests
import json
import time

def test_agent_specific_email_generation():
    """Test email generation using agent-specific endpoint"""
    print("🔍 DEBUGGING EMAIL CONTENT GENERATION - AGENT SPECIFIC")
    print("=" * 60)
    
    base_url = "http://localhost:8002"
    
    # First, let's try to use the test endpoint that doesn't require auth
    # Use a proper UUID format for the test agent
    test_agent_id = "12345678-1234-1234-1234-123456789abc"
    
    # Test the exact message from the screenshot
    test_message = """I am ceo and my name is Lakshanand Sugumar.We are proteinramen INC and we sell high protein ramen noodles. this is healthy.
Draft a sales pitch email about our company and send to slakshanand1105@gmail.com"""
    
    print(f"\n📧 Testing agent-specific email generation...")
    print(f"Agent ID: {test_agent_id}")
    print(f"Request: {test_message}")
    
    try:
        # Try the test endpoint first (no auth required)
        response = requests.post(f"{base_url}/api/test/agents/{test_agent_id}/chat",
            json={"message": test_message},
            timeout=30
        )
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"Response Analysis:")
            print(f"   Success: {result.get('success', 'unknown')}")
            print(f"   Workflow Status: {result.get('workflow_status', 'unknown')}")
            print(f"   Automation Type: {result.get('automation_type', 'unknown')}")
            print(f"   Processing Time: {result.get('processing_time', 'unknown')}")
            print(f"   Response Length: {len(result.get('response', ''))}")
            
            print(f"\n📝 Full Response Message:")
            print("-" * 40)
            print(result.get('response', 'No response'))
            print("-" * 40)
            
            # Check if this looks like a proper sales pitch
            response_content = result.get('response', '').lower()
            
            # Look for sales pitch elements
            sales_indicators = [
                'protein', 'ramen', 'noodles', 'healthy', 
                'proteinramen', 'inc', 'lakshanand', 'sugumar',
                'sales', 'pitch', 'company', 'business'
            ]
            
            found_indicators = []
            for indicator in sales_indicators:
                if indicator in response_content:
                    found_indicators.append(indicator)
            
            print(f"\n🔍 Content Analysis:")
            print(f"   Sales indicators found: {found_indicators}")
            print(f"   Proper content generation: {'✅' if len(found_indicators) >= 4 else '❌'}")
            
            # Check if it's just a template response
            template_phrases = [
                'this is regarding',
                'context: no context available',
                'best regards, sam - personal assistant',
                "i'm sam - personal assistant"
            ]
            
            is_template = any(phrase in response_content for phrase in template_phrases)
            print(f"   Template response detected: {'❌ YES' if is_template else '✅ NO'}")
            
            # Check for AI-generated content
            ai_indicators = [
                'subject:', 'dear', 'sincerely', 'best regards', 
                'excited to', 'partnership', 'opportunity', 'introduce'
            ]
            
            found_ai_indicators = [indicator for indicator in ai_indicators if indicator in response_content]
            print(f"   AI content indicators: {found_ai_indicators}")
            print(f"   Professional email structure: {'✅' if len(found_ai_indicators) >= 2 else '❌'}")
            
            if is_template:
                print(f"\n⚠️ ISSUE: Still getting template response")
                return False
            elif len(found_indicators) >= 4 and len(found_ai_indicators) >= 2:
                print(f"\n✅ Agent-specific email content generation working properly!")
                return True
            else:
                print(f"\n⚠️ Email content may need improvement")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_with_authenticated_agent():
    """Test with authenticated user and specific agent"""
    print(f"\n🔧 TESTING WITH AUTHENTICATED AGENT")
    print("=" * 60)
    
    base_url = "http://localhost:8002"
    
    # Login first
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
    agents_response = requests.get(f"{base_url}/api/agents", headers=headers)
    if agents_response.status_code == 200:
        agents = agents_response.json().get('agents', [])
        print(f"📋 Available agents: {len(agents)}")
        
        if agents:
            # Use the first available agent
            test_agent = agents[0]
            # Handle different possible key names
            agent_id = test_agent.get('agent_id') or test_agent.get('id') or test_agent.get('uuid')
            agent_name = test_agent.get('agent_name') or test_agent.get('name') or 'Unknown'
            print(f"🤖 Using agent: {agent_name} (ID: {agent_id})")
            print(f"🔍 Available keys in agent: {list(test_agent.keys())}")
            
            if not agent_id:
                print("❌ Could not find agent ID in agent data")
                return False
            
            # Test message
            test_message = """I am ceo and my name is Lakshanand Sugumar.We are proteinramen INC and we sell high protein ramen noodles. this is healthy.
Draft a sales pitch email about our company and send to slakshanand1105@gmail.com"""
            
            # Call the agent-specific endpoint with auth
            response = requests.post(f"{base_url}/api/agents/{agent_id}/chat",
                json={"message": test_message},
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_content = result.get('response', '')
                
                print(f"\n📝 Authenticated Agent Response:")
                print("-" * 40)
                print(response_content[:500])
                print("..." if len(response_content) > 500 else "")
                print("-" * 40)
                
                # Analysis
                sales_indicators = ['protein', 'ramen', 'noodles', 'healthy', 'proteinramen', 'inc', 'lakshanand', 'sugumar']
                found_indicators = [ind for ind in sales_indicators if ind in response_content.lower()]
                
                is_template = any(phrase in response_content.lower() for phrase in [
                    'this is regarding', "i'm sam - personal assistant"
                ])
                
                print(f"\n✅ Authenticated Agent Analysis:")
                print(f"   Sales indicators: {found_indicators}")
                print(f"   Template response: {'❌ YES' if is_template else '✅ NO'}")
                print(f"   Content quality: {'✅ GOOD' if len(found_indicators) >= 4 and not is_template else '❌ NEEDS FIX'}")
                
                return len(found_indicators) >= 4 and not is_template
            else:
                print(f"❌ Agent request failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        else:
            print("❌ No agents available")
            return False
    else:
        print(f"❌ Failed to get agents: {agents_response.status_code}")
        return False

def test_generic_vs_agent_comparison():
    """Compare generic endpoint vs agent-specific endpoint"""
    print(f"\n🆚 COMPARING GENERIC VS AGENT-SPECIFIC ENDPOINTS")
    print("=" * 60)
    
    base_url = "http://localhost:8002"
    
    # Login
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "email": "aitest@example.com",
        "password": "testpass123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed for comparison test")
        return
    
    session_token = login_response.json().get("session_token")
    headers = {"Cookie": f"session_token={session_token}"}
    
    test_message = "Draft a sales pitch email about our protein ramen company and send to test@example.com"
    
    # Test 1: Generic endpoint
    print("🔗 Testing generic /api/chat/mcpai endpoint...")
    try:
        generic_response = requests.post(f"{base_url}/api/chat/mcpai",
            json={"message": test_message},
            headers=headers,
            timeout=20
        )
        
        if generic_response.status_code == 200:
            generic_result = generic_response.json()
            generic_message = generic_result.get('message', '')
            print(f"   Generic response length: {len(generic_message)}")
            print(f"   Generic response preview: {generic_message[:100]}...")
            
            is_generic_template = "i'm sam - personal assistant" in generic_message.lower()
            print(f"   Generic is template: {'❌ YES' if is_generic_template else '✅ NO'}")
        else:
            print(f"   Generic failed: {generic_response.status_code}")
            
    except Exception as e:
        print(f"   Generic error: {e}")
    
    # Test 2: Agent-specific endpoint (test endpoint, no auth needed)
    print("\n🤖 Testing agent-specific endpoint...")
    try:
        agent_response = requests.post(f"{base_url}/api/test/agents/12345678-1234-1234-1234-123456789abc/chat",
            json={"message": test_message},
            timeout=20
        )
        
        if agent_response.status_code == 200:
            agent_result = agent_response.json()
            agent_message = agent_result.get('response', '')
            print(f"   Agent response length: {len(agent_message)}")
            print(f"   Agent response preview: {agent_message[:100]}...")
            
            is_agent_template = "i'm sam - personal assistant" in agent_message.lower()
            automation_type = agent_result.get('automation_type', 'none')
            print(f"   Agent is template: {'❌ YES' if is_agent_template else '✅ NO'}")
            print(f"   Agent automation type: {automation_type}")
        else:
            print(f"   Agent failed: {agent_response.status_code}")
            
    except Exception as e:
        print(f"   Agent error: {e}")

if __name__ == "__main__":
    print("🎯 EMAIL CONTENT GENERATION - AGENT ENDPOINT DEBUG")
    print("=" * 70)
    
    # Wait for server to be ready
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    # Test 1: Agent-specific endpoint (no auth)
    test1_result = test_agent_specific_email_generation()
    
    # Test 2: Authenticated agent endpoint
    test2_result = test_with_authenticated_agent()
    
    # Test 3: Comparison
    test_generic_vs_agent_comparison()
    
    print(f"\n🏁 FINAL RESULTS:")
    print(f"Agent-specific (test): {'✅ WORKING' if test1_result else '❌ NEEDS FIX'}")
    print(f"Authenticated agent: {'✅ WORKING' if test2_result else '❌ NEEDS FIX'}")
    
    if test1_result or test2_result:
        print(f"\n✅ Email content generation is working with agent-specific endpoints!")
        print(f"💡 Solution: Use agent-specific endpoints instead of generic /api/chat/mcpai")
    else:
        print(f"\n❌ Email content generation still needs fixing")
        print(f"🔧 Next steps: Debug the CustomMCPLLMIterationEngine directly")
