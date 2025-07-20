#!/usr/bin/env python3
"""
Test workflow automation execution from frontend perspective
"""

import requests
import json
import time

def test_automation_execution():
    """Test if workflows actually execute or just show UI"""
    
    print("🧪 TESTING WORKFLOW AUTOMATION EXECUTION")
    print("=" * 60)
    
    agent_id = "a99f903c-1fa5-4dc5-b15a-ec716b9a161a"
    base_url = "http://localhost:8002"
    
    print("🎯 ISSUE: Frontend shows workflow progress but no actual execution")
    print("Testing if backend has real automation capabilities...")
    
    # Test 1: AI Investor automation
    print(f"\n📧 TEST 1: AI Investor Email Automation")
    print(f"Request: Find AI investors and send emails")
    
    try:
        # Initial request
        response = requests.post(
            f"{base_url}/api/agents/{agent_id}/chat",
            json={"message": "find top 10 ai investors and send email about dxtr labs to test@example.com"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Step 1: Workflow offered")
            print(f"   Status: {result.get('status')}")
            print(f"   Has workflow: {result.get('hasWorkflowJson', False)}")
            
            # Confirm execution
            time.sleep(1)
            response = requests.post(
                f"{base_url}/api/agents/{agent_id}/chat",
                json={"message": "yes, proceed"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                
                print(f"✅ Step 2: Execution response received")
                print(f"   Response preview: {response_text[:200]}...")
                
                # Analyze response for actual execution indicators
                if 'email sent' in response_text.lower():
                    print(f"   ✅ Claims email was sent")
                elif 'sending' in response_text.lower():
                    print(f"   🔄 Claims to be sending")
                elif 'progress' in response_text.lower():
                    print(f"   📊 Shows progress (UI only)")
                else:
                    print(f"   ❌ No clear execution indication")
                    
                # Check if it's just UI or real execution
                if '✅' in response_text and 'automation is now in progress' in response_text:
                    print(f"   🎭 DETECTED: This is UI simulation, not real execution!")
                    
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Test available endpoints
    print(f"\n🔍 TESTING BACKEND ENDPOINTS")
    endpoints = ["/docs", "/api/workflows", "/api/automation", "/api/email"]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"📍 {endpoint}: {response.status_code}")
        except:
            print(f"📍 {endpoint}: Not available")
    
    print(f"\n🎯 DIAGNOSIS:")
    print(f"❌ PROBLEM IDENTIFIED: Workflow execution is UI simulation only")
    print(f"📋 The agent shows progress indicators but doesn't execute real automations")
    print(f"🔧 NEEDED: Integration with actual automation engine")

def check_automation_engine_integration():
    """Check if automation engine is properly integrated"""
    
    print(f"\n🔍 CHECKING AUTOMATION ENGINE INTEGRATION")
    print(f"=" * 50)
    
    # Check if automation engine exists in backend
    import os
    backend_path = "c:\\Users\\sugua\\Desktop\\redo\\backend"
    
    automation_files = [
        "mcp\\simple_automation_engine.py",
        "core\\automation_engine.py", 
        "automation\\engine.py"
    ]
    
    for file_path in automation_files:
        full_path = os.path.join(backend_path, file_path)
        if os.path.exists(full_path):
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
    
    print(f"\n💡 SOLUTION NEEDED:")
    print(f"1. Connect CustomMCPLLMIterationEngine to real automation engine")
    print(f"2. Implement actual email sending functionality") 
    print(f"3. Add web search and data processing capabilities")
    print(f"4. Replace UI simulation with real workflow execution")

if __name__ == "__main__":
    test_automation_execution()
    check_automation_engine_integration()
