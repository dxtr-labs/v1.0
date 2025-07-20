"""
Test the fixed CustomMCPLLMIterationEngine exception handling
This tests the main chat workflow to ensure OpenAI responses reach users
"""
import requests
import json

def test_main_backend_fixes():
    """Test the main backend with fixed exception handling"""
    
    print("🎯 TESTING MAIN BACKEND EXCEPTION HANDLING FIXES")
    print("=" * 60)
    
    BACKEND_URL = "http://localhost:8002"
    
    # Test 1: Health check
    print("\n1️⃣ Backend Health Check...")
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            print(f"✅ Backend healthy: {response.json()}")
        else:
            print(f"❌ Backend unhealthy: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return
    
    # Test 2: Auth and agent setup
    print("\n2️⃣ Setting up authentication and agent...")
    
    # User data for testing
    test_user = {
        "email": "test@dxtrlabs.com",
        "password": "testpass123",
        "full_name": "Test User"
    }
    
    try:
        # Signup (may fail if user exists, which is OK)
        signup_response = requests.post(f"{BACKEND_URL}/api/auth/signup", json=test_user)
        print(f"📝 Signup response: {signup_response.status_code}")
        
        # Login to get session
        login_response = requests.post(f"{BACKEND_URL}/api/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
            return
        
        session_token = login_response.cookies.get('session_token')
        if not session_token:
            print("❌ No session token received")
            return
            
        print(f"✅ Login successful, session: {session_token[:20]}...")
        cookies = {'session_token': session_token}
        
    except Exception as e:
        print(f"❌ Auth failed: {e}")
        return
    
    # Test 3: Get or create default agent
    print("\n3️⃣ Getting/creating default agent...")
    try:
        # Try to get existing agents first
        agents_response = requests.get(f"{BACKEND_URL}/api/agents", cookies=cookies)
        
        if agents_response.status_code == 200:
            agents = agents_response.json().get('agents', [])
            if agents:
                agent_id = agents[0]['agent_id']
                print(f"✅ Using existing agent: {agent_id}")
            else:
                # Create new agent
                agent_data = {
                    "agent_name": "DXTR Assistant",
                    "agent_role": "Personal Assistant", 
                    "operation_mode": "chat",
                    "agent_expectations": "Be helpful and conversational while assisting with automation"
                }
                
                create_response = requests.post(f"{BACKEND_URL}/api/agents", json=agent_data, cookies=cookies)
                if create_response.status_code in [200, 201]:
                    agent_id = create_response.json()['agent_id']
                    print(f"✅ Created new agent: {agent_id}")
                else:
                    print(f"❌ Agent creation failed: {create_response.status_code}")
                    return
        else:
            print(f"❌ Failed to get agents: {agents_response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Agent setup failed: {e}")
        return
    
    # Test 4: THE CRITICAL TEST - Chat with agent using fixed CustomMCPLLMIterationEngine
    print(f"\n4️⃣ 🔥 CRITICAL TEST: Chat with agent {agent_id} using FIXED exception handling...")
    
    test_messages = [
        "hello",
        "how are you today?", 
        "what can you help me with?",
        "tell me about DXTR Labs"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n  Test {i}: '{message}'")
        
        try:
            # Test the main chat endpoint that uses CustomMCPLLMIterationEngine
            chat_response = requests.post(
                f"{BACKEND_URL}/api/agents/{agent_id}/chat",
                json={"message": message},
                cookies=cookies
            )
            
            if chat_response.status_code == 200:
                result = chat_response.json()
                response_text = result.get('response', '')
                status = result.get('workflow_status', 'N/A')
                
                print(f"    📤 Request: {message}")
                print(f"    📥 Response: {response_text[:100]}...")
                print(f"    📊 Status: {status}")
                print(f"    ✅ Success: {result.get('success', False)}")
                
                # Check for the specific generic fallback that was the problem
                problematic_phrases = [
                    "Let me help you create an automation. What would you like to do?",
                    "I'm having trouble with my AI response system",
                    "Please provide more details about what you'd like to automate"
                ]
                
                is_generic_problem = any(phrase in response_text for phrase in problematic_phrases)
                
                if is_generic_problem:
                    print(f"    ❌ STILL GETTING PROBLEMATIC GENERIC RESPONSES!")
                elif len(response_text) > 30 and response_text != message:
                    print(f"    ✅ CONVERSATIONAL RESPONSE - EXCEPTION HANDLING FIXED!")
                else:
                    print(f"    ❓ UNCLEAR RESPONSE TYPE")
                    
            else:
                print(f"    ❌ Chat failed: {chat_response.status_code}")
                print(f"    ❌ Error: {chat_response.text}")
                
        except Exception as e:
            print(f"    ❌ Chat request failed: {e}")
    
    print(f"\n📊 SUMMARY:")
    print(f"✅ Backend: RUNNING")  
    print(f"✅ Authentication: WORKING")
    print(f"✅ Agent System: WORKING")
    print(f"⚠️  Exception Handling: TESTED (check responses above)")
    print(f"⚠️  OpenAI Integration: TESTED (check for conversational vs generic)")
    
    print(f"\n🎯 EXPECTED OUTCOME:")
    print(f"- If fixes worked: Conversational OpenAI responses like 'Hello! How can I assist you today?'")
    print(f"- If still broken: Generic responses like 'Let me help you create an automation'")

if __name__ == "__main__":
    test_main_backend_fixes()
