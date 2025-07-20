import asyncio
import aiohttp
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_calendar_integration():
    """Test comprehensive calendar integration OAuth system"""
    
    # Backend URL
    BASE_URL = "http://localhost:8002"
    
    async with aiohttp.ClientSession() as session:
        try:
            # Test MCP chat endpoint with calendar integration request
            chat_data = {
                "message": "email all potential ai investors explaining our product and send various timings in calendly"
            }
            
            logger.info("🧪 Testing calendar integration automation...")
            
            async with session.post(f"{BASE_URL}/api/chat/mcpai", json=chat_data) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info("✅ Calendar integration test successful!")
                    logger.info(f"📄 Response status: {result.get('status', 'N/A')}")
                    logger.info(f"📄 Response message: {result.get('response', 'N/A')[:100]}...")
                    
                    # Check if OAuth URLs are provided
                    workflow_preview = result.get('workflow_preview', {})
                    calendar_services = workflow_preview.get('calendar_services', [])
                    
                    if calendar_services:
                        logger.info("🎯 Calendar Services Available:")
                        for service in calendar_services:
                            logger.info(f"   📅 {service['name']}: {service['oauth_url'][:50]}...")
                    
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Calendar integration test failed: {response.status}")
                    logger.error(f"Error: {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Test error: {e}")
            return False

async def test_oauth_endpoints():
    """Test OAuth authorization endpoints"""
    
    BASE_URL = "http://localhost:8002"
    
    async with aiohttp.ClientSession() as session:
        try:
            # Test Google Calendar OAuth endpoint
            logger.info("🧪 Testing Google Calendar OAuth endpoint...")
            async with session.get(f"{BASE_URL}/api/oauth/google-calendar/authorize") as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info("✅ Google Calendar OAuth endpoint working!")
                    logger.info(f"OAuth URL: {result.get('oauth_url', 'N/A')[:50]}...")
                else:
                    logger.error(f"❌ Google Calendar OAuth failed: {response.status}")
            
            # Test Calendly OAuth endpoint
            logger.info("🧪 Testing Calendly OAuth endpoint...")
            async with session.get(f"{BASE_URL}/api/oauth/calendly/authorize") as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info("✅ Calendly OAuth endpoint working!")
                    logger.info(f"OAuth URL: {result.get('oauth_url', 'N/A')[:50]}...")
                else:
                    logger.error(f"❌ Calendly OAuth failed: {response.status}")
            
            # Test Outlook OAuth endpoint
            logger.info("🧪 Testing Outlook OAuth endpoint...")
            async with session.get(f"{BASE_URL}/api/oauth/outlook/authorize") as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info("✅ Outlook OAuth endpoint working!")
                    logger.info(f"OAuth URL: {result.get('oauth_url', 'N/A')[:50]}...")
                else:
                    logger.error(f"❌ Outlook OAuth failed: {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ OAuth endpoint test error: {e}")

async def main():
    """Run all calendar integration tests"""
    logger.info("🚀 Starting Calendar OAuth Integration Tests...")
    
    # Test calendar integration flow
    await test_calendar_integration()
    
    # Test OAuth endpoints
    await test_oauth_endpoints()
    
    logger.info("✅ All calendar integration tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
