#!/usr/bin/env python3
"""
Test script to verify the system works without MCP dependencies
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append('backend')

async def test_chat_api():
    """Test the simplified chat API"""
    try:
        from api.chat import chat_with_mcpai as chat_endpoint, ChatRequest
        
        print("✅ Successfully imported chat API without MCP dependencies")
        
        # Test a simple chat request
        request = ChatRequest(
            user_input="Hello, how are you?",
            agent_config={
                "name": "Test Assistant",
                "role": "helper"
            }
        )
        
        response = await chat_endpoint(request)
        print(f"✅ Chat API response: {response.response[:100]}...")
        print(f"✅ Fallback used: {response.fallback_used}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing chat API: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_email_sender():
    """Test the email sender without FastMCP"""
    try:
        from email_sender import FASTMCP_AVAILABLE
        
        print(f"✅ Email sender imported, FastMCP available: {FASTMCP_AVAILABLE}")
        
        if not FASTMCP_AVAILABLE:
            print("✅ Correctly disabled FastMCP dependencies")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing email sender: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 Testing system without MCP dependencies")
    print("=" * 50)
    
    tests = [
        ("Chat API", test_chat_api),
        ("Email Sender", test_email_sender)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        try:
            result = await test_func()
            results.append((test_name, result))
            print(f"✅ {test_name}: {'PASS' if result else 'FAIL'}")
        except Exception as e:
            print(f"❌ {test_name}: FAIL - {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    print(f"\n🎯 Overall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main())
