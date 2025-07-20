#!/usr/bin/env python3
"""
Final conversation flow verification
"""

import requests
import json
import time

def test_fixed_conversation():
    """Test the fixed conversation flow"""
    
    print("🎉 TESTING FIXED CONVERSATION FLOW")
    print("=" * 50)
    
    agent_id = "a99f903c-1fa5-4dc5-b15a-ec716b9a161a"
    base_url = "http://localhost:8002"
    
    # Your exact conversation sequence
    messages = [
        "hello",
        "find top 10 investors in ai field and send email about dxtr labs to them", 
        "sure"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"\n{i}. User: {message}")
        
        try:
            response = requests.post(
                f"{base_url}/api/agents/{agent_id}/chat",
                json={"message": message},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   Agent: {result.get('response', '')[:150]}...")
                
                if i == 2:  # Automation request
                    if result.get('hasWorkflowJson'):
                        print("   ✅ Workflow offered as expected")
                    else:
                        print("   ❌ No workflow offered")
                        
                if i == 3:  # Continuation
                    if 'investor' in result.get('response', '').lower():
                        print("   ✅ MEMORY WORKING! Agent remembers investor request")
                    else:
                        print("   ❌ Memory failed - no context awareness")
                        
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            
        time.sleep(1)
    
    print(f"\n🎯 CONVERSATION FLOW FIX VERIFICATION COMPLETE!")
    print(f"The conversation should now flow naturally with context preservation.")

if __name__ == "__main__":
    test_fixed_conversation()
