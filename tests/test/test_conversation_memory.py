#!/usr/bin/env python3
"""
Test the conversation flow fix
"""

import requests
import json
import time

def test_conversation_flow():
    """Test conversation flow with the enhanced memory system"""
    
    print("🧪 TESTING CONVERSATION FLOW WITH MEMORY")
    print("=" * 50)
    
    base_url = "http://localhost:8002"
    agent_id = "a99f903c-1fa5-4dc5-b15a-ec716b9a161a"
    
    # Simulate the exact conversation from your example
    conversation = [
        ("hello", "Should greet and remember this is the start"),
        ("find top 10 investors in ai field and send email about dxtr labs to them", "Should detect automation and offer workflow"),
        ("sure", "Should recognize continuation and proceed with workflow"),
        ("what was my previous request about?", "Should remember the AI investor request")
    ]
    
    print(f"Testing agent: {agent_id}")
    print("Simulating your exact conversation...")
    print()
    
    for i, (message, expectation) in enumerate(conversation, 1):
        print(f"Step {i}: '{message}'")
        print(f"Expected: {expectation}")
        
        try:
            response = requests.post(
                f"{base_url}/api/agents/{agent_id}/chat",
                json={"message": message},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ Status: {result.get('status', 'Unknown')}")
                print(f"📝 Response: {result.get('response', '')[:200]}...")
                
                if result.get('hasWorkflowJson'):
                    print(f"🔧 Workflow offered: Yes")
                else:
                    print(f"🔧 Workflow offered: No")
                
                # Check for context awareness
                response_text = result.get('response', '').lower()
                
                if i == 1 and 'hello' in message:
                    if 'hello' in response_text or 'hi' in response_text:
                        print("✅ Proper greeting response")
                    else:
                        print("❌ Unexpected greeting response")
                        
                elif i == 2 and 'investor' in message:
                    if 'investor' in response_text or 'workflow' in response_text:
                        print("✅ Automation detected correctly")
                    else:
                        print("❌ Automation not detected")
                        
                elif i == 3 and 'sure' in message:
                    if 'proceed' in response_text or 'workflow' in response_text or 'investor' in response_text:
                        print("✅ Context continuation working")
                    else:
                        print("❌ Context continuation failed")
                        
                elif i == 4 and 'previous request' in message:
                    if 'investor' in response_text or 'ai' in response_text or 'dxtr' in response_text:
                        print("✅ MEMORY WORKING - Remembers previous conversation!")
                    else:
                        print("❌ MEMORY FAILED - No recollection of previous requests")
                
            else:
                print(f"❌ Request failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)
        time.sleep(2)  # Wait between messages to simulate real conversation
    
    print("🎯 CONVERSATION FLOW TEST COMPLETE!")
    print("\nIf the memory is working, the agent should:")
    print("1. Remember your name across messages")
    print("2. Recognize 'sure' as continuation of the automation request")
    print("3. Remember the AI investor request when asked about previous requests")

if __name__ == "__main__":
    test_conversation_flow()
