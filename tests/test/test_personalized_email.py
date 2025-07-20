#!/usr/bin/env python3
"""
Test the new personalized content generation and email preview functionality
"""
import asyncio
import aiohttp
import json

async def test_personalized_email_preview():
    """Test the new personalized email generation with preview"""
    print("🚀 TESTING PERSONALIZED EMAIL WITH PREVIEW")
    print("=" * 60)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test different types of email requests
            test_requests = [
                {
                    "message": "create a sales pitch email for selling healthy protein bars and send email to slakshanand1105@gmail.com",
                    "description": "Healthy protein bars sales pitch"
                },
                {
                    "message": "draft a professional welcome email for new customers and send to slakshanand1105@gmail.com",
                    "description": "Welcome email for new customers"
                },
                {
                    "message": "compose a business proposal about AI solutions for enterprises and send to slakshanand1105@gmail.com",
                    "description": "AI solutions business proposal"
                }
            ]
            
            # Authenticate first
            auth_data = {
                "email": "testautomation@example.com",
                "password": "testpass123"
            }
            
            async with session.post("http://localhost:8002/api/auth/login", json=auth_data) as response:
                if response.status == 200:
                    auth_result = await response.json()
                    user_id = auth_result.get('user', {}).get('user_id') or auth_result.get('user_id')
                    session_token = auth_result.get('session_token')
                    print(f"✅ Authenticated as user: {user_id}")
                else:
                    user_id = "test_user"
                    session_token = None
                    print("⚠️ Using guest mode")
            
            headers = {'Content-Type': 'application/json'}
            if user_id and session_token:
                headers['x-user-id'] = user_id
                headers['Authorization'] = f'Bearer {session_token}'
            
            # Test each request type
            for i, test_req in enumerate(test_requests, 1):
                print(f"\n📧 TEST {i}: {test_req['description']}")
                print(f"Request: {test_req['message']}")
                print("-" * 40)
                
                chat_data = {
                    "message": test_req['message'],
                    "user_id": user_id
                }
                
                async with session.post("http://localhost:8002/api/chat/mcpai", 
                                       json=chat_data, 
                                       headers=headers) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        print(f"✅ Response Status: {result.get('status')}")
                        print(f"🎯 Automation Type: {result.get('automation_type')}")
                        print(f"📧 Preview Mode: {result.get('preview_mode', False)}")
                        print(f"🔍 Action Required: {result.get('action_required')}")
                        
                        if result.get('email_content'):
                            print(f"\n📄 GENERATED EMAIL CONTENT:")
                            print("=" * 50)
                            print(result['email_content'][:500] + "..." if len(result['email_content']) > 500 else result['email_content'])
                            print("=" * 50)
                            
                            # Check if content is personalized
                            content = result['email_content'].lower()
                            if 'protein bar' in test_req['message'].lower() and 'protein' in content:
                                print("✅ Content is PERSONALIZED for protein bars")
                            elif 'welcome' in test_req['message'].lower() and 'welcome' in content:
                                print("✅ Content is PERSONALIZED for welcome email")
                            elif 'ai solution' in test_req['message'].lower() and 'ai' in content:
                                print("✅ Content is PERSONALIZED for AI solutions")
                            else:
                                print("⚠️ Content may be generic")
                        else:
                            print("❌ No email content in response")
                        
                        if result.get('workflowPreviewContent'):
                            print(f"\n📋 Preview Content Available: {len(result['workflowPreviewContent'])} characters")
                        
                    else:
                        print(f"❌ Request failed (Status: {response.status})")
                        error_text = await response.text()
                        print(f"Error: {error_text[:200]}...")
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_personalized_email_preview())
