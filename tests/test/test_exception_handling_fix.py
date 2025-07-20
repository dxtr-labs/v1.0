"""
Test the fixed CustomMCPLLMIterationEngine WITHOUT authentication
Using the test endpoint to validate OpenAI conversational responses
"""
import requests
import json

def test_exception_handling_fixes():
    """Test the CustomMCPLLMIterationEngine exception handling fixes using test endpoint"""
    
    print("🎯 TESTING EXCEPTION HANDLING FIXES - NO AUTH REQUIRED")
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
    
    # Test 2: Create a test agent using the existing agent system
    print("\n2️⃣ Setting up test agent...")
    
    # For testing, let's use a predictable agent ID or create one
    # First, let's check what agents exist by using a dummy agent ID
    
    # Known agent format from previous tests - they're UUIDs
    # Let's try to find an existing agent or use a test pattern
    test_agent_id = "test-agent-001"  # Simple test ID
    
    print(f"🔍 Using test agent ID: {test_agent_id}")
    
    # Test 3: THE CRITICAL TEST - Chat using the test endpoint (no auth)
    print(f"\n3️⃣ 🔥 CRITICAL TEST: Testing CustomMCPLLMIterationEngine exception handling...")
    print(f"🎯 Endpoint: /api/test/agents/{test_agent_id}/chat")
    print(f"🎯 Purpose: Test fixed exception handling in CustomMCPLLMIterationEngine.process_user_request()")
    
    test_messages = [
        "hello",
        "how are you today?", 
        "what can you help me with?",
        "tell me about DXTR Labs"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n  Test {i}/4: '{message}'")
        
        try:
            # Test the NO-AUTH chat endpoint that uses CustomMCPLLMIterationEngine
            chat_response = requests.post(
                f"{BACKEND_URL}/api/test/agents/{test_agent_id}/chat",
                json={"message": message},
                timeout=30  # Give OpenAI time to respond
            )
            
            print(f"    📊 Status Code: {chat_response.status_code}")
            
            if chat_response.status_code == 200:
                result = chat_response.json()
                response_text = result.get('response', '')
                success = result.get('success', False)
                workflow_status = result.get('workflow_status', 'N/A')
                method_used = result.get('method', 'Unknown')
                
                print(f"    📤 Request: {message}")
                print(f"    📥 Response: {response_text}")
                print(f"    📊 Status: {workflow_status}")
                print(f"    🔧 Method: {method_used}")
                print(f"    ✅ Success: {success}")
                
                # Analyze the response type
                problematic_phrases = [
                    "Let me help you create an automation. What would you like to do?",
                    "I'm having trouble with my AI response system",
                    "Please provide more details about what you'd like to automate",
                    "I can help you set up workflows",
                    "What automation would you like to create?"
                ]
                
                conversational_indicators = [
                    "Hello", "Hi", "How can I", "I can help", "assist", "today"
                ]
                
                is_generic_problem = any(phrase.lower() in response_text.lower() for phrase in problematic_phrases)
                is_conversational = any(indicator.lower() in response_text.lower() for indicator in conversational_indicators)
                
                # Detailed analysis
                if is_generic_problem:
                    print(f"    ❌ STILL BROKEN: Getting problematic generic automation responses!")
                    print(f"    ❌ This means exception handling is STILL masking OpenAI responses!")
                elif is_conversational and len(response_text) > 10:
                    print(f"    ✅ SUCCESS: Conversational response - exception handling FIXED!")
                    print(f"    ✅ OpenAI responses are now reaching users properly!")
                elif "error" in response_text.lower() or len(response_text) < 5:
                    print(f"    ⚠️  ERROR RESPONSE: {response_text}")
                else:
                    print(f"    ❓ UNCLEAR: Response type unclear - need manual inspection")
                    
            else:
                print(f"    ❌ Chat failed: {chat_response.status_code}")
                try:
                    error_detail = chat_response.json()
                    print(f"    ❌ Error: {json.dumps(error_detail, indent=2)}")
                except:
                    print(f"    ❌ Error: {chat_response.text}")
                
        except Exception as e:
            print(f"    ❌ Chat request failed: {e}")
    
    print(f"\n📊 CRITICAL ANALYSIS:")
    print(f"🎯 WHAT WE'RE TESTING:")
    print(f"   - CustomMCPLLMIterationEngine.process_user_request() exception handling")
    print(f"   - Whether OpenAI responses reach users vs generic fallbacks")
    print(f"   - Fixed code should use OpenAI recovery instead of generic responses")
    
    print(f"\n✅ EXPECTED IF FIXED:")
    print(f"   - Conversational responses like 'Hello! How can I assist you today?'")
    print(f"   - Natural language that sounds like OpenAI")
    print(f"   - NO generic automation-focused responses")
    
    print(f"\n❌ SIGNS STILL BROKEN:")
    print(f"   - 'Let me help you create an automation. What would you like to do?'")
    print(f"   - Generic automation-focused responses")
    print(f"   - Exception handling masking OpenAI responses")

if __name__ == "__main__":
    test_exception_handling_fixes()
