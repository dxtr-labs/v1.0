#!/usr/bin/env python3
"""
Test the fixed intent analysis for sales pitch requests
"""

import sys
import os
import asyncio
import logging

# Add backend directory to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_path)

# Import the MCP LLM system
from backend.mcp.simple_mcp_llm import MCP_LLM_Orchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_intent_analysis():
    """Test the fixed intent analysis for sales pitch requests"""
    
    logger.info("🧪 Testing Fixed Intent Analysis")
    logger.info("=" * 50)
    
    # Initialize MCP LLM system
    mcp_llm = MCP_LLM_Orchestrator()
    logger.info("🤖 MCP LLM system initialized")
    
    # Test cases that should trigger AI content generation
    test_cases = [
        "raft a sales pitch to sell better torch lights using AI and send email to slakshanand1105@gmail.com",
        "draft sales pitch for our new product and email to test@example.com",
        "generate marketing email for torch lights and send to customer@example.com",
        "create a pitch to sell laptops using AI and send to buyer@example.com",
        "write sales email for our services and send to prospect@example.com"
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n🔍 Test Case #{i}")
        logger.info(f"   Input: {test_case}")
        
        try:
            # Analyze intent
            intent_analysis = mcp_llm.analyze_user_intent(test_case)
            
            logger.info(f"   📊 Intent Analysis:")
            logger.info(f"      Primary Intent: {intent_analysis['primary_intent']}")
            logger.info(f"      Confidence: {intent_analysis['confidence']:.0%}")
            logger.info(f"      Requires AI Service: {intent_analysis['requires_ai_service']}")
            logger.info(f"      Extracted Emails: {intent_analysis['extracted_emails']}")
            
            # Process through full MCP LLM
            result = await mcp_llm.process_user_input(
                user_id="test_user",
                agent_id="test_agent",
                user_message=test_case
            )
            
            logger.info(f"   🎯 MCP Result:")
            logger.info(f"      Status: {result.get('status', 'unknown')}")
            logger.info(f"      Message: {result.get('message', result.get('response', 'No message'))[:100]}...")
            
            # Check if it's working correctly
            if intent_analysis['requires_ai_service']:
                logger.info(f"   ✅ CORRECT: Detected need for AI service")
            else:
                logger.warning(f"   ❌ ISSUE: Should have detected AI service need")
                
        except Exception as e:
            logger.error(f"   ❌ Error: {e}")
    
    logger.info("=" * 50)
    logger.info("🏁 Intent Analysis Test Complete")

if __name__ == "__main__":
    asyncio.run(test_intent_analysis())
