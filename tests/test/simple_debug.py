#!/usr/bin/env python3
"""
🔍 SIMPLE AUTOMATION DEBUG
Single test to capture detailed backend logs
"""

import requests
import json
import time

def simple_automation_test():
    """Single automation test with timing"""
    
    base_url = "http://localhost:8002"
    
    # Login first
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "email": "aitest@example.com",
        "password": "testpass123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    session_token = login_response.json().get("session_token")
    headers = {"Cookie": f"session_token={session_token}"}
    
    print("🔥 SENDING AUTOMATION REQUEST")
    print("=" * 50)
    
    payload = {"message": "Send an email to test@example.com"}
    
    print(f"📤 Message: {payload['message']}")
    print(f"⏰ Time: {time.time()}")
    
    response = requests.post(f"{base_url}/api/chat/mcpai", 
        json=payload,
        headers=headers,
        timeout=30
    )
    
    print(f"⏰ Response Time: {time.time()}")
    print(f"📊 Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n🎯 RESPONSE SUMMARY:")
        print(f"   automation_type: {result.get('automation_type')}")
        print(f"   hasWorkflowJson: {result.get('hasWorkflowJson')}")
        print(f"   status: {result.get('status')}")
        print(f"   message: {result.get('message', '')[:100]}...")
        
        return result
    else:
        print(f"❌ Request failed: {response.status_code}")
        return None

if __name__ == "__main__":
    simple_automation_test()
