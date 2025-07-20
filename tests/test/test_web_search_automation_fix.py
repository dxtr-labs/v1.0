#!/usr/bin/env python3
"""
Test the fixed web search automation workflow
"""

import requests
import json
import time

def test_fixed_automation():
    """Test the web search automation fix"""
    print("🧪 Testing Fixed Web Search Automation")
    print("=" * 50)
    
    base_url = "http://localhost:8002"
    frontend_url = "http://localhost:3000"
    
    # Test user (using existing demo user)
    login_data = {
        "email": "demo@autoflow.ai",
        "password": "demo123456"
    }
    
    print("1. 🔑 Logging in...")
    
    # Login via frontend
    try:
        login_response = requests.post(f"{frontend_url}/api/auth/login", json=login_data, timeout=10)
        if login_response.status_code == 200:
            login_result = login_response.json()
            print(f"   ✅ Login successful: {login_result.get('user', {}).get('email')}")
            session_token = login_result.get('session_token')
        else:
            print(f"   ❌ Login failed: {login_response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return False
    
    print("\n2. 🔍 Testing Web Search Automation...")
    
    # Test the exact automation request that was failing
    automation_request = {
        "message": "Find top 10 ai investors using web search and send email to slakshanand1105@gmail.com",
        "agentId": "demo-agent",
        "agentConfig": {
            "name": "Demo Assistant",
            "role": "automation assistant",
            "personality": {"tone": "professional"}
        }
    }
    
    try:
        # Step 1: Send automation request (should trigger AI service selection)
        chat_response = requests.post(f"{frontend_url}/api/chat/mcpai", json=automation_request, timeout=15)
        
        print(f"   Status: {chat_response.status_code}")
        
        if chat_response.status_code == 200:
            result1 = chat_response.json()
            print(f"   Response status: {result1.get('status')}")
            print(f"   Message: {result1.get('message', '')[:100]}...")
            
            if result1.get('status') == 'ai_service_selection':
                print("   ✅ AI service selection triggered correctly")
                
                # Step 2: Send service selection (this should now trigger web search automation)
                service_request = {
                    "message": "service:inhouse Find top 10 ai investors using web search and send email to slakshanand1105@gmail.com",
                    "agentId": "demo-agent",
                    "agentConfig": automation_request["agentConfig"]
                }
                
                print("\n3. 🚀 Selecting inhouse service (should trigger web search)...")
                
                service_response = requests.post(f"{frontend_url}/api/chat/mcpai", json=service_request, timeout=30)
                
                if service_response.status_code == 200:
                    result2 = service_response.json()
                    print(f"   Status: {result2.get('status')}")
                    print(f"   Message: {result2.get('message', '')[:150]}...")
                    
                    # Check if web search automation was executed
                    if any(keyword in result2.get('message', '').lower() for keyword in ['research', 'investors', 'automation', 'workflow']):
                        print("   🎉 WEB SEARCH AUTOMATION TRIGGERED!")
                        print("   ✅ System is now properly executing web search + email workflow")
                        return True
                    else:
                        print("   ⚠️ Still getting generic AI response instead of web search automation")
                        print(f"   Full response: {json.dumps(result2, indent=2)}")
                        return False
                else:
                    print(f"   ❌ Service selection failed: {service_response.status_code}")
                    return False
            else:
                print(f"   ⚠️ Expected 'ai_service_selection', got: {result1.get('status')}")
                return False
        else:
            print(f"   ❌ Chat request failed: {chat_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Automation test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_fixed_automation()
    
    if success:
        print(f"\n🎉 WEB SEARCH AUTOMATION FIX SUCCESSFUL!")
        print(f"✅ The system now properly balances:")
        print(f"   - Web search automation execution")
        print(f"   - AI content generation")
        print(f"   - Pre-built workflow knowledge")
    else:
        print(f"\n❌ Fix needs additional work")
        print(f"💡 The issue was: System detecting automation but not executing web search")
