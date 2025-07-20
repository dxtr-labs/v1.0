#!/usr/bin/env python3

# Test the complete API email workflow
import asyncio
import aiohttp
import json

async def test_api_email_workflow():
    """Test end-to-end email workflow through the API"""
    print("🧪 Testing API Email Workflow")
    print("=" * 40)
    
    base_url = "http://localhost:8002"
    email = "slakshanand1105@gmail.com"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test signup and login first
            print("1️⃣ Testing signup...")
            signup_data = {
                "username": "test_user_email",
                "email": email,
                "password": "testpass123"
            }
            
            async with session.post(f"{base_url}/api/auth/signup", json=signup_data) as resp:
                if resp.status == 200:
                    signup_result = await resp.json()
                    print(f"✅ Signup: {signup_result.get('message', 'Success')}")
                else:
                    print(f"⚠️ Signup: {resp.status} (might already exist)")
            
            # Login
            print("2️⃣ Testing login...")
            login_data = {
                "username": "test_user_email",
                "password": "testpass123"
            }
            
            async with session.post(f"{base_url}/api/auth/login", json=login_data) as resp:
                if resp.status == 200:
                    login_result = await resp.json()
                    user_id = login_result.get("user", {}).get("user_id")
                    session_token = login_result.get("session_token")
                    print(f"✅ Login successful: {user_id}")
                    
                    # Set session headers
                    session.headers.update({
                        "x-user-id": user_id,
                        "Cookie": f"session_token={session_token}"
                    })
                else:
                    print(f"❌ Login failed: {resp.status}")
                    return False
            
            # Test the email automation
            print("3️⃣ Testing email automation...")
            chat_data = {
                "user_input": f"draft a sales pitch and send email to {email}",
                "agent_id": "test_agent_123",
                "conversation_id": "test_conv_123"
            }
            
            async with session.post(f"{base_url}/api/chat/mcpai", json=chat_data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    print("📊 API Response:")
                    print(f"  Status: {result.get('status')}")
                    print(f"  Success: {result.get('success')}")
                    print(f"  Message: {result.get('message', 'No message')[:100]}...")
                    print(f"  Email sent: {result.get('email_sent')}")
                    print(f"  Workflow ID: {result.get('workflow_id')}")
                    print(f"  Has workflow: {result.get('hasWorkflowJson')}")
                    
                    if result.get('email_sent'):
                        print("🎉 SUCCESS: API reports email was sent!")
                        return True
                    else:
                        print("❌ ISSUE: API reports email_sent as null/false")
                        print(f"Full response: {json.dumps(result, indent=2)}")
                        return False
                else:
                    print(f"❌ API request failed: {resp.status}")
                    response_text = await resp.text()
                    print(f"Error: {response_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_api_email_workflow())
    if success:
        print("\n✅ End-to-end email workflow successful!")
    else:
        print("\n❌ End-to-end test failed!")
