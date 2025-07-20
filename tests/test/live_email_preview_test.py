#!/usr/bin/env python3
"""
Live Application Email Preview Test
"""
import requests
import json
import time

def test_live_email_preview():
    print("🧪 TESTING LIVE EMAIL PREVIEW FUNCTIONALITY")
    print("=" * 60)
    
    # Use the frontend API that's already working
    frontend_api_url = "http://localhost:3002/api/chat/mcpai"
    
    # Email preview request that should trigger frontend detection
    email_request = {
        "message": "create a professional welcome email for new customers and send it to test@example.com - please show me a preview first",
        "agentId": "c4defde2-c7c2-43f2-aa0c-9d8c1abd6d35",  # Using the active agent from logs
        "agentConfig": {
            "name": "Sam",
            "role": "Personal Assistant", 
            "personality": "kind and generous",
            "llm_config": {}
        }
    }
    
    print(f"📧 Sending email preview request through frontend API...")
    print(f"   URL: {frontend_api_url}")
    print(f"   Agent ID: {email_request['agentId']}")
    
    try:
        response = requests.post(frontend_api_url, json=email_request, timeout=30)
        
        print(f"\n📊 RESPONSE STATUS: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Response received successfully")
            print(f"\n📋 RESPONSE ANALYSIS:")
            print(f"   Status: {result.get('status')}")
            print(f"   Action Required: {result.get('action_required')}")
            print(f"   Message: {result.get('message', 'N/A')[:100]}...")
            
            # Check if this would trigger frontend preview
            is_preview_ready = result.get('status') == 'preview_ready'
            is_approve_email = result.get('action_required') == 'approve_email'
            has_email_content = bool(result.get('email_content'))
            has_recipient = bool(result.get('recipient'))
            
            print(f"\n🎯 FRONTEND TRIGGER CONDITIONS:")
            print(f"   ✅ Status 'preview_ready': {is_preview_ready}")
            print(f"   ✅ Action 'approve_email': {is_approve_email}")
            print(f"   ✅ Has email content: {has_email_content}")
            print(f"   ✅ Has recipient: {has_recipient}")
            
            frontend_ready = is_preview_ready and is_approve_email and has_email_content and has_recipient
            
            if frontend_ready:
                print(f"\n🎉 SUCCESS! Frontend should show email preview dialog!")
                print(f"   Recipient: {result.get('recipient')}")
                print(f"   Subject: {result.get('email_subject', 'N/A')}")
                if result.get('email_content'):
                    content_preview = result.get('email_content')[:150]
                    print(f"   Content preview: {content_preview}...")
                
                # Test data structure that frontend expects
                print(f"\n📧 EMAIL PREVIEW DATA STRUCTURE:")
                preview_data = {
                    "title": "Email Preview",
                    "description": f"Review your email before sending to {result.get('recipient')}",
                    "email_preview": {
                        "to": result.get('recipient'),
                        "subject": result.get('email_subject'),
                        "preview_content": result.get('email_content'),
                        "ai_service": 'openai'
                    }
                }
                print(f"   Frontend will create: {json.dumps(preview_data, indent=2)[:300]}...")
                
                return True
            else:
                print(f"\n❌ Response doesn't match frontend preview expectations")
                print(f"   Status: {result.get('status')} (expected: preview_ready)")
                print(f"   Action: {result.get('action_required')} (expected: approve_email)")
                return False
                
        else:
            error_text = response.text
            print(f"❌ Request failed with status {response.status_code}")
            print(f"   Error: {error_text[:300]}...")
            return False
            
    except requests.exceptions.Timeout:
        print(f"⏰ Request timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def check_live_application_status():
    print(f"\n🌐 CHECKING LIVE APPLICATION STATUS")
    print("=" * 60)
    
    # Check frontend
    try:
        frontend_response = requests.get("http://localhost:3002", timeout=5)
        frontend_ok = frontend_response.status_code == 200
        print(f"Frontend (localhost:3002): {'✅ Running' if frontend_ok else '❌ Down'}")
    except:
        frontend_ok = False
        print(f"Frontend (localhost:3002): ❌ Not accessible")
    
    # Check backend
    try:
        backend_response = requests.get("http://localhost:8002", timeout=5)
        backend_ok = backend_response.status_code in [200, 404]  # 404 is OK, means server is running
        print(f"Backend (localhost:8002): {'✅ Running' if backend_ok else '❌ Down'}")
    except:
        backend_ok = False
        print(f"Backend (localhost:8002): ❌ Not accessible")
    
    return frontend_ok and backend_ok

if __name__ == "__main__":
    print("🚀 TESTING LIVE EMAIL PREVIEW SYSTEM")
    print("=" * 60)
    
    # Check if application is running
    if not check_live_application_status():
        print(f"\n❌ Application not fully running. Please start both frontend and backend.")
        exit(1)
    
    # Test email preview functionality
    success = test_live_email_preview()
    
    print(f"\n📊 LIVE TEST RESULTS")
    print("=" * 60)
    
    if success:
        print(f"🎉 EMAIL PREVIEW SYSTEM IS WORKING!")
        print(f"   ✅ Backend generates correct preview responses")
        print(f"   ✅ Frontend API integration working")
        print(f"   ✅ Response format matches frontend expectations")
        print(f"   ✅ Email preview dialog should display properly")
        print(f"\n🎯 NEXT STEPS:")
        print(f"   1. Open browser to http://localhost:3002")
        print(f"   2. Login and navigate to agent chat")
        print(f"   3. Request: 'create welcome email for test@example.com'")
        print(f"   4. Verify email preview dialog appears")
    else:
        print(f"❌ EMAIL PREVIEW SYSTEM NEEDS ATTENTION")
        print(f"   Backend may not be generating proper preview responses")
        print(f"   Check backend logs and response format")
