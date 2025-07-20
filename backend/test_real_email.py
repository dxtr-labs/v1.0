"""
Test real email automation with user's actual request
"""

import asyncio
import aiohttp
import json

BASE_URL = "http://localhost:8002"

async def test_real_email_request():
    """Test with the user's actual email request."""
    try:
        print("🧪 Testing Real Email Request")
        print("=" * 40)
        
        async with aiohttp.ClientSession() as session:
            
            # Create test user and agent quickly
            signup_data = {
                "email": f"realtest_{int(asyncio.get_event_loop().time())}@example.com",
                "password": "password123",
                "first_name": "Real",
                "last_name": "Test"
            }
            
            async with session.post(f"{BASE_URL}/api/auth/signup", json=signup_data) as resp:
                signup_result = await resp.json()
                token = signup_result.get("session_token")
                headers = {"Cookie": f"session_token={token}"}
                print("✅ User created")
            
            agent_data = {
                "name": "Email Assistant",
                "role": "Email Automation Specialist", 
                "personality": "Professional and efficient",
                "expectations": "Create perfect email automations"
            }
            
            async with session.post(f"{BASE_URL}/api/agents", json=agent_data, headers=headers) as resp:
                agent_result = await resp.json()
                agent_id = agent_result.get("agent", {}).get("id")
                print(f"✅ Agent created: {agent_id}")
            
            # Test the actual user request
            print(f"\n📨 User Request: 'send email to slakshanand1105@gmail.com'")
            print("-" * 40)
            
            chat_data = {
                "message": "send email to slakshanand1105@gmail.com"
            }
            
            async with session.post(f"{BASE_URL}/api/ai/chat/{agent_id}", json=chat_data, headers=headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    response = result.get('message', 'No response')
                    
                    print(f"🤖 AI Response:")
                    print(f"{response}")
                    
                    # Check what the system is asking for
                    if "subject" in response.lower() and "content" in response.lower():
                        print(f"\n✅ System correctly identified missing parameters!")
                        print(f"📋 Missing: Email subject and content")
                        
                        # Test providing the missing information
                        print(f"\n🔄 Providing missing parameters...")
                        follow_up_data = {
                            "message": 'Subject: "Test Automation System" and message: "Hello! This is a test of our new automation system. It successfully detected your email address and is now creating a workflow!"'
                        }
                        
                        async with session.post(f"{BASE_URL}/api/ai/chat/{agent_id}", json=follow_up_data, headers=headers) as resp2:
                            if resp2.status == 200:
                                result2 = await resp2.json()
                                response2 = result2.get('message', 'No response')
                                
                                print(f"🤖 Follow-up Response:")
                                print(f"{response2}")
                                
                                if "automation created successfully" in response2.lower():
                                    print(f"\n🎉 SUCCESS! Complete email automation created!")
                                    print(f"📧 Recipient: slakshanand1105@gmail.com")
                                    print(f"📝 Subject: Test Automation System") 
                                    print(f"✉️ Workflow: Ready to execute")
                                else:
                                    print(f"\n⚠️ Automation may need more information")
                            else:
                                print(f"❌ Follow-up failed: {resp2.status}")
                    
                else:
                    error_text = await resp.text()
                    print(f"❌ Error: {resp.status} - {error_text}")
                    
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_real_email_request())
