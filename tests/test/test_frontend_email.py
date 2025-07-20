#!/usr/bin/env python3
"""
Frontend Email Test - Test the exact frontend workflow
"""
import aiohttp
import asyncio
import json

async def test_frontend_email_workflow():
    """Test the frontend email workflow that was failing"""
    print("🚀 TESTING FRONTEND EMAIL WORKFLOW")
    print("=" * 50)
    
    backend_url = "http://localhost:8002"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test 1: Authentication
            print("🔐 Step 1: Authenticating...")
            auth_data = {
                "email": "testautomation@example.com",
                "password": "testpass123"
            }
            
            async with session.post(f"{backend_url}/api/auth/login", json=auth_data) as response:
                if response.status == 200:
                    auth_result = await response.json()
                    user_id = auth_result.get('user', {}).get('user_id') or auth_result.get('user_id')
                    session_token = auth_result.get('session_token')
                    print(f"✅ Authenticated as user: {user_id}")
                else:
                    print("⚠️ Using guest mode")
                    user_id = "test_frontend_user"
                    session_token = None
            
            # Test 2: Send the exact same request as frontend
            print("\n📧 Step 2: Sending email automation request...")
            
            headers = {'Content-Type': 'application/json'}
            if user_id and session_token:
                headers['x-user-id'] = user_id
                headers['Authorization'] = f'Bearer {session_token}'
            
            # This is the exact message from the frontend screenshot
            chat_data = {
                "message": "create a sales pitch email for selling healthy protein bars and send email to slakshanand1105@gmail.com",
                "user_id": user_id
            }
            
            print(f"Sending request: {chat_data['message']}")
            
            async with session.post(f"{backend_url}/api/chat/mcpai", 
                                   json=chat_data, 
                                   headers=headers) as response:
                
                response_time = response.headers.get('X-Response-Time', 'Unknown')
                
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Response received (Status: {response.status})")
                    print(f"📊 Response time: {response_time}")
                    print(f"🤖 Message: {result.get('message', 'No message')}")
                    print(f"📧 Email sent: {result.get('email_sent', 'Unknown')}")
                    print(f"🎯 Status: {result.get('status', 'Unknown')}")
                    
                    if result.get('email_sent') or result.get('status') == 'completed':
                        print("\n🎉 SUCCESS: Email should be delivered!")
                        print("📬 Check your inbox at slakshanand1105@gmail.com")
                    else:
                        print("\n⚠️ WARNING: Email may not have been sent")
                        print(f"Full response: {json.dumps(result, indent=2)}")
                        
                else:
                    error_text = await response.text()
                    print(f"❌ Request failed (Status: {response.status})")
                    print(f"Error: {error_text}")
                    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_frontend_email_workflow())
