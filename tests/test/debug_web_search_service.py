#!/usr/bin/env python3
"""
Simple web search service test
"""

import sys
import os
import asyncio

# Add the backend directory to path
sys.path.append('backend')

try:
    print("1. Testing imports...")
    from services.web_search_service import web_search_service
    print("✅ Web search service imported successfully")
    
    async def test_search():
        print("2. Testing basic search...")
        result = await web_search_service.search_comprehensive("test query", max_results=2)
        print(f"✅ Search completed: {type(result)}")
        print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not dict'}")
        return result
    
    print("3. Running async search...")
    result = asyncio.run(test_search())
    print("✅ All tests passed")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
