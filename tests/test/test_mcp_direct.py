#!/usr/bin/env python3
"""
Direct test of the web search integration in the MCP engine
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from backend.mcp.custom_mcp_llm_iteration import CustomMCPLLMIterationEngine

async def test_mcp_web_search():
    """Test the MCP engine web search directly"""
    print("🚀 Testing MCP Web Search Integration")
    
    try:
        # Create MCP engine instance
        engine = CustomMCPLLMIterationEngine()
        print("✅ MCP engine created")
        
        # Test web search request
        test_request = "find top 10 ai investors email from web and send that list to slakshanand1105@gmail.com"
        print(f"📝 Testing request: {test_request}")
        
        # Process the request
        response = await engine.process_request(
            original_request=test_request,
            chat_session=None,
            service_type="inhouse"
        )
        
        print("✅ Request processed successfully!")
        print(f"📋 Response type: {type(response)}")
        print(f"📋 Response: {response}")
        
        # Check if it's a workflow preview
        if isinstance(response, dict) and response.get("hasWorkflowPreview"):
            print("🎯 ✅ Web search workflow preview generated!")
            workflow = response.get("workflow_preview", {})
            email_preview = workflow.get("email_preview", {})
            search_count = email_preview.get("search_results_count", 0)
            print(f"🔍 Search results found: {search_count}")
            print("🎉 WEB SEARCH INTEGRATION IS WORKING!")
        else:
            print("⚠️ Response doesn't contain workflow preview - might not be web search")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_web_search())
