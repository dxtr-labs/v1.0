import requests
import json
import os
import asyncio
import sys
import traceback

async def test_openai_integration():
    """Test OpenAI integration with detailed debugging"""
    
    url = "http://localhost:8002/api/agents/1b58f5f0-931e-46e5-b7d9-f76bd189b96d/chat"
    
    test_messages = [
        "Hello! Tell me about DXTR Labs and what you can do for me.",
        "I need help with email automation for my business.",
        "What makes DXTR Labs special compared to other automation companies?"
    ]
    
    print("🧪 Testing OpenAI Integration with DXTR Labs Context")
    print("=" * 60)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n🔍 Test {i}: {message}")
        print("-" * 40)
        
        payload = {
            "message": message,
            "agentId": "1b58f5f0-931e-46e5-b7d9-f76bd189b96d"
        }
        
        try:
            # Add authentication headers like the frontend does
            headers = {
                'Content-Type': 'application/json',
                'Cookie': 'session_token=test_session'
            }
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract the response message
                agent_response = data.get('response', 'No response found')
                
                print(f"✅ Response: {agent_response}")
                
                # Check for DXTR Labs branding
                dxtr_indicators = ['DXTR Labs', 'DXTR', 'digital employee', 'automation']
                has_branding = any(indicator.lower() in agent_response.lower() for indicator in dxtr_indicators)
                
                print(f"🏷️  DXTR Branding: {'✅ Found' if has_branding else '❌ Missing'}")
                
                # Check response length (OpenAI responses are typically longer)
                response_length = len(agent_response)
                print(f"📏 Response Length: {response_length} chars")
                
                # Check for conversational quality
                conversational_indicators = ['I', 'you', 'we', 'help', 'can', 'will']
                is_conversational = sum(1 for word in conversational_indicators if word.lower() in agent_response.lower()) >= 3
                print(f"💬 Conversational: {'✅ Yes' if is_conversational else '❌ Generic'}")
                
                # Overall assessment
                is_openai_response = has_branding and response_length > 50 and is_conversational
                print(f"🤖 OpenAI Powered: {'✅ Likely' if is_openai_response else '❌ Fallback'}")
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            traceback.print_exc()
        
        if i < len(test_messages):
            print("\n⏳ Waiting 2 seconds before next test...")
            await asyncio.sleep(2)
    
    print("\n" + "=" * 60)
    print("🏁 OpenAI Integration Test Complete")

if __name__ == "__main__":
    asyncio.run(test_openai_integration())
