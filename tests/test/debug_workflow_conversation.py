"""
Debug the conversation workflow to see exact responses
"""
import asyncio
import aiohttp
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_conversation():
    """Debug the conversation flow step by step"""
    
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
                
                # Test simple message
                user_message = "draft a sales pitch to sell better torch lights using AI and send email to slakshanand1105@gmail.com"
                
                chat_request = {
                    "message": user_message,
                    "agentId": "debug-agent",
                    "agentConfig": {
                        "name": "Debug Assistant",
                        "role": "Sales Assistant",
                        "personality": {"tone": "professional"},
                        "llm_config": {"model": "inhouse"}
                    }
                }
                
                logger.info(f"🔍 Sending message: {user_message}")
                
                async with session.post(f"{backend_url}/api/chat/mcpai", json=chat_request, headers=headers) as chat_response:
                    if chat_response.status == 200:
                        result = await chat_response.json()
                        
                        logger.info("🔍 FULL RESPONSE DEBUG:")
                        logger.info("=" * 60)
                        logger.info(f"Status: {result.get('status')}")
                        logger.info(f"Message: {result.get('message')}")
                        logger.info(f"Response: {result.get('response')}")
                        logger.info(f"Workflow JSON: {result.get('workflow_json')}")
                        logger.info(f"AI Service: {result.get('ai_service')}")
                        logger.info(f"Next Step: {result.get('next_step')}")
                        logger.info("=" * 60)
                        
                        # Show full JSON for debugging
                        logger.info("COMPLETE JSON RESPONSE:")
                        logger.info(json.dumps(result, indent=2))
                        
                        return result
                    else:
                        error = await chat_response.text()
                        logger.error(f"❌ Chat request failed: {chat_response.status} - {error}")
                        return None
            else:
                error = await response.text()
                logger.error(f"❌ User creation failed: {response.status} - {error}")
                return None

if __name__ == "__main__":
    asyncio.run(debug_conversation())
