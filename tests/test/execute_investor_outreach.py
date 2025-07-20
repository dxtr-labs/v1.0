#!/usr/bin/env python3
"""
Execute investor outreach automation for Sam
"""

import asyncio
import aiohttp
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def execute_investor_outreach():
    """Execute investor outreach with calendar integration"""
    
    # Backend URL
    BASE_URL = "http://localhost:8002"
    
    # Prepare the investor outreach message
    message = """email all potential ai investors explaining our product and send various timings in calendly and ask for scheduling meeting with these details:

Investor emails: john.doe@a16z.com, priya.kapoor@sequoiacap.com, mike.harrison@greylock.com, investors@lightspeedvp.com

Product Details: DXTR Labs is building always-available AI e-workers (DXT Agents) that replace repetitive human tasks. Unlike other automation tools, DXT Agents have memory, personality, and work continuously 24/7—users simply chat or speak to assign tasks. We've already integrated 2000+ automation workflows and are working with early B2B clients saving 40+ hours of manual work per day.

Available Time Slots:
- Monday, July 22 – 10:00 AM to 12:00 PM PT
- Tuesday, July 23 – 3:00 PM to 5:00 PM PT  
- Thursday, July 25 – 1:00 PM to 3:00 PM PT

Calendly link: https://calendly.com/dxtrlabs/30min

Send professional investor outreach emails to all investors immediately."""
    
    async with aiohttp.ClientSession() as session:
        try:
            logger.info("🚀 Executing investor outreach automation...")
            
            # Send request to MCP AI chat endpoint
            chat_data = {"message": message}
            
            async with session.post(f"{BASE_URL}/api/chat/mcpai", json=chat_data) as response:
                logger.info(f"📡 Response status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    logger.info("✅ Investor outreach automation executed!")
                    
                    # Log key response details
                    logger.info(f"📄 Response: {result.get('response', 'N/A')[:200]}...")
                    logger.info(f"📊 Status: {result.get('status', 'N/A')}")
                    
                    # Check for workflow preview
                    if 'workflow_preview' in result:
                        workflow = result['workflow_preview']
                        logger.info(f"📋 Workflow: {workflow.get('title', 'N/A')}")
                        
                        # Check for calendar services
                        if 'calendar_services' in workflow:
                            services = workflow['calendar_services']
                            logger.info(f"📅 Calendar services available: {len(services)}")
                            for service in services:
                                logger.info(f"   - {service.get('name', 'N/A')}")
                    
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Request failed: {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error executing investor outreach: {e}")
            return None

async def main():
    """Main execution"""
    logger.info("🎯 DXTR Labs Investor Outreach Automation")
    logger.info("📧 Targeting 4 AI investors with Calendly scheduling")
    
    result = await execute_investor_outreach()
    
    if result:
        logger.info("✅ Investor outreach automation completed successfully!")
    else:
        logger.error("❌ Investor outreach automation failed")

if __name__ == "__main__":
    asyncio.run(main())
