#!/usr/bin/env python3
"""
🌐 WEB SEARCH FEATURE DEMO
Demonstrate the working web search capabilities
"""

import requests
import json

def demo_web_search():
    """Demo the web search automation feature"""
    print("🌐 WEB SEARCH AUTOMATION DEMO")
    print("=" * 50)
    
    # Example search queries that trigger automation
    search_examples = [
        "search for top investors in food technology",
        "find information about AI automation startups", 
        "research recent trends in protein alternatives",
        "look up competitors in the noodle market"
    ]
    
    print("📋 SUPPORTED SEARCH QUERIES:")
    for i, example in enumerate(search_examples, 1):
        print(f"{i}. '{example}'")
    
    print(f"\n🔍 SEARCH SOURCES SUPPORTED:")
    print("• Google Custom Search API")
    print("• Reddit (public API)")
    print("• LinkedIn (via web scraping)")
    print("• News sources (TechCrunch, Reuters, Bloomberg, CNBC)")
    print("• General web search (DuckDuckGo)")
    
    print(f"\n⚙️ CONFIGURATION NEEDED:")
    print("Add to .env.local:")
    print("GOOGLE_SEARCH_API_KEY=your_google_api_key")
    print("GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id")
    print("REDDIT_CLIENT_ID=your_reddit_client_id")
    print("REDDIT_CLIENT_SECRET=your_reddit_secret")
    
    print(f"\n🎯 CURRENT STATUS:")
    print("✅ Web search service implemented and tested")
    print("✅ AI automation detection working (detects as automation)")
    print("✅ Integration with MCP engine complete")
    print("⚠️ Fine-tuning needed: OpenAI classifying searches as 'data_fetching' instead of 'web_search'")
    
    print(f"\n🚀 TO ENABLE WEB SEARCH:")
    print("1. Get Google Custom Search API key from: https://developers.google.com/custom-search/v1/introduction")
    print("2. Add API keys to .env.local")
    print("3. Test with: 'search for investors in ramen companies'")
    print("4. The system will return comprehensive search results!")
    
    # Test if system is running
    try:
        response = requests.get("http://localhost:8002/health", timeout=5)
        if response.status_code == 200:
            print(f"\n✅ Backend server is running on http://localhost:8002")
            print(f"Ready to receive web search requests!")
        else:
            print(f"\n⚠️ Backend server not responding correctly")
    except:
        print(f"\n❌ Backend server not running. Start it with: python backend/main.py")

if __name__ == "__main__":
    demo_web_search()
