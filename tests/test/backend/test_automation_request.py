#!/usr/bin/env python3
"""
Test the specific automation request that was failing
"""

import requests
import json

def test_automation_request():
    """Test the specific automation request that caused the original error"""
    
    base_url = "http://localhost:8002"
    
    # The specific request that was failing
    test_message = "search web for top 10 investors in ai and send email to slakshanand1105@gmail.com"
    
    print(f"🧪 Testing automation request:")
    print(f"   Message: {test_message}")
    
    # Try different endpoints to see which one works
    endpoints = [
        "/api/chat/mcpai",
        "/api/chat/simple"
    ]
    
    for endpoint in endpoints:
        print(f"\n🔍 Testing endpoint: {endpoint}")
        
        try:
            response = requests.post(
                f"{base_url}{endpoint}",
                json={"message": test_message},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success!")
                print(f"   Response: {result.get('response', 'No response')[:200]}...")
                print(f"   Status: {result.get('status', 'unknown')}")
                return True
            else:
                print(f"   ❌ Failed: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return False

if __name__ == "__main__":
    print("🧪 Testing the specific automation request that was failing...")
    if test_automation_request():
        print("\n✅ Automation request system working!")
    else:
        print("\n❌ Automation request system still has issues")
