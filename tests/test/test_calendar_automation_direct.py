"""
🧪 Direct Calendar Integration Test
Tests calendar automation detection without OAuth dependencies
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.mcp.custom_mcp_llm_iteration import CustomMCPLLMIterationEngine
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_calendar_automation_detection():
    """Test calendar automation detection logic directly"""
    
    logger.info("🧪 Testing calendar automation detection...")
    
    # Create MCP engine instance
    engine = CustomMCPLLMIterationEngine(
        agent_id="test_calendar_agent",
        agent_context={"memory": {}},
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        session_id="test_session"
    )
    
    # Test various calendar-related messages
    test_messages = [
        "email all potential ai investors explaining our product and send various timings in calendly",
        "connect with google calendar and schedule meeting",
        "setup outlook oauth integration for scheduling",
        "integrate calendly for booking meetings",
        "send calendar availability to investors",
        "normal conversation about weather"  # This should NOT trigger calendar automation
    ]
    
    for message in test_messages:
        logger.info(f"\n📝 Testing message: '{message}'")
        
        try:
            # Test the detection logic
            user_lower = message.lower()
            
            # Calendar automation detection (copied from MCP engine)
            has_calendar_request = any(word in user_lower for word in ['calendar', 'google calendar', 'outlook', 'calendly', 'scheduling'])
            has_calendar_action = any(word in user_lower for word in ['connect', 'integrate', 'oauth', 'authorize', 'link', 'setup', 'send'])
            
            is_calendar_automation = has_calendar_request and has_calendar_action
            
            logger.info(f"   📅 Calendar request detected: {has_calendar_request}")
            logger.info(f"   🔧 Calendar action detected: {has_calendar_action}")
            logger.info(f"   🎯 Calendar automation triggered: {is_calendar_automation}")
            
            if is_calendar_automation:
                logger.info("   ✅ Would trigger calendar OAuth workflow!")
            else:
                logger.info("   💬 Would be treated as normal conversation")
                
        except Exception as e:
            logger.error(f"❌ Error testing message: {e}")
    
    logger.info("\n✅ Calendar automation detection test completed!")

async def test_calendar_service_availability():
    """Test if calendar services are properly imported"""
    
    logger.info("🧪 Testing calendar service availability...")
    
    try:
        # Test Google Calendar service
        try:
            from backend.services.google_calendar_service import GoogleCalendarService
            google_service = GoogleCalendarService()
            logger.info("✅ Google Calendar service imported successfully")
        except Exception as e:
            logger.error(f"❌ Google Calendar service error: {e}")
        
        # Test Calendly service
        try:
            from backend.services.calendly_service import CalendlyService
            calendly_service = CalendlyService()
            logger.info("✅ Calendly service imported successfully")
        except Exception as e:
            logger.error(f"❌ Calendly service error: {e}")
        
        # Test Outlook service
        try:
            from backend.services.outlook_service import OutlookService
            outlook_service = OutlookService()
            logger.info("✅ Outlook service imported successfully")
        except Exception as e:
            logger.error(f"❌ Outlook service error: {e}")
            
    except Exception as e:
        logger.error(f"❌ Service availability test error: {e}")

async def main():
    """Run all calendar automation tests"""
    logger.info("🚀 Starting Direct Calendar Automation Tests...")
    
    await test_calendar_automation_detection()
    await test_calendar_service_availability()
    
    logger.info("✅ All calendar automation tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
