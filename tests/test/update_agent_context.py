#!/usr/bin/env python3
"""
Update agent with Roomify and Pranay context in agent_expectations field
"""

import requests
import json

def update_agent_context():
    """Update the agent to include Roomify and Pranay context"""
    print("🔧 UPDATING AGENT WITH ROOMIFY CONTEXT")
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
    
    # Get current agent
    print(f"\n📋 Getting current agent...")
    try:
        agents_response = requests.get(f"{base_url}/api/agents", headers=headers)
        if agents_response.status_code == 200:
            agents = agents_response.json().get('agents', [])
            if agents:
                current_agent = agents[0]  # Get the first agent
                agent_id = current_agent.get('id')
                
                print(f"Current agent: {current_agent.get('name')} (ID: {agent_id})")
                
                # Create agent context with Roomify information
                roomify_context = """CEO: Pranay
Company: Roomify 
Product: Mobile/web application for room finding and roommate matching
Business: Technology startup in the housing/accommodation sector
Value Proposition: Simplifies the process of finding rooms and compatible roommates
Target Market: Students, young professionals, people relocating
Key Features: Room search, roommate matching, secure communication platform"""

                # Update agent with context
                update_data = {
                    "agent_expectations": roomify_context,
                    "description": f"{current_agent.get('description', '')} - Enhanced with Roomify app context",
                    "config": {
                        **current_agent.get('config', {}),
                        "company_context": "Roomify app for room finding and roommate matching, CEO: Pranay"
                    }
                }
                
                print(f"\n📤 Updating agent with Roomify context...")
                print(f"New agent_expectations: {roomify_context[:100]}...")
                
                # Update the agent
                update_response = requests.put(
                    f"{base_url}/api/agents/{agent_id}",
                    json=update_data,
                    headers=headers
                )
                
                if update_response.status_code == 200:
                    print("✅ Agent updated successfully!")
                    
                    # Verify the update
                    verify_response = requests.get(f"{base_url}/api/agents/{agent_id}", headers=headers)
                    if verify_response.status_code == 200:
                        updated_agent = verify_response.json()
                        expectations = updated_agent.get('agent_expectations', '')
                        
                        print(f"\n✅ VERIFICATION:")
                        print(f"Agent expectations updated: {'✅' if 'Roomify' in expectations else '❌'}")
                        print(f"Contains Pranay: {'✅' if 'Pranay' in expectations else '❌'}")
                        print(f"Contains app context: {'✅' if 'app' in expectations.lower() else '❌'}")
                        
                        return True
                    else:
                        print(f"❌ Failed to verify update: {verify_response.status_code}")
                        return False
                else:
                    print(f"❌ Failed to update agent: {update_response.status_code}")
                    print(f"Response: {update_response.text}")
                    return False
            else:
                print("❌ No agents found")
                return False
        else:
            print(f"❌ Failed to get agents: {agents_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_updated_email_generation():
    """Test email generation with updated agent context"""
    print(f"\n📧 TESTING EMAIL WITH UPDATED AGENT")
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
    
    # Test the same message that was failing
    test_message = """i am ceo pranay, draft a sales pitch email for our app roomify and send to slakshanand1105@gmail.com"""
    
    print(f"📤 Testing: {test_message}")
    
    try:
        response = requests.post(f"{base_url}/api/chat/mcpai",
            json={"message": test_message},
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            message = result.get('message', '')
            email_content = result.get('email_content', '')
            
            print(f"\n📧 EMAIL CONTENT ANALYSIS:")
            print("=" * 50)
            
            # Check for improvements
            has_roomify = 'roomify' in email_content.lower() if email_content else 'roomify' in message.lower()
            has_pranay = 'pranay' in email_content.lower() if email_content else 'pranay' in message.lower()
            has_app_context = 'app' in email_content.lower() if email_content else 'app' in message.lower()
            no_generic_template = 'high-quality solutions for our clients' not in (email_content or message)
            has_specific_content = len(email_content or message) > 200
            
            print(f"✅ Contains Roomify: {'YES' if has_roomify else 'NO'}")
            print(f"✅ Contains Pranay: {'YES' if has_pranay else 'NO'}")
            print(f"✅ Contains app context: {'YES' if has_app_context else 'NO'}")
            print(f"✅ Not generic template: {'YES' if no_generic_template else 'NO'}")
            print(f"✅ Substantial content: {'YES' if has_specific_content else 'NO'}")
            
            improvement_score = sum([has_roomify, has_pranay, has_app_context, no_generic_template, has_specific_content])
            
            print(f"\n🎯 IMPROVEMENT SCORE: {improvement_score}/5")
            
            if improvement_score >= 4:
                print("🎉 SUCCESS! Agent is now using Roomify context!")
                
                print(f"\n📝 EMAIL PREVIEW:")
                print("-" * 40)
                print((email_content or message)[:400])
                print("-" * 40)
                
                return True
            else:
                print("⚠️ Partial improvement - may need more context")
                return False
                
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 AGENT CONTEXT UPDATE SESSION")
    print("=" * 70)
    
    # Step 1: Update agent with Roomify context
    update_success = update_agent_context()
    
    if update_success:
        # Step 2: Test improved email generation
        test_success = test_updated_email_generation()
        
        print(f"\n🏁 FINAL RESULTS:")
        print("=" * 30)
        print(f"Agent update: {'✅ SUCCESS' if update_success else '❌ FAILED'}")
        print(f"Email improvement: {'✅ SUCCESS' if test_success else '❌ NEEDS MORE WORK'}")
        
        if test_success:
            print(f"\n🎉 PROBLEM SOLVED!")
            print(f"✅ Agent now uses Roomify context for email generation")
            print(f"📱 Try your email request again in the frontend!")
        else:
            print(f"\n⚠️ Agent updated but email generation needs more tuning")
    else:
        print(f"\n❌ Failed to update agent context")
