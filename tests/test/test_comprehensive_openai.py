import requests
import json
import time

def test_openai_responses():
    """Comprehensive test to check if OpenAI responses are working vs generic responses"""
    
    base_url = "http://localhost:8002/api/test/agents/1b58f5f0-931e-46e5-b7d9-f76bd189b96d/chat"
    
    # Test messages that should trigger different response types
    test_cases = [
        {
            "message": "hello",
            "expected_type": "conversational",
            "description": "Simple greeting - should get OpenAI conversational response"
        },
        {
            "message": "How are you doing today?",
            "expected_type": "conversational", 
            "description": "Personal question - should get OpenAI conversational response"
        },
        {
            "message": "What can you help me with?",
            "expected_type": "conversational",
            "description": "Capabilities question - should get OpenAI conversational response"
        },
        {
            "message": "Tell me about DXTR Labs",
            "expected_type": "conversational",
            "description": "Company info request - should get OpenAI conversational response"
        },
        {
            "message": "I need help with email automation",
            "expected_type": "automation",
            "description": "Automation request - might trigger automation path"
        },
        {
            "message": "Send an email to john@example.com about our new product",
            "expected_type": "automation", 
            "description": "Clear automation request - should trigger automation"
        },
        {
            "message": "Thank you for your help!",
            "expected_type": "conversational",
            "description": "Gratitude - should get OpenAI conversational response"
        }
    ]
    
    print("🧪 COMPREHENSIVE OPENAI RESPONSE TEST")
    print("=" * 60)
    
    headers = {'Content-Type': 'application/json'}
    
    for i, test_case in enumerate(test_cases, 1):
        message = test_case["message"]
        expected_type = test_case["expected_type"]
        description = test_case["description"]
        
        print(f"\n🔍 Test {i}: {message}")
        print(f"📝 Expected: {expected_type}")
        print(f"📋 Description: {description}")
        print("-" * 50)
        
        payload = {
            "message": message,
            "agentId": "1b58f5f0-931e-46e5-b7d9-f76bd189b96d",
            "agentConfig": {
                "name": "testbot", 
                "role": "Personal Assistant",
                "mode": "chat"
            }
        }
        
        try:
            response = requests.post(base_url, json=payload, headers=headers, timeout=30)
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                response_text = data.get('response', '')
                workflow_status = data.get('workflow_status', 'unknown')
                debug_info = data.get('debug_info', {})
                
                print(f"✅ Response Status: {workflow_status}")
                print(f"📏 Response Length: {len(response_text)} chars")
                print(f"🔍 Response Preview: {response_text[:150]}{'...' if len(response_text) > 150 else ''}")
                
                # Analyze response characteristics
                analysis = analyze_response(response_text, workflow_status, expected_type)
                print(f"🤖 Analysis: {analysis['type']} - {analysis['reasoning']}")
                
                if 'debug_info' in data:
                    print(f"🔧 Debug Keys: {debug_info.get('response_keys', [])}")
                
                # Check if it looks like OpenAI or generic
                is_likely_openai = (
                    len(response_text) > 50 and
                    workflow_status == "conversational" and
                    any(word in response_text.lower() for word in ['i', 'you', 'help', 'can', 'dxtr']) and
                    not response_text.startswith("Let me help you create an automation")
                )
                
                print(f"🎯 OpenAI Powered: {'✅ LIKELY' if is_likely_openai else '❌ GENERIC/FALLBACK'}")
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        # Small delay between requests
        if i < len(test_cases):
            time.sleep(1)
    
    print("\n" + "=" * 60)
    print("🏁 COMPREHENSIVE TEST COMPLETE")
    print("\nIf you see mostly 'GENERIC/FALLBACK' responses:")
    print("  - Check backend logs for OpenAI errors")
    print("  - Verify OPENAI_API_KEY is set correctly")
    print("  - Check if OpenAI API calls are failing")
    print("\nIf you see 'LIKELY' OpenAI responses:")
    print("  - ✅ OpenAI integration is working!")
    print("  - The conversational system is functioning properly")

def analyze_response(response_text, status, expected_type):
    """Analyze response characteristics to determine if it's OpenAI or generic"""
    
    response_lower = response_text.lower()
    
    # Generic response indicators
    generic_indicators = [
        "let me help you create an automation",
        "what would you like to automate",
        "company name: dxtr labs",
        "what we sell: ai-powered"
    ]
    
    # OpenAI conversational indicators
    conversational_indicators = [
        "i'm", "i am", "how can i", "i'd be happy", 
        "great question", "absolutely", "of course",
        "i can help", "i specialize", "i'm here to"
    ]
    
    if any(indicator in response_lower for indicator in generic_indicators):
        return {
            "type": "GENERIC",
            "reasoning": "Contains generic template phrases"
        }
    
    if status == "conversational" and any(indicator in response_lower for indicator in conversational_indicators):
        return {
            "type": "OPENAI_CONVERSATIONAL", 
            "reasoning": "Natural conversational language with personal pronouns"
        }
    
    if status == "conversational" and len(response_text) > 100:
        return {
            "type": "LIKELY_OPENAI",
            "reasoning": "Long conversational response with good status"
        }
    
    if status in ["automation", "completed"]:
        return {
            "type": "AUTOMATION_PATH",
            "reasoning": f"Processed as {status} - may be correct automation routing"
        }
    
    return {
        "type": "UNKNOWN",
        "reasoning": f"Status: {status}, unclear response type"
    }

if __name__ == "__main__":
    test_openai_responses()
