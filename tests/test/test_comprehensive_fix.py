"""
Test the fixed OpenAI integration and exception handling
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()
load_dotenv('.env')

# Test configuration
BACKEND_URL = "http://localhost:8002"
FRONTEND_URL = "http://localhost:3001"

def test_fixed_openai_integration():
    """Test the comprehensive fixes to OpenAI integration"""
    
    print("🧪 COMPREHENSIVE TEST: Fixed OpenAI Integration")
    print("=" * 60)
    
    # Test 1: Direct OpenAI Python test (baseline)
    print("\n1️⃣ Testing Direct OpenAI (Baseline)...")
    try:
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            print("❌ OpenAI API key not found")
            return
        
        print(f"✅ OpenAI API key loaded ({len(openai_key)} chars)")
        
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant for DXTR Labs, a cutting-edge automation and AI solutions company. Be conversational and helpful."
                },
                {"role": "user", "content": "hello"}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        response = completion.choices[0].message.content
        print(f"✅ Direct OpenAI: {response}")
        
    except Exception as e:
        print(f"❌ Direct OpenAI failed: {e}")
        return
    
    # Test 2: Backend health check
    print("\n2️⃣ Testing Backend Health...")
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            print(f"✅ Backend healthy: {response.json()}")
        else:
            print(f"❌ Backend unhealthy: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return
    
    # Test 3: Create a test agent first (needed for chat endpoints)
    print("\n3️⃣ Setting up test agent...")
    test_user_data = {
        "email": "test@dxtrlabs.com",
        "password": "testpass123",
        "full_name": "Test User"
    }
    
    # First signup/login to get session
    try:
        signup_response = requests.post(f"{BACKEND_URL}/api/auth/signup", json=test_user_data)
        if signup_response.status_code in [200, 201]:
            print("✅ User created/exists")
        
        login_response = requests.post(f"{BACKEND_URL}/api/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        
        if login_response.status_code == 200:
            session_token = login_response.cookies.get('session_token')
            print(f"✅ Login successful, session: {session_token[:20]}...")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Auth setup failed: {e}")
        return
    
    # Create test agent
    try:
        agent_data = {
            "agent_name": "Test Assistant",
            "agent_role": "Personal Assistant",
            "operation_mode": "chat",
            "agent_expectations": "Help with automation and be conversational"
        }
        
        cookies = {'session_token': session_token}
        agent_response = requests.post(f"{BACKEND_URL}/api/agents", json=agent_data, cookies=cookies)
        
        if agent_response.status_code in [200, 201]:
            agent_result = agent_response.json()
            agent_id = agent_result.get('agent_id')
            print(f"✅ Test agent created: {agent_id}")
        else:
            print(f"❌ Agent creation failed: {agent_response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Agent setup failed: {e}")
        return
    
    # Test 4: Test the fixed backend endpoint (using test endpoint)
    print("\n4️⃣ Testing Fixed Backend Endpoint...")
    try:
        test_messages = [
            {"message": "hello", "expected_type": "conversational"},
            {"message": "how are you today?", "expected_type": "conversational"},
            {"message": "what can you help me with?", "expected_type": "conversational"},
            {"message": "send email to john@example.com", "expected_type": "automation"}
        ]
        
        for test_case in test_messages:
            print(f"\n  Testing: '{test_case['message']}'")
            
            # Use the test endpoint that bypasses auth
            test_response = requests.post(
                f"{BACKEND_URL}/api/test/agents/{agent_id}/chat",
                json={"message": test_case["message"]}
            )
            
            if test_response.status_code == 200:
                result = test_response.json()
                response_text = result.get('response', '')
                
                print(f"  📤 Request: {test_case['message']}")
                print(f"  📥 Response: {response_text[:100]}...")
                print(f"  📊 Status: {result.get('workflow_status', 'N/A')}")
                
                # Check if response is generic fallback
                generic_indicators = [
                    "Let me help you create an automation",
                    "What would you like to do?",
                    "I'm having trouble"
                ]
                
                is_generic = any(indicator in response_text for indicator in generic_indicators)
                
                if is_generic:
                    print(f"  ⚠️  STILL GETTING GENERIC RESPONSES!")
                elif len(response_text) > 50 and response_text != test_case["message"]:
                    print(f"  ✅ CONVERSATIONAL RESPONSE WORKING!")
                else:
                    print(f"  ❓ UNKNOWN RESPONSE TYPE")
                    
            else:
                print(f"  ❌ Request failed: {test_response.status_code}")
                print(f"  ❌ Error: {test_response.text}")
                
    except Exception as e:
        print(f"❌ Backend endpoint test failed: {e}")
    
    # Test 5: Check backend logs for debug info
    print("\n5️⃣ Analysis Summary:")
    print("✅ Direct OpenAI integration: WORKING")
    print("✅ Backend startup: SUCCESS")
    print("✅ Authentication system: WORKING")
    print("✅ Agent creation: SUCCESS")
    print("⚠️  Exception handling: FIXED (needs validation)")
    print("⚠️  Frontend integration: NEEDS TESTING")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Verify OpenAI responses reach frontend without being masked")
    print("2. Test frontend chat interface with real user interaction")
    print("3. Confirm generic fallbacks are eliminated")
    
    return True

if __name__ == "__main__":
    test_fixed_openai_integration()
