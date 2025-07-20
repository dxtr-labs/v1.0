#!/usr/bin/env python3
"""
Direct MCP Workflow Test - No Authentication
This script directly tests the MCP workflow execution
to verify the email sending functionality is working.
"""

import asyncio
import aiohttp
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_direct_mcp_workflow():
    """Test MCP workflow directly without authentication"""
    logger.info("🎯 DIRECT MCP WORKFLOW TEST")
    logger.info("=" * 60)
    
    backend_url = "http://localhost:8002"
    
    async with aiohttp.ClientSession() as session:
        try:
            # Test 1: Initial request for AI service selection
            logger.info("📤 Step 1: Testing initial MCP request...")
            
            initial_request = {
                "user_id": "test_user",
                "agent_id": "test_agent", 
                "user_message": "draft a sales pitch to sell better torch lights using AI and send email to slakshanand1105@gmail.com"
            }
            
            async with session.post(f"{backend_url}/api/chat/mcpai/direct", json=initial_request) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Step 1 Success: {result.get('status')}")
                    
                    if result.get('status') == 'ai_service_selection':
                        logger.info("📤 Step 2: Selecting in-house AI service...")
                        
                        # Test 2: AI service selection
                        service_request = {
                            "user_id": "test_user",
                            "agent_id": "test_agent",
                            "user_message": "service:inhouse draft a sales pitch to sell better torch lights using AI and send email to slakshanand1105@gmail.com"
                        }
                        
                        async with session.post(f"{backend_url}/api/chat/mcpai/direct", json=service_request) as response2:
                            if response2.status == 200:
                                result2 = await response2.json()
                                logger.info(f"✅ Step 2 Success: {result2.get('status')}")
                                
                                if result2.get('status') == 'workflow_preview':
                                    workflow_json = result2.get('workflow_json')
                                    logger.info(f"📊 Workflow JSON received: {json.dumps(workflow_json, indent=2)}")
                                    
                                    # Test 3: Direct workflow execution
                                    logger.info("📤 Step 3: Executing workflow directly...")
                                    
                                    execution_request = {
                                        "workflow_json": workflow_json,
                                        "confirmed": True
                                    }
                                    
                                    async with session.post(f"{backend_url}/api/workflow/confirm/direct", json=execution_request) as response3:
                                        if response3.status == 200:
                                            result3 = await response3.json()
                                            logger.info("🎉 WORKFLOW EXECUTION SUCCESS!")
                                            logger.info(f"📧 Result: {result3.get('message')}")
                                            logger.info(f"📊 Details: {json.dumps(result3.get('execution_details', {}), indent=2)}")
                                            return True
                                        else:
                                            error_text = await response3.text()
                                            logger.error(f"❌ Step 3 Failed: {response3.status} - {error_text}")
                                else:
                                    logger.error(f"❌ Expected workflow_preview, got: {result2.get('status')}")
                            else:
                                error_text = await response2.text()
                                logger.error(f"❌ Step 2 Failed: {response2.status} - {error_text}")
                    else:
                        logger.error(f"❌ Expected ai_service_selection, got: {result.get('status')}")
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Step 1 Failed: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ Test error: {e}")
            return False
    
    return False

async def main():
    """Run the direct test"""
    success = await test_direct_mcp_workflow()
    
    logger.info("=" * 60)
    if success:
        logger.info("🏆 SUCCESS: MCP workflow execution is working!")
        logger.info("📧 Email should have been sent to slakshanand1105@gmail.com")
    else:
        logger.info("❌ FAILURE: MCP workflow execution has issues")
        logger.info("🔧 Check the backend implementation")

if __name__ == "__main__":
    asyncio.run(main())
