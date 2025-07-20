"""
Test the fixed CustomMCPLLMIterationEngine exception handling with REAL agent
This tests the main chat workflow to ensure OpenAI responses reach users
"""
import requests
import json

def test_fixed_exception_handling():
    """Test the CustomMCPLLMIterationEngine exception handling fixes"""
    
    print("🎯 TESTING FIXED EXCEPTION HANDLING WITH REAL AGENT")
    print("=" * 65)
    
    BACKEND_URL = "http://localhost:8002"
    
    # Read the agent ID from file
    try:
        with open('test_agent_id.txt', 'r') as f:
            agent_id = f.read().strip()
        print(f"🤖 Using agent: {agent_id}")
    except:
        print("❌ Could not read agent ID from test_agent_id.txt")
        return
    
    # Test 1: Test using the NO-AUTH endpoint first
    print(f"\n1️⃣ Testing NO-AUTH endpoint with CustomMCPLLMIterationEngine...")
    
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
                f"{BACKEND_URL}/api/test/agents/{agent_id}/chat",
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
                error_info = result.get('error', 'None')
                
                print(f"    📤 Request: {message}")
                print(f"    📥 Response ({len(response_text)} chars): {response_text}")
                print(f"    📊 Status: {workflow_status}")
                print(f"    🔧 Method: {method_used}")
                print(f"    ✅ Success: {success}")
                print(f"    ⚠️  Error: {error_info}")
                
                # Analyze the response type - CHECK FOR THE FIXED BEHAVIOR
                problematic_phrases = [
                    "Let me help you create an automation. What would you like to do?",
                    "I'm having trouble with my AI response system",
                    "Please provide more details about what you'd like to automate",
                    "I can help you set up workflows",
                    "What automation would you like to create?"
                ]
                
                conversational_indicators = [
                    "Hello", "Hi", "How can I", "I can help", "assist", "today", 
                    "I'm", "great", "doing well", "can assist", "happy to help"
                ]
                
                is_generic_problem = any(phrase.lower() in response_text.lower() for phrase in problematic_phrases)
                is_conversational = any(indicator.lower() in response_text.lower() for indicator in conversational_indicators)
                
                # Detailed analysis
                print(f"    🔍 Analysis:")
                if is_generic_problem:
                    print(f"    ❌ STILL BROKEN: Getting problematic generic automation responses!")
                    print(f"    ❌ Exception handling is STILL masking OpenAI responses with fallbacks!")
                elif is_conversational and len(response_text) > 20:
                    print(f"    ✅ SUCCESS: Conversational response - exception handling FIXED!")
                    print(f"    ✅ OpenAI responses are now reaching users properly!")
                    print(f"    ✅ No more generic fallback masking!")
                elif "error" in response_text.lower() or len(response_text) < 5:
                    print(f"    ⚠️  ERROR RESPONSE: {response_text}")
                elif response_text == message:
                    print(f"    ❓ ECHO: Response echoes input - possible error")
                else:
                    print(f"    ❓ UNCLEAR: Response type unclear - manual inspection needed")
                    
            else:
                print(f"    ❌ Chat failed: {chat_response.status_code}")
                try:
                    error_detail = chat_response.json()
                    print(f"    ❌ Error: {json.dumps(error_detail, indent=2)}")
                except:
                    print(f"    ❌ Error: {chat_response.text}")
                
        except Exception as e:
            print(f"    ❌ Chat request failed: {e}")
    
    print(f"\n📊 FINAL ANALYSIS:")
    print(f"🎯 WHAT WE JUST TESTED:")
    print(f"   - CustomMCPLLMIterationEngine.process_user_request() with FIXED exception handling")
    print(f"   - Whether OpenAI responses reach users vs getting masked by generic fallbacks")
    print(f"   - The core issue: Exception handler returning generic automation messages")
    
    print(f"\n✅ SUCCESS INDICATORS (Fixed Code):")
    print(f"   - Natural conversational responses like 'Hello! How can I assist you today?'")
    print(f"   - OpenAI-style language that sounds human and helpful")
    print(f"   - NO automation-focused generic responses")
    print(f"   - Responses that directly answer the user's greeting/question")
    
    print(f"\n❌ FAILURE INDICATORS (Still Broken):")
    print(f"   - 'Let me help you create an automation. What would you like to do?'")
    print(f"   - Any automation-focused responses to simple greetings")
    print(f"   - Exception handling still masking OpenAI with generic fallbacks")
    
    print(f"\n🔧 KEY TECHNICAL POINTS:")
    print(f"   - CustomMCPLLMIterationEngine should now use _generate_ai_conversational_response() in exceptions")
    print(f"   - NO MORE generic fallback responses that override OpenAI output")
    print(f"   - Exception recovery should attempt OpenAI before giving up")

if __name__ == "__main__":
    test_fixed_exception_handling()
