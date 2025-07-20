#!/usr/bin/env python3
"""
Quick test to verify the system is working
"""

import requests
import json
import time

def quick_system_test():
    print("🚀 Quick System Test")
    print("=" * 30)
    
    base_url = "http://localhost:8002"
    
    # Test 1: Health check
    print("1. Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            health = response.json()
            print(f"   Database: {health.get('database')}")
            print(f"   Status: {health.get('status')}")
        else:
            print(f"   ❌ Health check failed")
            return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False
    
    # Test 2: Chat endpoint
    print("\n2. Chat API Test...")
    try:
        chat_data = {
            "message": "I want to send an email to john@example.com about project updates",
            "session_id": "test_session"
        }
        
        response = requests.post(f"{base_url}/api/chat/mcpai", json=chat_data, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Response type: {result.get('response_type')}")
            print(f"   Status: {result.get('status')}")
            
            # Check for workflow status (should be ai_service_selection, not completed)
            if result.get('status') == 'ai_service_selection':
                print("   ✅ Workflow status fixed!")
            elif result.get('status') == 'completed':
                print("   ⚠️ Still showing 'completed' status")
            else:
                print(f"   Status: {result.get('status')}")
        else:
            print(f"   ❌ Chat failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Chat error: {e}")
        return False
    
    print("\n✅ Quick test completed!")
    return True

if __name__ == "__main__":
    quick_system_test()
