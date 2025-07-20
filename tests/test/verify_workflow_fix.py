#!/usr/bin/env python3
"""
Quick verification of fixed workflow system
"""

import requests
import json
import time

def test_workflow_fix():
    base_url = "http://localhost:8002"
    
    print("🧪 Testing Fixed Workflow System")
    print("=" * 50)
    
    # Test 1: Simple automation request
    print("\n📧 Test 1: Email automation detection")
    automation_request = {
        "message": "Send a weekly sales report email to john@company.com every Monday at 9 AM",
        "session_id": f"test-automation-{int(time.time())}"
    }
    
    try:
        response = requests.post(
            f"{base_url}/chat",
            json=automation_request,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response Status: {result.get('status', 'No status')}")
            print(f"Message: {result.get('response', 'No response')[:200]}...")
            
            # Check if status is ai_service_selection (the fix we implemented)
            if result.get('status') == 'ai_service_selection':
                print("✅ SUCCESS: Status correctly shows 'ai_service_selection'")
            else:
                print(f"❌ ISSUE: Expected 'ai_service_selection' but got '{result.get('status')}'")
        else:
            print(f"❌ HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
    
    # Test 2: Service selection
    print("\n🤖 Test 2: Service selection")
    service_request = {
        "message": "service:openai",
        "session_id": automation_request["session_id"]
    }
    
    try:
        response = requests.post(
            f"{base_url}/chat",
            json=service_request,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response Status: {result.get('status', 'No status')}")
            print(f"Message: {result.get('response', 'No response')[:200]}...")
            
            # Check if we get workflow preview
            if 'workflow_preview' in result.get('status', ''):
                print("✅ SUCCESS: Service selection working, showing workflow preview")
            else:
                print(f"⚠️  Status: {result.get('status')}")
        else:
            print(f"❌ HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
    
    # Test 3: Simple conversation (should not trigger automation)
    print("\n💭 Test 3: Simple conversation")
    conversation_request = {
        "message": "Hello, how are you today?",
        "session_id": f"test-conversation-{int(time.time())}"
    }
    
    try:
        response = requests.post(
            f"{base_url}/chat",
            json=conversation_request,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response Status: {result.get('status', 'No status')}")
            print(f"Message: {result.get('response', 'No response')[:200]}...")
            
            # Should stay conversational
            if result.get('status') == 'conversational':
                print("✅ SUCCESS: Conversational requests properly handled")
            else:
                print(f"⚠️  Unexpected status for conversation: {result.get('status')}")
        else:
            print(f"❌ HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

    print("\n" + "=" * 50)
    print("🎯 Workflow Fix Verification Complete")

if __name__ == "__main__":
    test_workflow_fix()
