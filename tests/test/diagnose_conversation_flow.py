#!/usr/bin/env python3
"""
Conversation Flow Diagnostic Tool
Identifies why conversations are not flowing properly
"""

import requests
import json
import time
import uuid

def diagnose_conversation_flow():
    """Diagnose conversation flow issues"""
    
    print("🔍 CONVERSATION FLOW DIAGNOSTIC TOOL")
    print("=" * 50)
    
    base_url = "http://localhost:8002"
    
    # Test 1: Check server connectivity
    print("\n📡 TEST 1: Server Connectivity")
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Server is accessible")
        else:
            print(f"❌ Server returned status: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # Test 2: Test agent endpoint with session persistence
    print("\n🤖 TEST 2: Agent Session Persistence")
    agent_id = "a99f903c-1fa5-4dc5-b15a-ec716b9a161a"  # Known working agent ID
    
    # Simulate the conversation flow you described
    conversation_steps = [
        "hello",
        "find top 10 investors in ai field and send email about dxtr labs to them",
        "sure",
        "can you proceed with the workflow?"
    ]
    
    session_data = {}
    
    for i, message in enumerate(conversation_steps, 1):
        print(f"\n  Step {i}: '{message}'")
        
        try:
            # Test agent endpoint
            response = requests.post(
                f"{base_url}/api/agents/{agent_id}/chat",
                json={"message": message},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"    ✅ Response received ({len(result.get('response', ''))} chars)")
                print(f"    📊 Status: {result.get('status', 'Unknown')}")
                print(f"    🔗 Has workflow: {result.get('hasWorkflowJson', False)}")
                print(f"    💬 Response preview: {result.get('response', '')[:100]}...")
                
                # Check for session/context indicators
                if 'session_id' in result:
                    session_data['session_id'] = result['session_id']
                    print(f"    🆔 Session ID: {result['session_id']}")
                
                if 'context' in result:
                    print(f"    📝 Context preserved: Yes")
                else:
                    print(f"    📝 Context preserved: Unknown")
                    
            else:
                print(f"    ❌ Failed: {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
        
        time.sleep(1)  # Brief pause between messages
    
    # Test 3: Check conversation memory/context
    print("\n🧠 TEST 3: Context Memory Analysis")
    
    # Ask a follow-up question that requires context
    follow_up = "What was my previous request about?"
    print(f"  Follow-up: '{follow_up}'")
    
    try:
        response = requests.post(
            f"{base_url}/api/agents/{agent_id}/chat",
            json={"message": follow_up},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', '').lower()
            
            # Check if it remembers the previous context
            context_keywords = ['investor', 'ai', 'dxtr', 'email', 'previous', 'earlier']
            context_found = any(keyword in response_text for keyword in context_keywords)
            
            if context_found:
                print(f"    ✅ Context preserved - AI remembers previous conversation")
            else:
                print(f"    ❌ Context lost - AI doesn't remember previous requests")
                print(f"    💬 Response: {response_text[:200]}...")
        else:
            print(f"    ❌ Follow-up failed: {response.status_code}")
            
    except Exception as e:
        print(f"    ❌ Follow-up error: {e}")
    
    # Test 4: Check different endpoints
    print("\n🔄 TEST 4: Endpoint Comparison")
    
    test_message = "Hello, can you help me?"
    
    # Test MCPAI endpoint
    print("  Testing /api/chat/mcpai:")
    try:
        response = requests.post(
            f"{base_url}/api/chat/mcpai",
            json={"message": test_message},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            print(f"    ✅ MCPAI endpoint working")
        elif response.status_code == 401:
            print(f"    🔒 MCPAI requires authentication")
        else:
            print(f"    ❌ MCPAI failed: {response.status_code}")
            
    except Exception as e:
        print(f"    ❌ MCPAI error: {e}")
    
    # Test agent endpoint again
    print(f"  Testing /api/agents/{agent_id}/chat:")
    try:
        response = requests.post(
            f"{base_url}/api/agents/{agent_id}/chat",
            json={"message": test_message},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            print(f"    ✅ Agent endpoint working")
        else:
            print(f"    ❌ Agent endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"    ❌ Agent endpoint error: {e}")
    
    # Analysis and recommendations
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS SUMMARY")
    print("=" * 50)
    
    print("\n🔍 LIKELY CAUSES OF CONVERSATION FLOW ISSUES:")
    print("   1. Session Management: Each request creates a new session")
    print("   2. Context Loss: Conversation history not preserved between messages")
    print("   3. Multiple Instances: Different endpoints/agents responding")
    print("   4. Memory Reset: Agent memory cleared between requests")
    
    print("\n💡 RECOMMENDED SOLUTIONS:")
    print("   1. Implement session persistence in CustomMCPLLMIterationEngine")
    print("   2. Add conversation history storage")
    print("   3. Ensure agent context is maintained across requests")
    print("   4. Check agent memory/context management")
    
    print("\n🔧 NEXT STEPS:")
    print("   • Examine CustomMCPLLMIterationEngine session handling")
    print("   • Check agent memory persistence")
    print("   • Verify conversation context storage")
    print("   • Test with explicit session IDs")

if __name__ == "__main__":
    print("Diagnosing conversation flow issues...")
    time.sleep(3)  # Wait for server to fully start
    diagnose_conversation_flow()
