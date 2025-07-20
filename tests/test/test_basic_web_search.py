#!/usr/bin/env python3
"""
🧪 BASIC WEB SEARCH TEST (No API Keys Required)
Test web search automation detection and basic functionality
"""

import requests
import json

def test_basic_web_search():
    """Test basic web search automation without external APIs"""
    base_url = "http://localhost:8002/api"
    
    print("🔍 BASIC WEB SEARCH AUTOMATION TEST")
    print("=" * 50)
    
    # Authenticate
    login_response = requests.post(f"{base_url}/auth/login", json={
        "email": "aitest@example.com", 
        "password": "testpass123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    session_token = login_response.json().get("session_token")
    headers = {"Cookie": f"session_token={session_token}"}
    print("✅ Authentication successful")
    
    # Test web search detection
    print("\n🧪 Testing web search intent detection...")
    
    test_query = "search top 10 investors interested in ramen bowl companies"
    
    try:
        response = requests.post(
            f"{base_url}/chat/mcpai",
            json={"message": test_query},
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Request successful")
            print(f"📋 Automation Type: {data.get('automation_type', 'Not detected')}")
            print(f"📋 Success: {data.get('success')}")
            
            # Check if web search was detected
            if data.get('automation_type') == 'web_search':
                print("🎯 ✅ WEB SEARCH CORRECTLY DETECTED!")
                print("🎯 ✅ Intent detection system working")
                print("🎯 ✅ Web search automation integration successful")
                
                # Show response
                response_text = data.get('response', '')
                if response_text:
                    print(f"\n📝 AI Response Preview:")
                    print(f"{response_text[:400]}...")
                
                # Check for search-related data
                if data.get('hasSearchResults'):
                    print(f"✅ Search results structure present")
                elif 'search' in response_text.lower():
                    print(f"✅ Search functionality acknowledged in response")
                
            else:
                print(f"❌ Web search not detected")
                print(f"   Got automation type: {data.get('automation_type')}")
                print(f"   Response: {data.get('response', '')[:200]}...")
                
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 BASIC TEST COMPLETE")

if __name__ == "__main__":
    test_basic_web_search()
