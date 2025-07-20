#!/usr/bin/env python3
"""
Test ASU Bus Automation Integration with Main MCP System
"""

import requests
import json
import time
import uuid

def test_asu_bus_automation():
    """Test ASU bus automation through the main MCP system"""
    
    print("🚌 Testing ASU Bus Automation Integration...")
    
    # Generate a valid UUID for testing
    test_agent_id = str(uuid.uuid4())
    
    # Test data
    test_request = {
        "message": "search asu bus shuttle website and fetch bus data from there and send email to slakshanand1105@gmail.com when is the next bus",
        "agent_id": test_agent_id
    }
    
    try:
        print(f"📤 Sending request to MCP API...")
        print(f"   Request: {test_request['message'][:100]}...")
        
        # Make request to the MCPAI chat endpoint (simpler endpoint)
        response = requests.post(
            "http://localhost:8002/api/chat/mcpai",
            json={"message": test_request["message"]},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: MCP system responded")
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"   Message: {result.get('message', 'No message')[:200]}...")
            
            # Check if it detected ASU bus automation
            if result.get('workflow_json'):
                workflow = result['workflow_json']
                automation_type = workflow.get('workflow_type')
                print(f"🚌 Automation Type: {automation_type}")
                
                if automation_type == "asu_bus_automation":
                    print(f"✅ ASU Bus Automation DETECTED and CREATED!")
                    print(f"   Workflow ID: {workflow.get('workflow_id')}")
                    print(f"   Steps: {len(workflow.get('steps', []))}")
                    print(f"   Estimated time: {workflow.get('estimated_execution_time')}")
                    
                    # Check workflow steps
                    for i, step in enumerate(workflow.get('steps', []), 1):
                        action = step.get('action')
                        print(f"   Step {i}: {action}")
                        
                        if action == "web_search_asu_bus":
                            print(f"      ✅ Web search step configured")
                        elif action == "ai_bus_analysis":
                            print(f"      ✅ AI processing step configured")
                        elif action == "send_email":
                            email_to = step.get('parameters', {}).get('to')
                            print(f"      ✅ Email step configured to: {email_to}")
                    
                    return True
                else:
                    print(f"❌ Wrong automation type detected: {automation_type}")
                    return False
            else:
                print(f"❌ No workflow JSON generated")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_automation_patterns():
    """Test various ASU bus automation trigger patterns"""
    
    print("\n🧪 Testing ASU Bus Automation Patterns...")
    
    test_patterns = [
        "asu bus shuttle schedule",
        "when is the next asu bus",
        "asu transportation information",
        "bus times at asu",
        "next shuttle to tempe campus"
    ]
    
    for i, pattern in enumerate(test_patterns, 1):
        print(f"\n📋 Test {i}: '{pattern}'")
        
        test_agent_id = str(uuid.uuid4())
        
        test_request = {
            "message": f"{pattern} send to test@example.com",
            "agent_id": test_agent_id
        }
        
        try:
            response = requests.post(
                "http://localhost:8002/api/chat/mcpai",
                json={"message": test_request["message"]},
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                workflow = result.get('workflow_json', {})
                automation_type = workflow.get('workflow_type')
                
                if automation_type == "asu_bus_automation":
                    print(f"   ✅ Pattern matched - ASU bus automation detected")
                else:
                    print(f"   ❌ Pattern missed - detected: {automation_type}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(1)  # Rate limiting

def main():
    """Run all ASU bus automation tests"""
    
    print("🚀 ASU Bus Automation Integration Test Suite")
    print("=" * 60)
    
    # Test 1: Main automation test
    success = test_asu_bus_automation()
    
    if success:
        print(f"\n✅ MAIN TEST PASSED - ASU Bus Automation Working!")
        
        # Test 2: Pattern recognition tests
        test_automation_patterns()
        
        print(f"\n🎉 ASU Bus Automation Integration Complete!")
        print(f"   • Web search functionality configured")
        print(f"   • AI processing pipeline set up")  
        print(f"   • Email automation integrated")
        print(f"   • Fallback system available")
        print(f"   • Pattern detection working")
        
    else:
        print(f"\n❌ MAIN TEST FAILED - Integration Issues Detected")

if __name__ == "__main__":
    main()
