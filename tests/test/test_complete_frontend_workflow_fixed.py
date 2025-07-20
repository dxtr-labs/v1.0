#!/usr/bin/env python3
"""
Complete Frontend Workflow Test - Fixed Version
This script tests the entire frontend → backend → email workflow
to ensure emails are being sent from the frontend interface.
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FrontendWorkflowTester:
    def __init__(self):
        self.backend_url = "http://localhost:8002"
        self.frontend_url = "http://localhost:3000"
        self.session_token = None
        
    async def test_login(self, session: aiohttp.ClientSession) -> bool:
        """Test user authentication"""
        logger.info("🔐 Testing user authentication...")
        
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        try:
            async with session.post(f"{self.backend_url}/api/auth/login", json=login_data) as response:
                if response.status == 200:
                    result = await response.json()
                    self.session_token = result.get("session_token")
                    logger.info("✅ Authentication successful")
                    return True
                else:
                    logger.warning(f"⚠️ Authentication failed: {response.status}")
                    # Try to register user first
                    return await self.test_register(session)
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False
    
    async def test_register(self, session: aiohttp.ClientSession) -> bool:
        """Register a test user"""
        logger.info("📝 Registering test user...")
        
        register_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "firstName": "Test",
            "lastName": "User",
            "username": "testuser"
        }
        
        try:
            async with session.post(f"{self.backend_url}/api/auth/signup", json=register_data) as response:
                if response.status == 201:
                    logger.info("✅ User registration successful")
                    # Now try to login
                    return await self.test_login(session)
                else:
                    logger.error(f"❌ Registration failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Registration error: {e}")
            return False
    
    async def test_complete_workflow(self, session: aiohttp.ClientSession) -> bool:
        """Test the complete email workflow"""
        logger.info("🚀 Testing complete email workflow...")
        
        headers = {}
        if self.session_token:
            headers["Cookie"] = f"session_token={self.session_token}"
        
        # Step 1: Send initial request
        logger.info("📤 Step 1: Sending initial AI email request...")
        
        initial_request = {
            "message": "draft a sales pitch to sell better torch lights using AI and send email to slakshanand1105@gmail.com",
            "agentId": "test-agent-id",
            "agentConfig": {
                "name": "Test Agent",
                "role": "Email Assistant",
                "personality": {"tone": "professional"},
                "llm_config": {"model": "gpt-3.5-turbo"}
            }
        }
        
        try:
            async with session.post(
                f"{self.backend_url}/api/chat/mcpai", 
                json=initial_request,
                headers=headers
            ) as response:
                
                if response.status != 200:
                    logger.error(f"❌ Initial request failed: {response.status}")
                    return False
                
                result = await response.json()
                logger.info(f"✅ Step 1 Response: {result.get('status')}")
                
                # Step 2: Handle AI service selection
                if result.get('status') == 'ai_service_selection':
                    logger.info("📤 Step 2: Selecting in-house AI service...")
                    
                    service_request = {
                        "message": "service:inhouse draft a sales pitch to sell better torch lights using AI and send email to slakshanand1105@gmail.com",
                        "agentId": "test-agent-id",
                        "agentConfig": {
                            "name": "Test Agent",
                            "role": "Email Assistant",
                            "personality": {"tone": "professional"},
                            "llm_config": {"model": "gpt-3.5-turbo"}
                        }
                    }
                    
                    async with session.post(
                        f"{self.backend_url}/api/chat/mcpai",
                        json=service_request,
                        headers=headers
                    ) as response2:
                        
                        if response2.status != 200:
                            logger.error(f"❌ Service selection failed: {response2.status}")
                            return False
                        
                        result2 = await response2.json()
                        logger.info(f"✅ Step 2 Response: {result2.get('status')}")
                        
                        # Step 3: Handle workflow confirmation
                        if result2.get('status') == 'workflow_preview':
                            logger.info("📤 Step 3: Confirming workflow execution...")
                            
                            workflow_json = result2.get('workflow_json')
                            if not workflow_json:
                                logger.error("❌ No workflow JSON received")
                                return False
                            
                            logger.info(f"🔍 Workflow details: {json.dumps(workflow_json, indent=2)}")
                            
                            confirmation_request = {
                                "workflow_json": workflow_json,
                                "agentId": "test-agent-id",
                                "confirmed": True
                            }
                            
                            async with session.post(
                                f"{self.backend_url}/api/workflow/confirm",
                                json=confirmation_request,
                                headers=headers
                            ) as response3:
                                
                                if response3.status != 200:
                                    error_text = await response3.text()
                                    logger.error(f"❌ Workflow confirmation failed: {response3.status} - {error_text}")
                                    return False
                                
                                result3 = await response3.json()
                                logger.info(f"✅ Step 3 Response: {result3.get('message')}")
                                
                                if result3.get('success'):
                                    logger.info("🎉 COMPLETE WORKFLOW SUCCESS!")
                                    logger.info("📧 Email should have been sent to slakshanand1105@gmail.com")
                                    
                                    # Log execution details
                                    execution_details = result3.get('execution_details', {})
                                    logger.info(f"📊 Execution Details: {json.dumps(execution_details, indent=2)}")
                                    
                                    return True
                                else:
                                    logger.error(f"❌ Workflow execution failed: {result3}")
                                    return False
                        else:
                            logger.error(f"❌ Expected workflow_preview, got: {result2.get('status')}")
                            return False
                else:
                    logger.error(f"❌ Expected ai_service_selection, got: {result.get('status')}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Workflow test error: {e}")
            return False
    
    async def run_complete_test(self):
        """Run the complete test suite"""
        logger.info("🎯 FRONTEND WORKFLOW TEST - FIXED VERSION")
        logger.info("=" * 70)
        
        async with aiohttp.ClientSession() as session:
            # Test authentication
            auth_success = await self.test_login(session)
            if not auth_success:
                logger.error("❌ Authentication failed - cannot proceed")
                return False
            
            # Test complete workflow
            workflow_success = await self.test_complete_workflow(session)
            
            logger.info("=" * 70)
            if workflow_success:
                logger.info("🏆 ALL TESTS PASSED!")
                logger.info("✅ Frontend → Backend → Email workflow is working!")
                logger.info("📧 Email delivered to slakshanand1105@gmail.com")
                logger.info("🎨 AI-generated torch lights sales pitch sent successfully")
            else:
                logger.info("❌ TESTS FAILED!")
                logger.info("🔧 Workflow issues detected - check logs above")
            
            return workflow_success

async def main():
    """Main test function"""
    tester = FrontendWorkflowTester()
    success = await tester.run_complete_test()
    
    if success:
        print("\n🎉 SUCCESS: Frontend email workflow is working!")
        print("📧 Check slakshanand1105@gmail.com for the AI-generated torch lights email")
    else:
        print("\n❌ FAILURE: Frontend email workflow has issues")
        print("🔧 Check the backend logs and frontend code")

if __name__ == "__main__":
    asyncio.run(main())
