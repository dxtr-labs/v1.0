#!/usr/bin/env python3
"""
Debug the exact response structure being returned
"""

import asyncio
import sys
import os
import json

from mcp.simple_mcp_llm import MCP_LLM_Orchestrator

async def debug_response_structure():
    """Test the exact response structure for debugging"""
    
    print("=== Debugging Response Structure ===\n")
    
    mcp = MCP_LLM_Orchestrator()
    
    # Test the exact message that's failing
    message = "service:inhouse Using AI generate a sales pitch to sell healthy mango ice cream and send email to slakshanand1105@gmail.com"
    
    print(f"Testing message: {message}")
    response = await mcp.process_user_input("user123", "agent456", message)
    
    print(f"\nResponse status: {response.get('status')}")
    print(f"Response keys: {list(response.keys())}")
    
    # Check if workflow_preview exists
    if 'workflow_preview' in response:
        print(f"\nworkflow_preview exists: {response['workflow_preview'] is not None}")
        print(f"workflow_preview keys: {list(response['workflow_preview'].keys()) if response['workflow_preview'] else 'None'}")
    else:
        print("\n❌ workflow_preview field is MISSING!")
    
    # Print full response structure
    print(f"\nFull response structure:")
    print(json.dumps(response, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(debug_response_structure())
