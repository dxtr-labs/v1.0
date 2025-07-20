"""
Debug the exact workflow logic step by step
"""
import asyncio
import aiohttp
import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def debug_workflow_step_by_step():
    """Debug each step of the workflow logic"""
    
    backend_url = "http://localhost:8002"
    
    async with aiohttp.ClientSession() as session:
        # Create test user
        register_data = {
            "email": f"debug_{int(asyncio.get_event_loop().time())}@example.com",
            "password": "testpassword123",
            "firstName": "Debug",
            "lastName": "User",
            "username": f"debuguser{int(asyncio.get_event_loop().time())}"
        }
        
        async with session.post(f"{backend_url}/api/auth/signup", json=register_data) as response:
            if response.status in [200, 201]:
                result = await response.json()
                session_token = result.get("session_token")
                headers = {"Cookie": f"session_token={session_token}"}
                
                # Step 1: Send automation request and check exact response
                user_message = "draft email to test@example.com"
                
                chat_request = {
                    "message": user_message,
                    "agentId": "debug-agent",
                    "agentConfig": {
                        "name": "Debug Assistant",
                        "role": "Debug Assistant",
                        "personality": {"tone": "helpful"},
                        "llm_config": {"model": "inhouse"}
                    }
                }
                
                logger.info(f"🔍 Sending automation request: {user_message}")
                
                async with session.post(f"{backend_url}/api/chat/mcpai", json=chat_request, headers=headers) as chat_response:
                    if chat_response.status == 200:
                        result = await chat_response.json()
                        
                        logger.info("🔍 STEP 1 - AUTOMATION REQUEST:")
                        logger.info("=" * 60)
                        logger.info(f"Raw response: {json.dumps(result, indent=2)}")
                        logger.info("=" * 60)
                        
                        # Check if status is ai_service_selection
                        if result.get('status') == 'ai_service_selection':
                            logger.info("✅ Step 1 SUCCESS: Got ai_service_selection status")
                            
                            # Step 2: Send service selection
                            service_message = "service:inhouse"
                            
                            service_request = {
                                "message": service_message,
                                "agentId": "debug-agent",
                                "agentConfig": chat_request["agentConfig"]
                            }
                            
                            logger.info(f"🔍 Sending service selection: {service_message}")
                            
                            async with session.post(f"{backend_url}/api/chat/mcpai", json=service_request, headers=headers) as service_response:
                                if service_response.status == 200:
                                    result2 = await service_response.json()
                                    
                                    logger.info("🔍 STEP 2 - SERVICE SELECTION:")
                                    logger.info("=" * 60)
                                    logger.info(f"Status: {result2.get('status')}")
                                    logger.info(f"Has Workflow JSON: {result2.get('hasWorkflowJson')}")
                                    logger.info(f"Workflow JSON: {result2.get('workflow_json')}")
                                    logger.info("=" * 60)
                                    
                                    if result2.get('status') == 'workflow_preview':
                                        logger.info("✅ Step 2 SUCCESS: Got workflow_preview status")
                                        return True
                                    else:
                                        logger.error(f"❌ Step 2 FAILED: Expected workflow_preview, got {result2.get('status')}")
                                        return False
                        else:
                            logger.error(f"❌ Step 1 FAILED: Expected ai_service_selection, got {result.get('status')}")
                            logger.error(f"Message: {result.get('message')}")
                            return False
                    else:
                        error = await chat_response.text()
                        logger.error(f"❌ Chat request failed: {chat_response.status} - {error}")
                        return False
            else:
                error = await response.text()
                logger.error(f"❌ User creation failed: {response.status} - {error}")
                return False

if __name__ == "__main__":
    asyncio.run(debug_workflow_step_by_step())
