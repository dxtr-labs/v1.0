#!/usr/bin/env python3
"""
Test script to verify web search integration is working
"""
import sys
import os
import asyncio

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_web_search():
    try:
        # Test 1: Import web search service
        print("🔍 Testing web search service import...")
        from backend.services.web_search_service import web_search_service
        print("✅ Web search service imported successfully")
        
        # Test 2: Execute a simple search
        print("🔍 Testing web search execution...")
        search_query = "top 10 AI investors"
        results = await web_search_service.search_comprehensive(search_query)
        print(f"✅ Web search completed: Found {len(results.get('results', [])) if results else 0} results")
        
        # Test 3: Display first few results
        if results and results.get('results'):
            print("\n📋 First 3 search results:")
            for i, result in enumerate(results['results'][:3], 1):
                print(f"{i}. {result.get('title', 'N/A')}")
                print(f"   URL: {result.get('url', 'N/A')}")
                print(f"   Description: {result.get('description', 'N/A')[:100]}...")
                print()
        
        return True
        
    except Exception as e:
        print(f"❌ Web search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_mcp_integration():
    try:
        # Test MCP engine integration
        print("🔍 Testing MCP engine integration...")
        from backend.mcp.custom_mcp_llm_iteration import CustomMCPLLMIterationEngine
        
        # Check if web search service is available in the MCP engine
        engine = CustomMCPLLMIterationEngine()
        print("✅ MCP engine created successfully")
        
        # Check WEB_SEARCH_AVAILABLE flag
        from backend.mcp.custom_mcp_llm_iteration import WEB_SEARCH_AVAILABLE
        print(f"✅ WEB_SEARCH_AVAILABLE flag: {WEB_SEARCH_AVAILABLE}")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("🚀 Starting Web Search Integration Tests\n")
    
    # Test 1: Web search service
    web_search_success = await test_web_search()
    print(f"\n📊 Web Search Service Test: {'PASSED' if web_search_success else 'FAILED'}")
    
    # Test 2: MCP integration
    mcp_success = await test_mcp_integration()
    print(f"📊 MCP Integration Test: {'PASSED' if mcp_success else 'FAILED'}")
    
    # Overall result
    overall_success = web_search_success and mcp_success
    print(f"\n🎯 Overall Test Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎉 Web search integration is ready! You can now test with:")
        print("   'find top 10 ai investors email from web and send that list to slakshanand1105@gmail.com'")

if __name__ == "__main__":
    asyncio.run(main())
