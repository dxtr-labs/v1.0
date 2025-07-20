#!/usr/bin/env python3
"""
Test script for the enhanced AI system with web access capabilities
"""

import asyncio
import sys
import os

# Add the backend directory to the path  
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)
os.chdir(backend_path)

try:
    from core.web_access import WebAccessEngine
    from mcp.ai_content_generator import AIContentGenerator
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the correct directory")
    sys.exit(1)

async def test_web_access():
    """Test web access capabilities"""
    print("🔍 Testing Web Access Engine...")
    
    web_engine = WebAccessEngine()
    
    # Test web search
    print("\n1. Testing web search...")
    search_results = await web_engine.search_web("latest AI developments 2024")
    if search_results.get("success"):
        print(f"✅ Search successful: Found {len(search_results.get('results', []))} results")
        for i, result in enumerate(search_results.get('results', [])[:2]):
            print(f"   {i+1}. {result.get('title', 'No title')}")
    else:
        print(f"❌ Search failed: {search_results.get('error')}")
    
    # Test Wikipedia lookup
    print("\n2. Testing Wikipedia lookup...")
    wiki_result = await web_engine.get_wikipedia_summary("Artificial Intelligence")
    if wiki_result.get("success"):
        print(f"✅ Wikipedia lookup successful")
        print(f"   Title: {wiki_result.get('title', 'No title')}")
        summary = wiki_result.get('summary', '')
        print(f"   Summary: {summary[:100]}..." if len(summary) > 100 else f"   Summary: {summary}")
    else:
        print(f"❌ Wikipedia lookup failed: {wiki_result.get('error')}")
    
    # Test HTTP request
    print("\n3. Testing HTTP request...")
    http_result = await web_engine.make_http_request("https://httpbin.org/json")
    if http_result.get("success"):
        print("✅ HTTP request successful")
        print(f"   Status: {http_result.get('status_code')}")
        print(f"   Data available: {bool(http_result.get('data'))}")
    else:
        print(f"❌ HTTP request failed: {http_result.get('error')}")

async def test_ai_content_generation():
    """Test AI content generation with web search"""
    print("\n🤖 Testing AI Content Generation with Web Search...")
    
    ai_generator = AIContentGenerator()
    
    # Test web-enhanced content generation
    print("\n1. Testing web-enhanced AI content...")
    try:
        content_result = await ai_generator.generate_content_with_web_search(
            "Latest technology trends and productivity tips",
            "test@example.com"
        )
        
        if content_result.get("success"):
            print("✅ Web-enhanced AI content generation successful")
            print(f"   Subject: {content_result.get('subject', 'No subject')}")
            content_preview = content_result.get('content', '')[:200]
            print(f"   Content preview: {content_preview}...")
        else:
            print(f"❌ Web-enhanced AI content generation failed: {content_result.get('error')}")
            
    except Exception as e:
        print(f"❌ Exception during AI content generation: {e}")

async def main():
    """Run all tests"""
    print("🚀 Starting Enhanced AI System Tests")
    print("=" * 50)
    
    try:
        await test_web_access()
        await test_ai_content_generation()
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed!")
        print("✨ Your AI system now has internet access and enhanced capabilities!")
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
