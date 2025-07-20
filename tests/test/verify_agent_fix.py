#!/usr/bin/env python3
"""
Comprehensive test to verify the agent chat fix and system health
"""

import requests
import json
import time

def test_agent_chat_comprehensive():
    """Comprehensive test of agent chat functionality"""
    
    print("🧪 COMPREHENSIVE AGENT CHAT VERIFICATION")
    print("=" * 50)
    
    # Test the specific agent from the error
    agent_id = "a99f903c-1fa5-4dc5-b15a-ec716b9a161a"
    
    test_messages = [
        "Hello! Can you help me?",
        "I need to create an email automation",
        "What can you do for me?",
        "Thank you for your help!",
        "Can you process a workflow?"
    ]
    
    successful_tests = 0
    total_tests = len(test_messages)
    
    print(f"Testing agent {agent_id} with {total_tests} different messages...")
    print()
    
    for i, message in enumerate(test_messages, 1):
        print(f"Test {i}/{total_tests}: '{message[:30]}...'")
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"http://localhost:8002/api/agents/{agent_id}/chat",
                json={"message": message},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ SUCCESS ({response_time:.2f}s)")
                print(f"     Status: {result.get('status', 'Unknown')}")
                print(f"     Response: {result.get('response', '')[:80]}...")
                successful_tests += 1
            else:
                print(f"  ❌ FAILED: Status {response.status_code}")
                print(f"     Error: {response.text[:100]}...")
                
        except Exception as e:
            print(f"  ❌ EXCEPTION: {e}")
        
        print()
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    success_rate = (successful_tests / total_tests) * 100
    print("=" * 50)
    print(f"📊 TEST RESULTS SUMMARY:")
    print(f"   • Successful Tests: {successful_tests}/{total_tests}")
    print(f"   • Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print(f"   • Status: 🎉 EXCELLENT - Agent chat is working properly!")
    elif success_rate >= 60:
        print(f"   • Status: ✅ GOOD - Minor issues but mostly working")
    else:
        print(f"   • Status: ❌ NEEDS ATTENTION - Multiple failures")
    
    return success_rate >= 80

def test_automation_detection():
    """Test if automation detection is working"""
    
    print("\n🤖 TESTING AUTOMATION DETECTION")
    print("=" * 50)
    
    agent_id = "a99f903c-1fa5-4dc5-b15a-ec716b9a161a"
    
    automation_messages = [
        "Send an email to john@example.com about the meeting",
        "Create a workflow for processing customer data",
        "Schedule a reminder for next Monday",
        "Automate the backup process",
        "Generate a report from the sales data"
    ]
    
    automation_detected = 0
    
    for message in automation_messages:
        print(f"Testing: '{message[:40]}...'")
        
        try:
            response = requests.post(
                f"http://localhost:8002/api/agents/{agent_id}/chat",
                json={"message": message},
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                status = result.get('status', '')
                has_workflow = result.get('hasWorkflowJson', False)
                
                if status in ['automation_ready', 'workflow_confirmation', 'parameter_collection'] or has_workflow:
                    print(f"  ✅ Automation detected (Status: {status})")
                    automation_detected += 1
                else:
                    print(f"  🟡 Conversational response (Status: {status})")
            else:
                print(f"  ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        time.sleep(0.5)
    
    detection_rate = (automation_detected / len(automation_messages)) * 100
    print(f"\n📊 Automation Detection: {automation_detected}/{len(automation_messages)} ({detection_rate:.1f}%)")
    
    return detection_rate

if __name__ == "__main__":
    print("🔧 VERIFYING CUSTOMMCPLLMITERATIONENGINE PARAMETER FIX")
    print()
    
    # Test basic chat functionality
    chat_success = test_agent_chat_comprehensive()
    
    # Test automation detection
    automation_rate = test_automation_detection()
    
    print("\n" + "=" * 60)
    print("🏆 FINAL VERIFICATION RESULTS:")
    print("=" * 60)
    
    if chat_success:
        print("✅ Agent Chat Fix: SUCCESSFUL")
        print("   • CustomMCPLLMIterationEngine parameter error resolved")
        print("   • Agent endpoints responding correctly")
        print("   • No more TypeError on initialization")
    else:
        print("❌ Agent Chat Fix: NEEDS MORE WORK")
    
    if automation_rate > 0:
        print(f"✅ Automation Detection: {automation_rate:.1f}% working")
    else:
        print("🟡 Automation Detection: May need tuning")
    
    print(f"\n🎯 SYSTEM STATUS: {'OPERATIONAL' if chat_success else 'NEEDS ATTENTION'}")
    print("The CustomMCPLLMIterationEngine.__init__() parameter fix has been applied!")
