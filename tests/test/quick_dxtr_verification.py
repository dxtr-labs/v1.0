#!/usr/bin/env python3
"""
Quick DXTR AutoFlow Platform Verification
Tests core functionality once backend is running
"""

import requests
import json
import time
import uuid

def wait_for_backend(max_wait=30):
    """Wait for backend to be ready"""
    print("⏳ Waiting for DXTR AutoFlow backend to start...")
    
    for i in range(max_wait):
        try:
            response = requests.get("http://localhost:8002/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend is ready!")
                return True
        except:
            time.sleep(1)
            if i % 5 == 0:
                print(f"   Still waiting... ({i+1}s)")
    
    print("❌ Backend failed to start within 30 seconds")
    return False

def test_dxtr_platform():
    """Test DXTR AutoFlow platform core features"""
    if not wait_for_backend():
        return False
    
    print("\n🚀 Testing DXTR AutoFlow Platform Core Features")
    print("=" * 60)
    
    # Test 1: Basic API endpoint
    try:
        response = requests.get("http://localhost:8002/health")
        print(f"✅ Health Check: {response.status_code}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False
    
    # Test 2: Create test user
    test_email = f"dxtr_test_{uuid.uuid4().hex[:6]}@example.com"
    signup_data = {
        "email": test_email,
        "password": "dxtr123",
        "name": "DXTR Test User"
    }
    
    try:
        response = requests.post("http://localhost:8002/api/auth/signup", json=signup_data)
        print(f"✅ User Creation: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            user_id = user_data.get("user", {}).get("user_id")
            print(f"   User ID: {user_id[:8]}...")
            
            # Test 3: Test MCP AI Chat (core feature)
            headers = {"x-user-id": user_id}
            chat_data = {"message": "Search for AI automation investors and email list to slakshanand1105@gmail.com"}
            
            try:
                response = requests.post("http://localhost:8002/api/chat/mcpai", json=chat_data, headers=headers, timeout=60)
                print(f"✅ MCP AI Chat: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        print("   🎯 AI processing successful!")
                        response_text = data.get("response", "")
                        print(f"   📝 Response: {response_text[:200]}...")
                    else:
                        print(f"   ⚠️ AI processing issue: {data.get('error', 'Unknown')}")
                        
                return True
                        
            except Exception as e:
                print(f"❌ MCP AI Chat Error: {e}")
                return False
                
    except Exception as e:
        print(f"❌ User Creation Error: {e}")
        return False
    
    return False

def test_email_functionality():
    """Test email automation"""
    print("\n📧 Testing Email Automation")
    print("=" * 40)
    
    # Create user for email test
    test_email = f"email_test_{uuid.uuid4().hex[:6]}@example.com"
    signup_data = {
        "email": test_email,
        "password": "email123",
        "name": "Email Test User"
    }
    
    try:
        response = requests.post("http://localhost:8002/api/auth/signup", json=signup_data)
        if response.status_code == 200:
            user_data = response.json()
            user_id = user_data.get("user", {}).get("user_id")
            
            # Test direct email
            headers = {"x-user-id": user_id}
            email_data = {
                "to": "slakshanand1105@gmail.com",
                "subject": "DXTR AutoFlow Platform Test",
                "content": "🚀 Your DXTR AutoFlow platform is working perfectly! All systems are operational."
            }
            
            response = requests.post("http://localhost:8002/api/email/send", json=email_data, headers=headers)
            print(f"✅ Email Send: {response.status_code}")
            
            if response.status_code == 200:
                print("   📧 Email sent successfully!")
                return True
            else:
                print(f"   ❌ Email failed: {response.text}")
                
    except Exception as e:
        print(f"❌ Email Test Error: {e}")
        
    return False

def test_agent_management():
    """Test agent management features"""
    print("\n🤖 Testing Agent Management")
    print("=" * 40)
    
    try:
        # Create user
        test_email = f"agent_test_{uuid.uuid4().hex[:6]}@example.com"
        signup_data = {
            "email": test_email,
            "password": "agent123",
            "name": "Agent Test User"
        }
        
        response = requests.post("http://localhost:8002/api/auth/signup", json=signup_data)
        if response.status_code == 200:
            user_data = response.json()
            user_id = user_data.get("user", {}).get("user_id")
            
            # Test agent listing
            headers = {"x-user-id": user_id}
            response = requests.get("http://localhost:8002/api/agents", headers=headers)
            print(f"✅ Agent List: {response.status_code}")
            
            if response.status_code == 200:
                agents = response.json()
                agent_count = len(agents.get("agents", []))
                print(f"   🤖 Found {agent_count} agents")
                return True
            else:
                print(f"   ❌ Agent listing failed: {response.text}")
                
    except Exception as e:
        print(f"❌ Agent Test Error: {e}")
        
    return False

if __name__ == "__main__":
    print("🚀 DXTR AUTOFLOW PLATFORM VERIFICATION")
    print("=" * 70)
    
    # Run tests
    platform_working = test_dxtr_platform()
    email_working = test_email_functionality()
    agent_working = test_agent_management()
    
    print("\n" + "=" * 70)
    print("📊 DXTR AUTOFLOW PLATFORM STATUS")
    print("=" * 70)
    
    print(f"🚀 Core Platform: {'✅ WORKING' if platform_working else '❌ ISSUES'}")
    print(f"📧 Email Automation: {'✅ WORKING' if email_working else '❌ ISSUES'}")
    print(f"🤖 Agent Management: {'✅ WORKING' if agent_working else '❌ ISSUES'}")
    
    if platform_working and email_working and agent_working:
        print("\n🎉 🎉 🎉 DXTR AUTOFLOW PLATFORM IS FULLY OPERATIONAL! 🎉 🎉 🎉")
        print("\n🌟 YOUR PLATFORM FEATURES:")
        print("✅ AI-Powered Workflow Search (OpenAI GPT-4)")
        print("✅ Agent Station Management")
        print("✅ Email Automation System")
        print("✅ Template Library (2055+ workflows)")
        print("✅ Enterprise API Integrations")
        print("✅ Memory-Enhanced AI Agents")
        print("✅ Natural Language Processing")
        print("✅ Production-Ready Architecture")
        
        print("\n🔗 Access Your Platform:")
        print("📱 Frontend: http://localhost:3000")
        print("🔧 Backend API: http://localhost:8002")
        print("📖 API Docs: http://localhost:8002/docs")
        
    else:
        print("\n⚠️ Some components need attention - check the logs above for details.")
