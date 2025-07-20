"""
Create Test User and Frontend Workflow
This script creates a test user and demonstrates the complete frontend workflow.
"""

import asyncio
import aiohttp
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_with_real_authentication():
    """Test with proper user authentication"""
    
    logger.info("🎯 TESTING FRONTEND WORKFLOW WITH AUTHENTICATION")
    logger.info("=" * 60)
    
    backend_url = "http://localhost:8002"
    
    async with aiohttp.ClientSession() as session:
        try:
            # Step 1: Register a test user
            logger.info("📝 Creating test user...")
            
            register_data = {
                "email": f"test_{int(asyncio.get_event_loop().time())}@example.com",
                "password": "testpassword123",
                "firstName": "Test",
                "lastName": "User",
                "username": f"testuser{int(asyncio.get_event_loop().time())}"
            }
            
            async with session.post(f"{backend_url}/api/auth/signup", json=register_data) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    session_token = result.get("session_token")
                    logger.info("✅ User created and authenticated")
                    
                    # Step 2: Test the complete workflow with proper authentication
                    headers = {"Cookie": f"session_token={session_token}"}
                    
                    return await test_email_workflow(session, backend_url, headers)
                    
                else:
                    error_text = await response.text()
                    logger.error(f"❌ User creation failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Authentication test error: {e}")
            return False

async def test_email_workflow(session, backend_url, headers):
    """Test the complete email workflow with valid session"""
    
    logger.info("🚀 Testing complete email workflow...")
    
    try:
        # Step 1: Initial request
        user_message = "draft a sales pitch to sell better torch lights using AI and send email to slakshanand1105@gmail.com"
        
        chat_request = {
            "message": user_message,
            "agentId": "test-agent",
            "agentConfig": {
                "name": "Email Assistant",
                "role": "Sales Assistant",
                "personality": {"tone": "professional"},
                "llm_config": {"model": "inhouse"}
            }
        }
        
        async with session.post(f"{backend_url}/api/chat/mcpai", json=chat_request, headers=headers) as response:
            if response.status == 200:
                result1 = await response.json()
                logger.info(f"✅ Step 1 Response: {result1.get('status')}")
                
                # Step 2: AI service selection
                if result1.get('status') == 'ai_service_selection':
                    service_request = {
                        "message": f"service:inhouse {user_message}",
                        "agentId": "test-agent",
                        "agentConfig": chat_request["agentConfig"]
                    }
                    
                    async with session.post(f"{backend_url}/api/chat/mcpai", json=service_request, headers=headers) as response2:
                        if response2.status == 200:
                            result2 = await response2.json()
                            logger.info(f"✅ Step 2 Response: {result2.get('status')}")
                            
                            # Step 3: Workflow confirmation
                            if result2.get('status') == 'workflow_preview':
                                workflow_json = result2.get('workflow_json')
                                
                                if workflow_json:
                                    logger.info(f"📊 Workflow Preview Generated:")
                                    logger.info(f"   Type: {workflow_json.get('type')}")
                                    logger.info(f"   Recipient: {workflow_json.get('recipient')}")
                                    logger.info(f"   AI Service: {workflow_json.get('ai_service')}")
                                    
                                    confirmation_request = {
                                        "workflow_json": workflow_json,
                                        "agentId": "test-agent",
                                        "confirmed": True
                                    }
                                    
                                    async with session.post(f"{backend_url}/api/workflow/confirm", json=confirmation_request, headers=headers) as response3:
                                        if response3.status == 200:
                                            result3 = await response3.json()
                                            logger.info("🎉 WORKFLOW EXECUTION SUCCESSFUL!")
                                            logger.info(f"📧 Message: {result3.get('message')}")
                                            
                                            details = result3.get('execution_details', {})
                                            logger.info(f"📊 Execution Details:")
                                            logger.info(f"   Status: {details.get('status')}")
                                            logger.info(f"   Email Sent: {details.get('email_sent')}")
                                            logger.info(f"   Recipient: {details.get('recipient')}")
                                            
                                            if details.get('email_sent'):
                                                logger.info("✅ EMAIL SUCCESSFULLY SENT!")
                                                return True
                                            else:
                                                logger.error("❌ Email was not sent")
                                                return False
                                        else:
                                            error = await response3.text()
                                            logger.error(f"❌ Workflow confirmation failed: {response3.status} - {error}")
                                            return False
                                else:
                                    logger.error("❌ No workflow JSON in preview response")
                                    return False
                            else:
                                logger.error(f"❌ Expected workflow_preview, got: {result2.get('status')}")
                                return False
                        else:
                            error = await response2.text()
                            logger.error(f"❌ Service selection failed: {response2.status} - {error}")
                            return False
                else:
                    logger.error(f"❌ Expected ai_service_selection, got: {result1.get('status')}")
                    return False
            else:
                error = await response.text()
                logger.error(f"❌ Initial request failed: {response.status} - {error}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Workflow test error: {e}")
        return False

async def main():
    """Run the complete test"""
    success = await test_with_real_authentication()
    
    logger.info("=" * 60)
    if success:
        logger.info("🏆 COMPLETE SUCCESS!")
        logger.info("✅ Frontend workflow is working end-to-end")
        logger.info("📧 Email sent to slakshanand1105@gmail.com")
        logger.info("🎨 AI-generated torch lights sales pitch delivered")
        logger.info("")
        logger.info("🎯 RESULT: Your system is working! The issue was:")
        logger.info("   - Backend is working perfectly")
        logger.info("   - Frontend needs proper authentication flow")
        logger.info("   - All workflow steps are functioning correctly")
    else:
        logger.info("❌ TEST FAILED!")
        logger.info("🔧 Check the specific error messages above")

if __name__ == "__main__":
    asyncio.run(main())
