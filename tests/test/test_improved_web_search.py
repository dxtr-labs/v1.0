#!/usr/bin/env python3
"""
Test the improved web search functionality specifically for AI investors
"""

import sys
import os
import asyncio
import requests
import json

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_web_search_direct():
    """Test web search service directly"""
    print("🔍 Testing Web Search Service Directly")
    print("=" * 50)
    
    try:
        from backend.services.web_search_service import web_search_service
        
        # Test the search query
        search_query = "top 10 AI venture capital investors contact information email"
        print(f"📝 Search Query: {search_query}")
        
        # Execute search
        results = await web_search_service.search_comprehensive(search_query, max_results=10)
        
        print(f"✅ Search completed")
        print(f"📊 Results: {type(results)}")
        
        if results and results.get('results'):
            print(f"🎯 Found {len(results['results'])} results:")
            for i, result in enumerate(results['results'][:5], 1):
                print(f"{i}. {result.get('title', 'N/A')}")
                print(f"   URL: {result.get('url', 'N/A')}")
                print(f"   Description: {result.get('description', 'N/A')[:100]}...")
                print()
            return True
        else:
            print("❌ No results found")
            return False
            
    except Exception as e:
        print(f"❌ Web search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mcp_api():
    """Test the MCP API with improved web search"""
    print("\n🚀 Testing MCP API with Web Search")
    print("=" * 50)
    
    test_request = "find top 10 ai investors email from web and send that list to slakshanand1105@gmail.com"
    print(f"📝 Test Request: {test_request}")
    
    try:
        response = requests.post(
            "http://localhost:8002/api/mcp/chat",
            json={
                "message": test_request,
                "service": "inhouse"
            },
            timeout=60  # Increased timeout for web search
        )
        
        print(f"📤 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Request successful!")
            
            # Check if it's a workflow preview
            if result.get("hasWorkflowPreview"):
                print("🎯 ✅ Web search workflow preview generated!")
                
                workflow = result.get("workflow_preview", {})
                email_preview = workflow.get("email_preview", {})
                
                print(f"📧 Email To: {email_preview.get('to', 'N/A')}")
                print(f"📧 Email Subject: {email_preview.get('subject', 'N/A')}")
                print(f"🔍 Search Results Count: {email_preview.get('search_results_count', 0)}")
                
                # Check email content for actual search results
                content = email_preview.get('preview_content', '')
                if 'http' in content and ('investor' in content.lower() or 'venture' in content.lower()):
                    print("🎉 ✅ Email contains actual search results with links!")
                    print(f"📋 Content Preview: {content[:200]}...")
                    return True
                else:
                    print("⚠️ Email might not contain detailed search results")
                    print(f"📋 Content Preview: {content[:200]}...")
                    return False
            else:
                print("⚠️ No workflow preview found")
                print(f"📋 Response: {result.get('response', 'N/A')}")
                return False
        else:
            print(f"❌ Request failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Testing Improved Web Search for AI Investors")
    print("=" * 60)
    
    # Test 1: Direct web search
    web_search_ok = await test_web_search_direct()
    
    # Test 2: MCP API
    api_ok = test_mcp_api()
    
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS:")
    print(f"   Web Search Service: {'✅ WORKING' if web_search_ok else '❌ FAILED'}")
    print(f"   MCP API Integration: {'✅ WORKING' if api_ok else '❌ FAILED'}")
    
    if web_search_ok and api_ok:
        print("\n🎉 SUCCESS: Improved web search for AI investors is working!")
        print("\n💡 Sam can now test with:")
        print("   'find top 10 ai investors email from web and send that list to slakshanand1105@gmail.com'")
        print("   The email should now contain actual search results with contact information!")
    else:
        print("\n❌ Some issues remain - check the logs above")

if __name__ == "__main__":
    asyncio.run(main())
