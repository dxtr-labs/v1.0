#!/usr/bin/env python3
"""
Test intent analysis for debugging
"""

import asyncio
import sys
import os

from mcp.simple_mcp_llm import MCP_LLM_Orchestrator

async def test_intent_analysis():
    """Test intent analysis for problematic messages"""
    
    print("=== Testing Intent Analysis ===\n")
    
    mcp = MCP_LLM_Orchestrator()
    
    test_messages = [
        "generate content using AI service:claude",
        "write email using AI to test@example.com about project update",
        "using AI generate content",
        "create content with AI"
    ]
    
    for msg in test_messages:
        print(f"Message: '{msg}'")
        intent = mcp.analyze_user_intent(msg)
        print(f"   Primary intent: {intent['primary_intent']}")
        print(f"   Requires AI service: {intent['requires_ai_service']}")
        print(f"   Confidence: {intent['confidence']}")
        print()

if __name__ == "__main__":
    asyncio.run(test_intent_analysis())
