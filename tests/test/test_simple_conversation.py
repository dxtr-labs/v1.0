"""
Test with simple conversational message
"""
import asyncio
import aiohttp
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_simple_conversation():
    """Test with a simple, non-automation message"""
    
    backend_url = "http://localhost:8002"
    
    async with aiohttp.ClientSession() as session:
        # Create test user
        register_data = {
            "email": f"simple_{int(asyncio.get_event_loop().time())}@example.com",
            "password": "testpassword123",
            "firstName": "Simple",
            "lastName": "User",
            "username": f"simpleuser{int(asyncio.get_event_loop().time())}"
        }
        
        async with session.post(f"{backend_url}/api/auth/signup", json=register_data) as response:
            if response.status in [200, 201]:
                result = await response.json()
                session_token = result.get("session_token")
                headers = {"Cookie": f"session_token={session_token}"}
                
                # Test simple conversational message
                user_message = "Hello! How are you today?"
                
                chat_request = {
                    "message": user_message,
                    "agentId": "simple-agent",
                    "agentConfig": {
                        "name": "Friendly Assistant",
                        "role": "Conversational Assistant",
                        "personality": {"tone": "friendly"},
                        "llm_config": {"model": "inhouse"}
                    }
                }
                
                logger.info(f"🔍 Testing simple message: {user_message}")
                
                async with session.post(f"{backend_url}/api/chat/mcpai", json=chat_request, headers=headers) as chat_response:
                    if chat_response.status == 200:
                        result = await chat_response.json()
                        
                        logger.info("🔍 SIMPLE CONVERSATION TEST:")
                        logger.info("=" * 60)
                        logger.info(f"Status: {result.get('status')}")
                        logger.info(f"Message: {result.get('message')}")
                        logger.info(f"Response: {result.get('response')}")
                        logger.info("=" * 60)
                        
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
    asyncio.run(test_simple_conversation())
