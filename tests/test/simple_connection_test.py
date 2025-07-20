#!/usr/bin/env python3
"""
Simple connection test to verify server is responsive
"""

import requests
import json

def test_connection():
    base_url = "http://localhost:8002"
    
    print("🔌 Testing server connection...")
    
    try:
        # Test basic connectivity
        response = requests.get(f"{base_url}/docs", timeout=5)
        print(f"✅ Server responding on port 8002: {response.status_code}")
        
        # Test chat endpoint
        test_request = {
            "message": "Hello, are you working?",
            "session_id": "test-session-123"
        }
        
        chat_response = requests.post(
            f"{base_url}/chat", 
            json=test_request,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"✅ Chat endpoint responding: {chat_response.status_code}")
        if chat_response.status_code == 200:
            result = chat_response.json()
            print(f"📝 Response: {result.get('response', 'No response field')[:100]}...")
            print(f"🔄 Status: {result.get('status', 'No status field')}")
        else:
            print(f"❌ Chat error: {chat_response.text}")
            
    except requests.exceptions.ConnectRefused:
        print("❌ Connection refused - server not running on port 8002")
    except requests.exceptions.Timeout:
        print("❌ Connection timeout - server might be overloaded")
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_connection()
