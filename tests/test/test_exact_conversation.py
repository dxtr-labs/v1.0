#!/usr/bin/env python3
"""
Test the exact conversation flow from your example
"""

import requests
import json
import time

def test_exact_conversation():
    """Test the exact conversation sequence"""
    
    print("🧪 TESTING EXACT CONVERSATION FLOW")
    print("=" * 50)
    
    agent_id = "a99f903c-1fa5-4dc5-b15a-ec716b9a161a"
    base_url = "http://localhost:8002"
    
    # Your exact conversation sequence
    messages = [
        "hello",
        "find top 10 ai investors and send email to slakshanand1105@gmail.com",
        "yes",
        "yes"
    ]
    
    expected_behaviors = [
        "Should greet the user",
        "Should detect AI investor automation and offer workflow",
        "Should proceed with AI investor workflow",
        "Should continue with execution or ask for more details"
    ]
    
    for i, (message, expected) in enumerate(zip(messages, expected_behaviors), 1):
        print(f"\n{i}. User: '{message}'")
        print(f"   Expected: {expected}")
        
        try:
            response = requests.post(
                f"{base_url}/api/agents/{agent_id}/chat",
                json={"message": message},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                status = result.get('status', 'Unknown')
                has_workflow = result.get('hasWorkflowJson', False)
                
                print(f"   Agent: {response_text[:150]}...")
                print(f"   Status: {status}")
                print(f"   Workflow: {has_workflow}")
                
                # Check specific behaviors
                if i == 1:  # Hello
                    if 'hello' in response_text.lower() or 'hi' in response_text.lower():
                        print("   ✅ Proper greeting")
                    else:
                        print("   ❌ No greeting detected")
                        
                elif i == 2:  # AI investor request
                    if 'investor' in response_text.lower() and has_workflow:
                        print("   ✅ AI investor automation detected")
                    else:
                        print("   ❌ AI investor automation not properly detected")
                        
                elif i == 3:  # First "yes"
                    if 'proceeding' in response_text.lower() or 'excellent' in response_text.lower():
                        print("   ✅ CONTINUATION WORKING! Agent proceeds with workflow")
                    else:
                        print("   ❌ Continuation failed - agent doesn't recognize 'yes'")
                        
                elif i == 4:  # Second "yes"
                    if 'investor' in response_text.lower() or 'workflow' in response_text.lower():
                        print("   ✅ Context maintained for second 'yes'")
                    else:
                        print("   ❌ Lost context on second 'yes'")
                
            else:
                print(f"   ❌ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(1)  # Brief pause between messages
    
    print(f"\n🎯 CONVERSATION FLOW TEST COMPLETE!")
    print("The agent should now properly handle 'yes' responses as workflow continuations.")

if __name__ == "__main__":
    test_exact_conversation()
